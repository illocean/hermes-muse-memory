# Integrity and publication boundaries

The reusable plugin and worker source was exported through an explicit file allowlist. This repository contains no runtime archive, personal memory, authentication files, configured provider credentials, native databases, logs, job records, installation receipts, or machine backups. Review the tracked files before publishing a fork.

`SHA256SUMS` records the bytes of shipped source, tests, documentation, and configuration. To check a clone:

```powershell
python -I -B scripts/check_integrity.py
```

The check detects missing or altered listed files. It does not authenticate the publisher: someone who can replace both a file and its checksum can produce a matching manifest. Review and pin a trusted Git commit; use normal Git transport verification. This initial publication has no claimed independent security audit or signed-release guarantee.

Hermes's native plugin installer records source and revision outside the plugin tree. Its admission checks remain in force; the install guide does not disable security scanning. Review any reported caution before accepting it. The plugin declares no extra Python dependencies.

The canonical SQLite store enforces source identities, exact contiguous evidence quotes, valid claim identifiers, and reviewed reflection snapshots. A separate model checks semantic support. SQLite transactions, atomic file replacement, rollback repair, deletion cleanup, and regression checks protect consistency; they do not make the reviewer infallible or prove that user statements describe reality.

Generated Markdown files are useful views, not a channel for trusted instructions. The prompt section reads committed SQLite state. The agent instructions treat evidence as data and current user instructions as authoritative. Native tool authorization remains the harness's responsibility.

CI checks the dependency-free store and these checksums. The Windows scheduler and configured-model checks are opt-in native runtime checks described in [VERIFICATION.md](VERIFICATION.md). A green CI run alone does not establish that a local installation is healthy end to end.

Before committing local changes, inspect `git status` and the staged diff. `.gitignore` excludes common local reports and sensitive runtime filenames as a convenience; it is not a secret scanner and cannot undo an already tracked secret.
