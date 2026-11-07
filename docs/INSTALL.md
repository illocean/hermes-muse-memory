# Installation

Requires **Hermes Agent** CLI (v0.21.5 tested on Windows 10/11; other releases need validation) and a configured Hermes model provider for extraction/review/reflection when there is work.

## 1. Install the plugin

```powershell
hermes plugins install illocean/hermes-muse-memory/plugins/muse-memory --enable
hermes muse-memory status
```

Pin a reviewed commit for reproducibility:

```powershell
hermes plugins install illocean/hermes-muse-memory/plugins/muse-memory --ref <40-character-commit-sha> --enable
```

The plugin lives at `$HERMES_HOME/plugins/muse-memory`. Other Hermes profiles install separately.

## 2. Enable automatic consolidation (Windows)

The plugin ships two no-agent workers:

- `scripts/muse-memory-hourly.py` — hourly consolidation (00 * * * *)
- `scripts/muse-memory-nightly.py` — nightly reflection (03:00 local)

Create/pause them natively:

```powershell
hermes cron list
```

A hidden Windows scheduled task (`Hermes Muse Memory Tick`, every minute) runs `hermes cron tick` while the user is signed in and the machine is awake. On systems using the gateway ticker, native cron ticks via the gateway instead.

To disable reversibly:

```powershell
hermes plugins disable muse-memory
hermes cron pause <hourly_job_id>
hermes cron pause <nightly_job_id>
Disable-ScheduledTask -TaskName 'Hermes Muse Memory Tick'
```

Archive files remain under `$HERMES_HOME/memories/muse`.

## 3. Verify

```powershell
python -I -B plugins/muse-memory/test_store.py
python -I -B scripts/check_integrity.py
hermes plugins list --plain --no-bundled
hermes cron list
```

Live checks use your configured provider. See [USAGE.md](USAGE.md) and [VERIFICATION.md](VERIFICATION.md).
