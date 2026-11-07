# Using the archive

After installation, open a **new** Hermes CLI conversation. Tell Hermes a lasting preference or project convention in your own words. Collection begins at first activation; it does not automatically import old history.

For example:

```text
For my own projects, I prefer runnable checks before a success claim.
```

Not every message becomes a claim. The extraction and review instructions reject transient tasks, setup smoke prompts, unsupported claims, and instructions embedded in evidence. Model decisions can still be wrong: inspect the quote before relying on a claim.

## Inspect and process

```powershell
hermes muse-memory status
hermes muse-memory collect
hermes muse-memory consolidate
hermes muse-memory dream
hermes muse-memory search "runnable checks"
hermes muse-memory explain <claim-uuid>
```

`collect` reads eligible native user messages without inference. `consolidate` and `dream` use the configured Hermes provider when there is work. They skip unchanged inputs. A successful run can accept zero claims; it does not imply every message should become memory.

Search uses active claims and SQLite FTS5 keyword matching. Use distinguishing words rather than assuming embeddings or fuzzy semantic recall. `explain` returns the original exact quote, native session/message identifiers, claim status, and daily-file citation. Generated line numbers may move after a retraction; ask for the current explanation.

## Ask the agent

```text
Search the muse_memory archive for my testing preference and explain each result.
Show the original quote and distinguish my preference from a verified system fact.
```

The agent sees one tool, `muse_memory`, with these actions:

| Action | Purpose |
| --- | --- |
| `status` | Archive counts and metadata |
| `sources` | Pending original source messages |
| `record` | Propose claims using known source keys and exact quotes; semantic review runs before storage |
| `search` | Find active claims using keywords |
| `explain` | Inspect a claim and its evidence |
| `forget` | Remove the explicitly requested claim and dependent archive data |

Native Hermes tool discovery may expose this tool through `tool_search` and `tool_call`. That is normal; use the underlying action's successful result as evidence that it ran.

## Corrections and generated files

State a correction explicitly in a new user message, for example: “Correction: for this project I now prefer X over my previous preference Y.” A new supported claim may supersede the older claim after review. Supersession is not automatic truth discovery; inspect both claims and their evidence.

The canonical database is `memories/muse/memory.sqlite3` under the selected Hermes home. Generated views include:

```text
memories/muse/
  daily/YYYY-MM-DD.md
  bank/world.md
  bank/experience.md
  bank/opinions.md
  bank/reflections.md
  dreams/YYYY-MM-DD.md
  ALIGNMENT_SYNTHESIS.md
```

Check the architecture for the exact current file names. These are generated views. Editing them directly does not alter stored claims or the canonical synthesis injected into a conversation. Use the tool or CLI for archive changes. Use Hermes's native `memory` tool for its separate curated `MEMORY.md` and `USER.md`.

## Forgetting

First inspect the claim you intend to remove:

```powershell
hermes muse-memory explain <claim-uuid>
hermes muse-memory forget <claim-uuid>
hermes muse-memory search "distinctive forgotten words"
```

Or tell the agent: “I explicitly request that you forget archive claim `<claim-uuid>`. Use `muse_memory`, then verify the archive search result.” The tool's instructions require explicit user intent; the storage API itself is not a permission system.

Forgetting removes the archive's source copies and linked claims, supersession chains, dreams, guidance, and search entries. Claims sharing a removed source message are also removed. Tombstones block recollection of the original source keys, source text, exact quotes, and normalized derivatives. SQLite cleanup and Markdown regeneration remove the archive's live copies.

This does **not** erase native `state.db` conversations, native `MEMORY.md`/`USER.md`, persisted prompts, filesystem snapshots, or remote provider records. Tombstones do not recognize every paraphrase of a topic. Request any separate deletion explicitly and use the corresponding Hermes or storage mechanism. Open a new conversation to load revised guidance; a resumed conversation still has its earlier context.

## Scheduling and troubleshooting

The optional setup creates hourly consolidation and nightly reflection at 03:00 in the configured Hermes timezone. On Windows, a hidden task calls native `hermes cron tick` every minute while the selected user is signed in and the computer is awake. Local receipts live under `workspace/self_improvement/objectives/muse-memory/`.

```powershell
hermes plugins list --plain --no-bundled
hermes cron list
hermes cron runs
hermes muse-memory status
```

Inspect the native execution ledger and the scheduled task's last result together. Native cron's service-status warning alone does not prove that an external tick is failing. `0x41301` means a Windows task is running. A delayed job after sleep is not an on-time execution.

If review fails, pending sources remain available for retry. If nothing was accepted, inspect source eligibility, exact-quote support, and model results before assuming storage is broken. Do not publish raw reports or receipts: they can contain source data, route metadata, identifiers, and local paths.

To disable reversibly, run `hermes plugins disable muse-memory`, pause the two jobs recorded in your local installation receipt, and disable this installation's Windows task. Archive files remain available. Restore a configuration backup only after comparing later edits; a blind restore can discard unrelated changes.
