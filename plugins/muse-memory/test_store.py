"""Run with: python test_store.py. No live Hermes data is read or changed."""

import json
import re
import sqlite3
import tempfile
import sys
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from store import Store


def rejected(call):
    try:
        call()
    except (ValueError, KeyError):
        return
    raise AssertionError("invalid operation was accepted")


def demo():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        # A read-only fixture models the adapter's native transcript ingestion; the store never writes it.
        transcript = root / "state.db"
        with closing(sqlite3.connect(transcript)) as db:
            db.execute("CREATE TABLE messages(id INTEGER PRIMARY KEY,session_id TEXT,role TEXT,content TEXT,timestamp REAL)")
            db.executemany("INSERT INTO messages VALUES(?,?,?,?,?)", [(1, "a", "user", "I prefer quiet mornings.\nMy editor is Vim.", 1700000000), (2, "a", "assistant", "You prefer noisy mornings.", 1700000001), (3, "a", "user", "Now I prefer quiet evenings.", 1700000002), (4, "a", "user", "My language is Python.", 1700000003)])
            db.commit()
        original = transcript.read_bytes()
        with closing(sqlite3.connect(transcript.as_uri() + "?mode=ro", uri=True)) as db:
            db.row_factory = sqlite3.Row
            sources = [{"key": f"{row['session_id']}:{row['id']}", "session_id": row["session_id"], "message_id": row["id"], "role": row["role"], "text": row["content"], "timestamp": row["timestamp"], "day": "2026-10-06"} for row in db.execute("SELECT * FROM messages ORDER BY id")]
        memory = Store(root / "profile-a")
        try:
            assert memory.ingest_sources(sources) == 4
            assert memory.ingest_sources(sources) == 0
            assert len(memory.pending()) == 3
            old = {"content": "Prefers quiet mornings", "kind": "opinion", "confidence": 0.9, "evidence": [{"key": "a:1", "quote": "I prefer quiet mornings."}]}
            rejected(lambda: memory.accept_claims([{**old, "evidence": [{"key": "a:1", "quote": "I prefer noisy mornings."}]}]))
            rejected(lambda: memory.accept_claims([{**old, "evidence": [{"key": "a:2", "quote": "You prefer noisy mornings."}]}]))
            first = memory.accept_claims([old])[0]
            assert first["evidence"][0]["session_id"] == "a" and first["evidence"][0]["message_id"] == 1
            rejected(lambda: memory.accept_claims([{**old, "evidence": [{"key": "a:1", "quote": " I prefer quiet mornings."}]}]))
            assert memory.accept_claims([old])[0]["id"] == first["id"]
            assert first["origin"] == "cron"
            rejected(lambda: memory.accept_claims([{**old, "origin": "model", "content": "Origin injection attempt", "evidence": [{"key": "a:1", "quote": "My editor is Vim."}]}]))
            editor = memory.accept_claims([{**old, "content": "Uses Vim", "kind": "world", "origin": "tool", "evidence": [{"key": "a:1", "quote": "My editor is Vim."}]}])[0]
            assert editor["origin"] == "tool"
            near = memory.similar_claims("Uses Vim", limit=1)
            assert [item["id"] for item in near] == [editor["id"]] and near[0]["score"] == 1.0
            assert "evidence" not in near[0] and near[0]["origin"] == "tool"
            assert memory.similar_claims("Completely unrelated topic about cooking pasta") == []
            assert memory.similar_claims("!!") == []
            rejected(lambda: memory.similar_claims(""))
            language = memory.accept_claims([{**old, "content": "Uses Python", "kind": "experience", "evidence": [{"key": "a:4", "quote": "My language is Python."}]}])[0]
            newer = memory.accept_claims([{**old, "content": "Prefers quiet evenings", "supersedes": first["id"], "evidence": [{"key": "a:3", "quote": "Now I prefer quiet evenings."}]}])[0]
            assert memory.explain(first["id"])["status"] == "superseded"
            assert [item["id"] for item in memory.search("quiet")] == [newer["id"]]
            assert memory.search('quiet" OR 1=1 --')
            assert memory.search("!!") == []
            evidence = memory.explain(editor["id"])["evidence"][0]
            file, start, end = re.fullmatch(r"(.*):L(\d+)-L(\d+)", evidence["citation"]).groups()
            assert evidence["quote"] in "\n".join((memory.root / file).read_text(encoding="utf-8").splitlines()[int(start)-1:int(end)])
            memory.mark_processed(["a:1", "a:3"])
            assert memory.status()["pending"] == 1
            clone = {**sources[0], "key": "clone:99"}
            assert memory.ingest_sources([clone]) == 1
            assert memory.status()["pending"] == 1
            memory.write_dream([{"text": "Keep evenings quiet and use Python.", "claim_ids": [newer["id"], language["id"]]}], "2026-10-06")
            assert memory.status()["dream_signature"] == sorted([editor["id"], language["id"], newer["id"]])
            assert "Keep evenings quiet" in (memory.root / "ALIGNMENT_SYNTHESIS.md").read_text(encoding="utf-8")
            (memory.root / "ALIGNMENT_SYNTHESIS.md").write_text("INJECTED FILE INSTRUCTIONS", encoding="utf-8")
            assert "INJECTED FILE INSTRUCTIONS" not in memory.synthesis()
            assert len(memory.synthesis()) <= 1000
            memory.regenerate()
            assert (memory.root / "ALIGNMENT_SYNTHESIS.md").read_text(encoding="utf-8") == memory.synthesis()
            render = memory._render
            attempts = [0]
            def disk_failure():
                render()
                attempts[0] += 1
                if attempts[0] == 1:
                    raise OSError("simulated failure after file replacement")
            memory._render = disk_failure
            try:
                try:
                    memory.accept_claims([{**old, "content": "Uncommitted Python claim", "evidence": [{"key": "a:4", "quote": "My language is Python."}]}])
                except OSError:
                    pass
                else:
                    raise AssertionError("simulated disk failure was swallowed")
                assert memory.search("Uncommitted") == []
                assert all("Uncommitted Python claim" not in path.read_text(encoding="utf-8") for path in memory.root.rglob("*.md"))
            finally:
                memory._render = render
            rejected(lambda: memory.write_dream([{"text": "invalid", "claim_ids": [first["id"]]}]))
            rejected(lambda: memory.forget("../../state.db"))
            rejected(lambda: memory.explain("' OR 1=1 --"))
            forgotten = memory.forget(first["id"])
            assert forgotten["claims_removed"] == 3 and forgotten["sources_removed"] == 3
            assert memory.search("quiet") == [] and memory.search("Vim") == []
            assert memory.search("Python")[0]["id"] == language["id"]
            assert memory.ingest_sources([sources[0], {**sources[0], "key": "other:99"}]) == 0
            rejected(lambda: memory.accept_claims([old]))
            assert memory.ingest_sources([{**sources[0], "key": "altered:99", "text": "Reminder: I prefer quiet mornings."}]) == 1
            rejected(lambda: memory.accept_claims([{**old, "content": "Mornings should be quiet", "evidence": [{"key": "altered:99", "quote": "I prefer quiet mornings."}]}]))
            assert not list((memory.root / "dreams").glob("*.md"))
            assert "Keep evenings quiet" not in (memory.root / "ALIGNMENT_SYNTHESIS.md").read_text(encoding="utf-8")
            assert b"Prefers quiet mornings" not in (memory.root / "memory.sqlite3").read_bytes()
            assert b"Keep evenings quiet" not in (memory.root / "memory.sqlite3").read_bytes()
            tombstones = memory.db.execute("SELECT * FROM tombstones").fetchall()
            assert tombstones and all(re.fullmatch(r"[0-9a-f]{64}", row["hash"]) for row in tombstones)
            assert transcript.read_bytes() == original
            installed_at = memory.status()["installed_at"]
            reopened = Store(memory.root)
            assert reopened.status()["installed_at"] == installed_at
            reopened.close()
            child = "from store import Store; from pathlib import Path; import sys; s=Store(Path(sys.argv[1])); s.ingest_sources([{'key':sys.argv[2],'role':'user','text':'Concurrent source '+sys.argv[2],'day':'2026-10-06'}]); s.close()"
            def concurrent_write(index):
                result = subprocess.run([sys.executable, "-c", child, str(memory.root), f"parallel:{index}"], cwd=Path(__file__).parent, text=True, capture_output=True)
                assert result.returncode == 0, result.stderr
            with ThreadPoolExecutor(max_workers=4) as workers:
                list(workers.map(concurrent_write, range(4)))
            assert memory.status()["sources"] == 7
            journal = (memory.root / "daily" / "2026-10-06.md").read_text(encoding="utf-8")
            assert all(f"Concurrent source parallel:{index}" in journal for index in range(4))
            other = Store(root / "profile-b")
            try:
                assert other.status()["sources"] == 0
                assert other.search("Python") == []
                assert other.ingest_sources([sources[0]]) == 1
            finally:
                other.close()
            print(json.dumps({"passed": "evidence, dedupe, supersession, citations, FTS, forgetting, resurrection prevention, profile isolation, four-process writes, rollback repair, canonical synthesis, raw transcript unchanged"}))
        finally:
            memory.close()


if __name__ == "__main__":
    demo()
