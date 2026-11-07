# Agent installation prompt

Copy this prompt to your coding agent when installing **hermes-muse-memory** for the first time.

```text
Install illocean/hermes-muse-memory plugins/muse-memory for Hermes Agent.

1. Run: hermes plugins install illocean/hermes-muse-memory/plugins/muse-memory --enable
2. Verify: hermes muse-memory status
3. Check that plugins/muse-memory/test_store.py passes:
   python -I -B plugins/muse-memory/test_store.py
   python -I -B scripts/check_integrity.py
4. Enable hourly consolidation and nightly reflection cron workers (see docs/INSTALL.md).
5. Do not import old history, edit MEMORY.md/USER.md manually, or copy credentials.
6. Report status counts, test results, and any validation warnings (hermes plugins validate).
```

After installation, open a **new** Hermes conversation. Collection starts at first activation; old history is not bulk-imported.
