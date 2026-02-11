param(
  [string]$OutRoot = "D:\storyworld-plays",
  [string]$SweepDir = "C:\projects\sweepweave-ts\sweepweave-ts",
  [string]$PuppetRoot = "C:\projects\PuppetMaster\PuppetMaster",
  [int]$Port = 5173,
  [string[]]$Files = @(
    "C:\projects\GPTStoryworld\storyworlds\diplomacy\forecast_backstab_p.json"
  )
)

$ErrorActionPreference = "Stop"

if ($Files.Count -eq 0) {
  throw "Provide at least one storyworld JSON path in -Files."
}

$scriptPath = Join-Path $PSScriptRoot "capture_storyworld_ui.cjs"
if (-not (Test-Path $scriptPath)) {
  throw "Missing script: $scriptPath"
}

New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null

$argsList = @(
  $scriptPath,
  "--out-root", $OutRoot,
  "--sweep-dir", $SweepDir,
  "--puppet-root", $PuppetRoot,
  "--port", $Port,
  "--files"
) + $Files

& node @argsList
if ($LASTEXITCODE -ne 0) {
  throw "UI spot-check failed with exit code $LASTEXITCODE"
}
