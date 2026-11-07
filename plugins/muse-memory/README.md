# Muse memory for Hermes CLI

Global default-profile installation in `$HERMES_HOME/plugins/muse-memory`.
This adapts the public [Muse diagram](https://mouse.dev/img/blog/muse/memory-diagram.webp)
and [article](https://mouse.dev/blog/muse-runtime-export/); Muse's implementation was not published.
It uses the installed Hermes APIs, without modifying Hermes core.
Hermes primary references: [memory](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md),
[plugin APIs](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/plugins/index.md),
and [cron](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/cron.md).
Their behavior was checked against this machine's installed source and actual CLI, not assumed from current docs.

| Muse component | Hermes adaptation |
| --- | --- |
| Curated memory | Existing `memories/MEMORY.md` and `USER.md`, with their existing limits |
| Daily notes | `memories/muse/daily/YYYY-MM-DD.md`, captured from original CLI user messages |
| Evidence and claims | Local `memories/muse/memory.sqlite3`; exact quote, native session/message IDs, confidence, status, supersession |
| Memory bank | Generated `memories/muse/bank/world.md`, `experience.md`, `opinions.md`, `reflections.md` |
| Search and explanation | `muse_memory` actions `search` and `explain`; SQLite FTS5 with daily file/line citations |
| Hourly consolidation | Native no-agent cron script; extraction followed by independent evidence review |
| Nightly dream | Native no-agent cron at 03:00 Asia/Shanghai; reflection followed by independent evidence review |
| Standing alignment | Bounded `ALIGNMENT_SYNTHESIS.md`, read from canonical committed DB state and frozen in each new session |
| Maintenance receipts | `workspace/self_improvement/objectives/muse-memory/` |
| Forgetting | Cascades through dependent claims, supersession chains, shared source messages, bank pages, dreams, synthesis, and FTS; hashes prevent exact-source/quote relearning |

No Postgres server or embedding model is installed. Hermes's native `session_search`
remains available for raw conversation recall; the new archive uses local keyword search.
People/groups remain ordinary scoped claims. Separate relationship agents and speculative
goal/workflow automation are not added.

Interactive CLI and CLI one-shot sessions are collected; gateway and cron sessions are excluded.
Collection starts at installation; old sessions are not
bulk-imported. Native history remains available. Non-text messages, source text over 12,000
characters, and any message changed by Hermes's forced credential redaction are skipped.
This conservatively excludes credential-bearing messages rather than persisting masked secrets.
Recovery scans at most 200 sessions and 2,000 messages per session; normal after-turn capture
keeps up as the CLI is used.
Source keys combine the native message UID with its content fingerprint so a revised prompt
does not overwrite earlier evidence or halt collection.

Claims require exact contiguous quotes from original **user** messages. A separate model
checks semantic support. Confidence is a model estimate; a user's statement is not runtime
verification of a machine, file, database, or external service. Model reviews reduce errors
but cannot guarantee perfect entailment. Stored instructions are reference data; current
user instructions always take priority, and memories never grant permission for actions.

Consolidation processes up to 40 pending messages / 18,000 source characters and eight claims
per run. Nightly reflection uses at most 60 active claims and four guidance items. Both skip
model calls when there is no new relevant input. Calls use the current configured Hermes
provider/model/auth, with bounded output and timeouts; no provider credentials are copied.
This does use that provider's inference when there is work. Failures retain pending evidence.

The SQLite database is canonical; Markdown files are generated views. Direct edits to the
generated files do not change claims or injected synthesis. Use the tool or CLI to change
archive state. Daily file line numbers can move after a retraction; `explain` recomputes them.
The native curated files continue to use Hermes's own `memory` tool independently.

## Use

```powershell
hermes muse-memory status
hermes muse-memory search "project convention"
hermes muse-memory explain <claim-uuid>
hermes muse-memory collect
hermes muse-memory consolidate
hermes muse-memory dream
hermes muse-memory forget <claim-uuid>
```

The model receives one `muse_memory` tool: `status`, `sources`, `record`, `search`,
`explain`, and `forget`. Recording requires source keys and exact quotes; it also runs
the semantic reviewer. Use forgetting only on an explicit user request.

**Forgetting scope:** this deletes the archive's source copies and linked derivatives.
Removing a whole source message also retracts sibling claims supported by it.
The native `state.db` chats, frozen/persisted system prompts, and native MEMORY/USER files
remain separate. The model should remove matching native entries with the native `memory`
tool when asked to forget them. Delete source sessions using Hermes's session-management
commands only when explicitly requested. Start a new session after memory changes; a resumed
old session can still contain old context. Tombstones block the original keys/text/quotes,
not every possible paraphrase of a forgotten topic. Filesystem backups outside this archive
are also outside its deletion scope.

## Scheduling

Two native cron jobs deliver receipts locally. A hidden Windows scheduled task,
`Hermes Muse Memory Tick`, invokes `hermes cron tick` once a minute. It runs while this
Windows account is signed in and the machine is awake, with missed starts resumed when
available. Hermes's native scheduler owns due dates, locks, and execution records.
No gateway is needed. `hermes cron status` may warn between external task ticks; check
the Windows task's result and `hermes cron runs` for actual executions.

## Check and rollback

```powershell
$musePython = (hermes --print-runtime-command | ConvertFrom-Json)[0]
& $musePython -I "$env:HERMES_HOME/plugins/muse-memory/test_store.py"
& $musePython -I -B "$env:HERMES_HOME/plugins/muse-memory/test_integration.py"
# Optional: add --live to test_integration.py for a temporary-archive check using your configured model.
& $musePython -I -B "$env:HERMES_HOME/plugins/muse-memory/test_integration.py" --live-record
& $musePython -I -B "$env:HERMES_HOME/plugins/muse-memory/test_e2e.py" --live
hermes plugins list --plain --no-bundled
hermes cron list
Get-ScheduledTaskInfo -TaskName 'Hermes Muse Memory Tick'
```

The live end-to-end check uses the actual CLI, a temporary job dispatched by the Windows
task, and your configured model in an isolated native profile that shares the installed
dependencies. Credentials pass only through the child environment; no authentication files
are copied. It cleans up its fixture and job when finished, retaining them if a worker is
still running. The optional integration `--live` check covers the narrower memory pipeline;
`--live-record` checks recording from processed original evidence with one model review.
See [HEALTHCHECK.md](HEALTHCHECK.md) for the current health report and
[VERIFICATION.md](VERIFICATION.md) for the historical installation checks.

To disable it reversibly: disable `muse-memory` with `hermes plugins disable muse-memory`,
pause the two named cron jobs, and disable the Windows task. Archive files are retained.
The pre-install configuration backup and exact job IDs are recorded in `installation.json`.
Rollback of configuration uses that backup only after checking for later config edits.
