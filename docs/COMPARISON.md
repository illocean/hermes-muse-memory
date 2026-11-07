# Publication decision: held (superseded 2026-11-07)

**Decision on 2026-10-06: do not publish this draft.** The user authorized publication only if this setup is better than Mnemosyne. The inspected implementation and available test evidence do not substantiate overall superiority. No GitHub repository was created, no commit was pushed, and no Mnemosyne installation or migration was performed.

**Update 2026-11-07: published by explicit user override.** The owner (illocean) instructed publication as [illocean/hermes-muse-memory](https://github.com/illocean/hermes-muse-memory) (public, MIT, code-only). This does **not** claim superiority over Mnemosyne and does not retract the analysis below; it records that the held condition was overridden for the initial public release.

The existing local Muse-style Hermes setup remains in place. Publication work copied reusable files into this separate draft and changed only the exported test bootstrap paths. The draft's portable installer, release manifest, and release documentation are unfinished; proposed installation commands are not a published installation method.

## What was inspected

- Our actual installed plugin, store, workers, existing health artifacts, and the exported standalone checks.
- Mnemosyne cloned from the requested URL, which now redirects to [mnemosyne-oss/mnemosyne](https://github.com/mnemosyne-oss/mnemosyne), at commit `e871f39480b9b9156faa4396162f7ec1f3b11525`.
- Actual Mnemosyne core/provider/install/test source and declared CI, rather than treating README marketing or test-file counts as runtime proof.
- The installed Hermes source at commit `2b52acc2d8ceea37d06945a8bbc7deddaa30de63`, including its native Mnemosyne catalog entry and provider interface.

## Relevant differences

| Area | This Muse-style plugin | Mnemosyne inspected source | Assessment |
| --- | --- | --- | --- |
| Recall | Active-claim SQLite FTS5 keyword search | Vector/FTS/importance recall, additional temporal and veracity controls, with optional embedding dependencies | Mnemosyne has a broader retrieval implementation. We did not measure a quality or latency winner. |
| Accepted user claims | Every claim must reference an existing original USER source and an exact contiguous quote; a separate model checks support | General memory writes with source metadata, optional extraction, veracity, and evidence packs | Our quote requirement is a useful narrower contract. It does not establish overall superiority or imply Mnemosyne lacks provenance. |
| Workflow | Original-user collection, hourly extraction/review, nightly bounded reflection/review, generated Markdown, frozen new-session guidance | Working/episodic memory, consolidation, model refresh, provider prefetch, and broader tools | Different goals. Our focused Muse-style workflow is easier to inspect; Mnemosyne supports more kinds of memory work. |
| Dependencies and inference | No added package dependencies beyond Hermes; processing uses its configured model when work exists | Base package declares PyYAML; vectors, MCP, local inference, and sync are optional extras | Our packaging is smaller. Neither local storage nor a README slogan establishes offline behavior for every configuration. |
| Installation | Current Windows deployment verified; portable scheduler setup unfinished | Packaged Hermes adapter, native catalog wrapper, runtime discovery and Windows installation paths | Mnemosyne has a more developed reusable installation surface. |
| Deletion | Removes linked source copies and derivatives; source/quote/derivative tombstones block exact recollection; SQLite cleanup and regenerated views | Tier-aware ownership/deletion cascades, transaction protections, canonical/sync tombstone mechanisms | These are distinct contracts. We did not establish that either erases all copies or all paraphrases. |
| Verification | Actual CLI, Windows tick, configured model, search/explain/forget, and prompt-freeze behavior observed here | Broad regression and packaging/contract tests inspected; suite not run here | Strong local deployment evidence for ours does not prove superior general quality. |

## Source pointers

Mnemosyne's [BEAM implementation](https://github.com/mnemosyne-oss/mnemosyne/blob/e871f39480b9b9156faa4396162f7ec1f3b11525/mnemosyne/core/beam.py) includes `remember` around line 5835, tier-aware forgetting around lines 7400/7452, consolidation around line 7512, evidence packs around line 8894, and recall around line 8977. Inspect the implementation and configuration together: optional embeddings are not equivalent to guaranteed semantic retrieval in a base-only installation.

The [Hermes adapter](https://github.com/mnemosyne-oss/mnemosyne/tree/e871f39480b9b9156faa4396162f7ec1f3b11525/integrations/hermes), [package dependencies](https://github.com/mnemosyne-oss/mnemosyne/blob/e871f39480b9b9156faa4396162f7ec1f3b11525/pyproject.toml), and [CI configuration](https://github.com/mnemosyne-oss/mnemosyne/blob/e871f39480b9b9156faa4396162f7ec1f3b11525/.github/workflows/ci.yml) support the installation and declared test-scope comparison.

The installed Hermes catalog's canonical install name is `mnemosyne`, using `integrations/hermes-catalog`. Its reviewed pin is `d73848735a2a48471a62d2c8fb96cd7183c97491`, not the latest commit inspected above. We did not install either revision. See the [installed-revision catalog source](https://github.com/NousResearch/hermes-agent/blob/2b52acc2d8ceea37d06945a8bbc7deddaa30de63/plugin-catalog/mnemosyne.yaml).

Our quote invariant is in [store.py](../plugins/muse-memory/store.py), enforced before writing evidence. [The plugin](../plugins/muse-memory/__init__.py) runs the semantic reviewer and exposes canonical prompt guidance. [The architecture draft](ARCHITECTURE.md) documents the actual pipeline and its boundaries.

## Verification performed and limits

During publication preparation, the exported store and offline native integration programs both passed under the existing managed Python 3.14.7 runtime. The exported production plugin, store, manifest, and workers remained byte-identical to the previously live-tested installation. Only the exported test runners gained an explicit `HERMES_REPO` bootstrap option; the installed original files were unchanged.

The earlier local health evidence contains 17 named global checks, two standalone offline programs, five grouped live end-to-end checks, and one additional live manual-record review. All executed checks passed. These are different evidence types, not an interchangeable aggregate score, and they are not a retrieval benchmark.

Mnemosyne's regression sources cover real SQLite thread/process races, rollback and savepoint behavior, ownership-sensitive deletion, provenance/supersession atomicity, and built-wheel provider lifecycle contracts. Its configured CI includes Linux Python 3.10–3.13. We did **not** run its pytest suite: pytest was absent from the four existing interpreters checked. No dependencies or model calls were added for this comparison. Declared CI and inspected tests are not presented as observed passing runs.

There is no matched head-to-head dataset, model/embedding configuration, inference budget, retrieval score, latency measurement, or failure-rate comparison here. Published benchmark results for another revision or judge cannot fill that gap. We also have not validated Mnemosyne end to end on this particular Windows installation.

The evidence supports keeping the current plugin as a working local customization with stricter user-quote admission. It does not support publishing it under a claim that it is better than Mnemosyne. Publication stays held unless a later explicit instruction changes that condition.
