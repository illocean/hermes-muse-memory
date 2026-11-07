# Hermes Muse memory health check

Final live run passed on **2026-10-06, 09:38-09:47 Asia/Shanghai**.
Three reproduced memory defects were fixed with failing regressions before implementation.
Both standalone offline checks passed; the full native CLI/Windows scheduler check and
one additional live recording review passed. No new dependencies or Hermes core patches.

Machine-readable evidence: [global audit](health-global.json) and [live E2E](health-e2e.json).
The earlier [installation verification](VERIFICATION.md) remains a historical snapshot.

## Defects fixed

| Reproduced failure | Correction | Regression evidence |
| --- | --- | --- |
| First input in a fresh profile was excluded because its timestamp preceded lazy archive initialization | Initialize the archive during supported plugin registration, before native input staging; preserve existing installation cutoff | Cold registration check failed before the fix, then passed; actual CLI captured its first message without tool calls |
| A claim arriving during model reflection was marked already reviewed | Commit the exact reviewed claim-ID snapshot; reject guidance citing unreviewed IDs | Concurrent-insertion check failed before the fix, then passed and required another reflection |
| Manual recording omitted processed original messages from semantic review | Select only cited USER source keys, independently of processing status, with existing size bounds and commit checks | Registered-handler check failed before the fix, then passed; one real review accepted its processed original with no unrelated pending evidence |

Production changes are confined to [__init__.py](__init__.py) and [store.py](store.py).
Checks are in [test_store.py](test_store.py), [test_integration.py](test_integration.py),
and [test_e2e.py](test_e2e.py). README now includes the repeatable live command.

## Final runtime results

| Check | Result |
| --- | --- |
| Store and native adapter checks | Two runnable offline programs passed, zero failed; includes exact quotes, role/secret filtering, immutable UID revisions, paging, dedupe, supersession, concurrent writes, rollback repair, canonical synthesis and forgetting |
| Actual first CLI turn | One main API call, no tool calls; automatic hook captured the original persisted user message and native IDs; plugin section present in persisted system prompt |
| Actual Windows dispatch | Temporary job `3019f5a2e7c6` completed with `source=builtin` and a non-null scheduled instant; due 09:40:15, claimed 09:41:14, finished 09:42:27 |
| Consolidation and reflection | Actual installed workers accepted one claim and one guidance item; independent extraction/evidence and reflection/evidence reviews all completed |
| Evidence and guidance | Daily file/line citation resolved to the exact original quote; SQLite integrity `ok`; canonical synthesis stayed within 1,000 characters |
| Resume and fresh recall | Resumed system prompt stayed exactly unchanged; fresh CLI contained canonical synthesis and successfully called real search and explain through native Tool Search routing |
| Actual forgetting | Real explicitly authorized CLI action removed the claim, linked source and guidance; active search returned empty; recollection did not recreate the original; native chat remained intact |
| Disable gate | Actual hourly script returned disabled before collection/model work |
| Manual recording review | Processed original accepted by `z-ai/glm-5.3-flash-free` through OmniRoute, 952 tokens; unrelated pending source excluded |
| Preservation and cleanup | Provider/configuration preserved; MEMORY/USER/SOUL hashes unchanged; source Git tree clean; temporary profile, wrapper and job removed |

The live E2E's four CLI conversations completed with 1/1/4/4 main API calls, respectively.
Worker response metadata reported `z-ai/glm-5.3-flash-free` through the configured OmniRoute:
extraction/review used 1,077/1,017 tokens; reflection/review used 1,193/918 tokens.
These are observed results from this run, not guarantees for future routing or inference.

Native `tool_names` was initially absent and became populated on resume. Installed
oneshot code creates the new session row after the initial prompt/pin update; resume
populates a missing pin. This is separate from the verified frozen system prompt.
First-turn tool-pin byte equality is not asserted.

## Nightly timing and operating boundaries

The real 03:00 nightly slot completed at 09:22 after dispatch at 09:21. Windows events
record sleep from **02:45:04 to 09:20:33**, covering that slot; native execution started
about **78 seconds after wake**. The task has `WakeToRun=false` and
`StartWhenAvailable=true`. It operates while this account is signed in and the machine
is awake; catch-up after sleep was verified. No wake or account settings were changed.
Windows documents the [power-state values](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-system_power_state)
and [WakeToRun setting](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-waketorun).
Task Scheduler's Operational log was disabled, so individual task-event history was unavailable;
native execution records, current task metadata and System power events supplied the evidence.

This covers the global default Hermes CLI profile; corpus paths stay profile-local.
Retrieval is lexical SQLite FTS5. Semantic entailment still depends on the configured model's
conservative review; these checks do not prove adversarial resistance or perfect recall.
Forget removes this archive's linked material and blocks exact-source/quote reconstruction.
Native chats, persisted prompts, native curated memory, external backups and all possible
paraphrases remain outside that erase scope. Start a fresh conversation to load changed guidance.

## Repeat and restore

```powershell
$musePython = (hermes --print-runtime-command | ConvertFrom-Json)[0]
& $musePython -I -B "$env:HERMES_HOME/plugins/muse-memory/test_store.py"
& $musePython -I -B "$env:HERMES_HOME/plugins/muse-memory/test_integration.py"
& $musePython -I -B "$env:HERMES_HOME/plugins/muse-memory/test_integration.py" --live-record
& $musePython -I -B "$env:HERMES_HOME/plugins/muse-memory/test_e2e.py" --live
```

Live checks use the configured provider. E2E uses an isolated native profile sharing
the installed runtime, passes credentials only through child environments, and lets
the installed Windows task dispatch a temporary native job. No authentication files
are copied. Cleanup retains a fixture if its worker still owns it.

Pre-fix backups are under `$HERMES_HOME/backups/`:

- `muse-health-20261006-022127`: reflection snapshot fix.
- `muse-health-cold-20261006-023457`: first-input capture fix.
- `muse-health-record-20261006-093745`: processed-original recording fix.

Restore matching implementation files only after checking for later edits. The
existing reversible disable procedure is in [README.md](README.md#check-and-rollback).
Earlier failed test attempts were not counted as passes: an ambiguous retention fixture
and overstrict/nullable native-pin diagnostics were corrected before the successful final run.
