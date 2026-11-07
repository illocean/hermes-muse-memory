$ErrorActionPreference = 'Stop'
$museAgentHome = Split-Path -Parent $PSScriptRoot
$env:HERMES_HOME = $museAgentHome
$museTickLog = Join-Path $museAgentHome 'logs\muse-memory-tick.log'
& (Join-Path $museAgentHome 'bin\hermes.cmd') cron tick *> $museTickLog
exit $LASTEXITCODE
