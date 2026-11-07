# Installation verification

Verified on 2026-10-06 against the installed Hermes CLI:
`v0.21.5+6553.g2b52acc`, commit `2b52acc2d8ceea37d06945a8bbc7deddaa30de63`, managed Python 3.14.7.
No Hermes update or core-source patch was performed; its Git working tree remained clean.

The global default-profile plugin is enabled in `config.yaml`. The only configuration
changes are its allow-list/empty deny-list and `timezone: Asia/Shanghai`. Parsed before/after
configuration comparison confirmed every existing value was preserved, including provider,
model, authentication references, tools, and native memory limits.

Native MEMORY.md, USER.md, and SOUL.md hashes remained unchanged across runtime validation.
The existing Obsidian memory skill and other skills were preserved; none were imported into
the new corpus. No credentials were copied to the memory archive or test profiles.

## Runtime evidence

| Check | Result |
| --- | --- |
| Global plugin discovery | `muse-memory` enabled, user plugin, version 1.0.0 |
| Real CLI tool calls | One-shot invocation called `muse_memory(status)` and `muse_memory(search)` successfully; native usage record completed with three main API calls |
| Store check | Exact user quotes, claim dedupe, supersession, source-line citations, active-only FTS, shared-source forgetting, hash tombstones, isolated profiles, four concurrent writers, rollback repair, canonical synthesis all passed |
| Native adapter check | Real temporary SessionDB fixtures passed role/platform/summary/secret filtering, 100-message paging, stable UID plus immutable content revisions, idempotent collection, unchanged native fixture bytes, and end-to-end offline extraction/review/dream/retraction |
| Live model pipeline | Temporary archive: one evidence-backed claim accepted, one guidance item accepted; independent reviews passed, empty-work reruns made no model calls, forgetting prevented relearning |
| Observed live routing | Existing OmniRoute configuration resolved to `z-ai/glm-5.3-flash-free`; extraction/review used 1151/915 tokens, dream/review used 1482/914 tokens in the final live check |
| Hourly native job | `95099fc82933`, forced execution and periodic 02:00 execution completed in native cron ledger |
| Nightly native job | `cf0ab436473f`, forced execution completed; next scheduled 03:00 occurrence was not waited for |
| Windows ticker | `Hermes Muse Memory Tick`, hidden PowerShell, every minute; completed ticks returned LastTaskResult 0; active ticks can show 267009 (running) |

Native CLI smoke evidence: `$HERMES_HOME/logs/muse-memory-smoke-usage.json`.
Native job outputs: `$HERMES_HOME/cron/output/<job-id>/`.
Maintenance receipts: `$HERMES_HOME/workspace/self_improvement/objectives/muse-memory/`.

The global corpus starts fresh. Its one collected setup-check message was reviewed and
produced zero durable claims, as intended; pending count returned to zero. Positive claim
and dream tests used temporary archives, which were removed after successful checks.
Future interactive CLI and one-shot conversations supply the real archive.

## Boundaries

SQLite FTS5 replaces Muse's Postgres/vector retrieval. Search is lexical; semantic embeddings
and relationship/goal agents are not installed. The scheduler requires this Windows account
to be signed in and the computer awake. Model inference runs only when there is pending
evidence or changed active claims, using the user's current provider configuration.

Forgetting erases this archive's linked notes, claims, FTS material, and guidance, and blocks
exact original keys/text/quote fingerprints. Native chats, persisted session prompts,
native MEMORY/USER entries, filesystem backups, and every possible paraphrase are outside
that erasure scope. Start a new session to load changed synthesis.

## Reversible disable

```powershell
hermes plugins disable muse-memory
hermes cron pause 95099fc82933
hermes cron pause cf0ab436473f
Disable-ScheduledTask -TaskName 'Hermes Muse Memory Tick'
```

This retains the corpus and implementation. Both workers also check plugin enablement
before running. Configuration backup:
`$HERMES_HOME/backups/muse-memory-20261006-015134/config.yaml`.
Restore it only after checking for later configuration edits. Exact paths and job IDs
are recorded in `installation.json`; architecture and usage are in [README.md](README.md).
