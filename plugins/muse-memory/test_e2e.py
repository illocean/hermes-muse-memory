"""Live CLI -> Windows tick -> model review -> fresh recall -> forget check.

Run with the bundled managed Python, -I -B, and --live. Credentials are
passed only in child environments; synthetic conversations use a temporary home.
"""

import argparse
import gc
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HOME = Path(__file__).resolve().parents[2]
REPO = HOME / "hermes-agent"
sys.path.insert(0, str(REPO))
import hermes_bootstrap
import hermes_yaml as yaml
from agent.redact import redact_sensitive_text
from cron.executions import list_executions
from cron.jobs import list_jobs, remove_job
from cron.scheduler import CronSchedulerRegistrationError, create_job_with_scheduler_registration
from hermes_cli._launchers import runtime_command
from hermes_cli.config import get_env_value_prefer_dotenv, load_config_readonly
from hermes_state import SessionDB
from tools.tool_search_validation import normalize_tool_call_entries

spec = importlib.util.spec_from_file_location("muse_e2e_store", Path(__file__).with_name("store.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Store = module.Store


def last_json(output):
    for offset, char in enumerate(output):
        if char == "{":
            try:
                value, end = json.JSONDecoder().raw_decode(output[offset:])
                if not output[offset + end:].strip():
                    return value
            except ValueError:
                pass
    raise AssertionError("Command did not return a final JSON object")


def native_hashes():
    files = [HOME / "memories/MEMORY.md", HOME / "memories/USER.md", HOME / "SOUL.md"]
    return {str(p.relative_to(HOME)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}


def main():
    config = load_config_readonly()
    before = native_hashes()
    original_jobs = {job["id"] for job in list_jobs(include_disabled=True)}
    report = {"started_at": datetime.now(ZoneInfo(config["timezone"])).isoformat(), "checks": [], "cli_usage": []}
    job_id = None
    worker = None
    # Native profiles share the installed dependency runtime. An arbitrary
    # HERMES_HOME would request its own fresh dependency installation.
    (HOME / "profiles").mkdir(exist_ok=True)
    temporary = tempfile.TemporaryDirectory(prefix="muse-e2e-", dir=HOME / "profiles")
    profile = Path(temporary.name).resolve()
    assert profile.is_relative_to((HOME / "profiles").resolve()), "Fixture escaped the profile directory"
    try:
        projected = {key: config["model"][key] for key in ("default", "provider", "base_url", "api_mode", "key_env") if key in config["model"]}
        provider = config.get("providers", {}).get(projected.get("provider"), {})
        public_provider = {key: provider[key] for key in ("name", "base_url", "key_env", "api_key_env", "api_mode", "default_model") if key in provider}
        key_env = public_provider.get("key_env") or public_provider.get("api_key_env") or projected.get("key_env")
        assert key_env and get_env_value_prefer_dotenv(key_env), "Configured route has no environment credential"
        settings = {"_config_version": config["_config_version"], "model": projected, "providers": {projected["provider"]: public_provider},
                    "plugins": {"enabled": ["muse-memory"], "disabled": []}, "timezone": config["timezone"],
                    "agent": {"max_turns": 8}, "auxiliary": {"background_review": {"enabled": False}, "title_generation": {"enabled": False}}}
        (profile / "config.yaml").write_text(yaml.safe_dump(settings), encoding="utf-8")
        shutil.copytree(HOME / "plugins/muse-memory", profile / "plugins/muse-memory", ignore=shutil.ignore_patterns("__pycache__"))
        (profile / "scripts").mkdir()
        for filename in ("muse-memory-hourly.py", "muse-memory-nightly.py"):
            shutil.copy2(HOME / "scripts" / filename, profile / "scripts" / filename)
        env = dict(os.environ, HERMES_HOME=str(profile), **{key_env: get_env_value_prefer_dotenv(key_env)})
        env.pop("HERMES_PROFILE", None)

        def command(args, *, usage=None):
            if usage is not None:
                args = [*args, "--usage-file", str(profile / usage)]
            result = subprocess.run(runtime_command(REPO, args, home=profile), env=env, cwd=profile,
                                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240,
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            assert result.returncode == 0, redact_sensitive_text((result.stdout + result.stderr)[-5000:], force=True)
            if usage is not None:
                used = json.loads((profile / usage).read_text(encoding="utf-8"))
                assert used["completed"] and not used["failed"], "CLI conversation failed"
                report["cli_usage"].append({k: used[k] for k in ("session_id", "api_calls", "total_tokens", "model", "completed")})
                return used["session_id"]
            return last_json(result.stdout)

        def session(session_id):
            with closing(SessionDB(profile / "state.db", read_only=True)) as db:
                return db.get_session(session_id), db.get_messages(session_id, include_compacted=True, limit=100, latest=True)

        def check_tools(session_id, actions):
            _, messages = session(session_id)
            parsed = []
            for message in messages:
                for call in message.get("tool_calls") or []:
                    fn = call.get("function", {})
                    if fn.get("name") not in ("muse_memory", "tool_call"):
                        continue
                    args = json.loads(fn["arguments"]) if isinstance(fn["arguments"], str) else fn["arguments"]
                    if fn["name"] == "muse_memory":
                        parsed.append(args)
                    else:
                        entries, error = normalize_tool_call_entries(args)
                        assert not error, "Native deferred-tool request malformed"
                        parsed.extend(entry["arguments"] for entry in entries if entry["name"] == "muse_memory")
            assert actions <= {call["action"] for call in parsed}, f"Required real tool calls missing: {actions}"
            results = [json.loads(m["content"]) for m in messages if m["role"] == "tool" and m.get("tool_name") == "muse_memory"]
            assert results and all(result["success"] for result in results), "Native memory tool failed"
            return results

        query = "research"
        quote = "I prefer to research first and never assume."
        initial_id = command(["-t", "muse_memory", "-z", quote + " This is a lasting preference for future sessions. For this reply, say OK and do not call any tools."], usage="initial.json")
        initial_prompt, initial_messages = session(initial_id)
        frozen = initial_prompt["system_prompt"]
        assert "## Plugin Context: muse-memory" in frozen, "Actual prompt omitted the plugin context"
        source_message = next(m for m in initial_messages if m["role"] == "user" and quote in m["content"])
        with closing(Store(profile / "memories/muse")) as corpus:
            sources = corpus.pending()
            assert any(s["message_uid"] == source_message["message_uid"] and s["session_id"] == initial_id and quote in s["text"] for s in sources), "Actual on_session_end did not capture the user source"
        report["checks"].append("Actual one-shot CLI and automatic original-source capture")
        print("PASS: actual CLI source captured; awaiting Windows scheduled worker", flush=True)

        # One temporary global cron job proves the installed Windows task dispatches
        # both actual workers. Its fixture writes stay in the temporary profile.
        worker = HOME / "scripts" / ("muse-memory-e2e-" + uuid.uuid4().hex[:8] + ".py")
        worker.write_text(f'''import json, os, subprocess, runpy
from pathlib import Path
from hermes_cli._launchers import runtime_command
from hermes_cli.config import get_env_value_prefer_dotenv
repo = Path({str(REPO)!r})
profile = Path({str(profile)!r})
env = dict(os.environ, HERMES_HOME=str(profile))
env.pop("HERMES_PROFILE", None)
env[{key_env!r}] = get_env_value_prefer_dotenv({key_env!r})
results = {{}}
for name, script in (("consolidation", "muse-memory-hourly.py"), ("dream", "muse-memory-nightly.py")):
    code = "runpy.run_path(" + repr(str(profile / "scripts" / script)) + ", run_name='__main__')"
    child = subprocess.run(runtime_command(repo, code=code, home=profile), env=env, cwd=profile,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if child.returncode:
        raise RuntimeError("Scheduled fixture worker failed: " + name)
    results[name] = json.loads(child.stdout.strip().splitlines()[-1])
(profile / "scheduled-results.json").write_text(json.dumps(results), encoding="utf-8")
print(json.dumps(results), flush=True)
assert results["consolidation"]["success"] and results["consolidation"]["accepted_claims"] >= 1
assert results["dream"]["success"] and results["dream"]["count"] >= 1
print(json.dumps({{"success": True, "isolated_profile": True, "results": results}}))
''', encoding="utf-8")
        due = datetime.now(ZoneInfo(config["timezone"])) + timedelta(seconds=30)
        try:
            job = create_job_with_scheduler_registration(prompt=None, schedule=due.isoformat(), name="Muse memory isolated E2E", script=worker.name, no_agent=True, deliver="local", repeat=1)
        except CronSchedulerRegistrationError as error:
            job_id = error.job["id"]
            raise
        job_id = job["id"]
        print("Scheduled test job " + job_id + " at " + due.isoformat(), flush=True)
        deadline = time.monotonic() + 600
        execution = None
        while time.monotonic() < deadline:
            executions = list_executions(job_id=job_id, limit=1)
            if executions and executions[0]["status"] not in ("claimed", "running"):
                execution = executions[0]
                break
            time.sleep(2)
        if not execution or execution["status"] != "completed":
            failed = {"execution": execution, "workers": json.loads((profile / "scheduled-results.json").read_text(encoding="utf-8")) if (profile / "scheduled-results.json").exists() else None}
            (HOME / "plugins/muse-memory/health-e2e-last-failure.json").write_text(json.dumps(failed, indent=2), encoding="utf-8")
            raise AssertionError("Windows-dispatched execution did not complete; see health-e2e-last-failure.json")
        assert execution["source"] == "builtin" and execution["scheduled_instant"], "Test was not dispatched as a real scheduled occurrence"
        report["scheduled_execution"] = {k: execution[k] for k in ("id", "job_id", "source", "status", "scheduled_instant", "claimed_at", "finished_at")}
        report["workers"] = json.loads((profile / "scheduled-results.json").read_text(encoding="utf-8"))
        remove_job(job_id)
        job_id = None
        worker.unlink()
        worker = None

        with closing(Store(profile / "memories/muse")) as corpus:
            assert corpus.db.execute("PRAGMA quick_check").fetchone()[0] == "ok"
            hits = corpus.search(query)
            assert hits, "Reviewed memory not searchable"
            claim = next(h for h in hits if any(quote in e["quote"] or e["quote"] in quote for e in h["evidence"]))
            claim_id = claim["id"]
            assert all(e["session_id"] == initial_id and e["message_uid"] == source_message["message_uid"] for e in claim["evidence"])
            for evidence in claim["evidence"]:
                relative, lines = evidence["citation"].split(":L")
                start, end = map(int, lines.split("-L"))
                cited = (profile / "memories/muse" / relative).read_text(encoding="utf-8").splitlines()[start-1:end]
                assert evidence["quote"] in "\n".join(cited), "Citation did not resolve to the exact evidence"
            synthesis = corpus.synthesis()
            assert len(synthesis) <= 1000 and query in synthesis.casefold()
            assert corpus.status()["pending"] == 0
        report["checks"].append("Windows Task Scheduler -> native cron -> hourly extraction/review -> nightly reflection/review -> exact citations and synthesis")
        print("PASS: Windows scheduled workers, review, citations and synthesis", flush=True)

        # Resume proves a pinned prompt does not mutate; a fresh conversation must
        # receive new synthesis and use real search/explain calls for the evidence.
        resumed_id = command(["-t", "muse_memory", "--resume", initial_id, "--no-restore-cwd", "-z", "Reply with acknowledged."], usage="resumed.json")
        resumed_session = session(initial_id)[0]
        assert resumed_id == initial_id and resumed_session["system_prompt"] == frozen, "Existing session prompt changed"
        # Hermes can merge newly available tools when resuming. Inspect semantic
        # changes separately from the memory feature's frozen-prompt requirement.
        pins = [json.loads(row["tool_names"]) if row.get("tool_names") else {"version": None, "tools": []}
                for row in (initial_prompt, resumed_session)]
        definitions = [{t["function"]["name"]: t for t in pin["tools"]} for pin in pins]
        names = [list(definition) for definition in definitions]
        report["resumed_session"] = {"system_prompt_unchanged": True,
            "initial_tool_pin_present": bool(initial_prompt.get("tool_names")),
            "resumed_tool_pin_present": bool(resumed_session.get("tool_names")),
            "serialized_tool_pin_equal": initial_prompt["tool_names"] == resumed_session["tool_names"],
            "semantic_tool_pin_equal": pins[0] == pins[1], "versions": [pin["version"] for pin in pins],
            "tool_names_before": names[0], "tool_names_after": names[1],
            "changed_schemas": [name for name in names[0] if name in definitions[1] and definitions[0][name] != definitions[1][name]]}
        print("Resume tool pin: " + json.dumps(report["resumed_session"]), flush=True)
        recall_id = command(["-t", "muse_memory", "-z", f"Use muse_memory search for {query}, then muse_memory explain for its matching claim. Report the preference and original source citation."], usage="recall.json")
        assert synthesis in session(recall_id)[0]["system_prompt"], "Fresh session did not receive canonical synthesis"
        recall_results = check_tools(recall_id, {"search", "explain"})
        assert any(isinstance(r["result"], dict) and r["result"].get("id") == claim_id for r in recall_results)
        report["checks"].append("Resumed prompt stays frozen; fresh CLI injects synthesis and performs successful search/explain")
        print("PASS: frozen resumed prompt and actual fresh-session recall", flush=True)

        forget_id = command(["-t", "muse_memory", "-z", f"I explicitly authorize forgetting archive claim {claim_id}. Call muse_memory with action forget and claim_id {claim_id}, then action search for {query}, and report whether anything remains."], usage="forget.json")
        check_tools(forget_id, {"forget", "search"})
        command(["muse-memory", "collect"])
        with closing(Store(profile / "memories/muse")) as corpus:
            assert not corpus.search(query), "Forgotten claim reconstructed after collection"
            assert not corpus.db.execute("SELECT 1 FROM claims WHERE id=?", (claim_id,)).fetchone()
            assert not corpus.db.execute("SELECT 1 FROM sources WHERE message_uid=?", (source_message["message_uid"],)).fetchone()
            assert query not in corpus.synthesis().casefold()
            assert corpus.db.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert quote in next(m["content"] for m in session(initial_id)[1] if m["id"] == source_message["id"]), "Forget changed native history"
        report["checks"].append("Actual CLI forget removes claim/evidence/guidance, blocks original-source recollection, preserves native chat")

        settings["plugins"]["disabled"] = ["muse-memory"]
        (profile / "config.yaml").write_text(yaml.safe_dump(settings), encoding="utf-8")
        disabled = subprocess.run(runtime_command(REPO, code="runpy.run_path(" + repr(str(profile / "scripts/muse-memory-hourly.py")) + ",run_name='__main__')", home=profile), env=env, cwd=profile, capture_output=True, text=True, timeout=60)
        assert disabled.returncode == 0 and last_json(disabled.stdout)["disabled"] is True
        report["checks"].append("Disabled plugin worker exits before collection/model work")
        assert before == native_hashes(), "Global native memory files changed"
        assert original_jobs == {job["id"] for job in list_jobs(include_disabled=True)}, "Temporary scheduler job not removed"
        report.update({"passed": True, "finished_at": datetime.now(ZoneInfo(config["timezone"])).isoformat(), "global_native_sha256": before, "fixture_removed": True, "transient_job_removed": True})
        report_file = HOME / "plugins/muse-memory/health-e2e.json"
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"passed": True, "checks": len(report["checks"]), "report": str(report_file)}, ensure_ascii=False), flush=True)
    finally:
        if job_id:
            executions = list_executions(job_id=job_id, limit=1)
            if executions and executions[0]["status"] in ("claimed", "running"):
                # Keep the referenced fixture if a worker still owns it.
                temporary._finalizer.detach()
                raise RuntimeError("Test worker is still running; retained fixture and job for inspection: " + job_id)
            remove_job(job_id)
        if worker and worker.exists():
            worker.unlink()
        gc.collect()
        temporary.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Use the configured model and a temporary Windows-dispatched cron job")
    if not parser.parse_args().live:
        parser.error("--live is required for this end-to-end check")
    main()
