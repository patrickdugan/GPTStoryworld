param(
  [string]$LogRoot = "D:\Research_Engine\Hermes-experiment-logs\storyworld-conveyor",
  [int]$LoopCount = 3,
  [int]$TimeoutMinutes = 30,
  [string]$SessionStamp = ""
)

$ErrorActionPreference = "Stop"

$repo = "C:\projects\GPTStoryworld"
$brief = Join-Path $repo "hermes-skills\storyworld-conveyor\sample_data\macbeth_overnight_brief.json"
$baseFactoryConfig = Join-Path $repo "hermes-skills\storyworld-conveyor\sample_data\factory_overnight_macbeth.json"
$runner = "/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/hermes_run_prompt.sh"
$auditScript = Join-Path $repo "hermes-skills\storyworld-conveyor\scripts\audit_macbeth_loop.py"
$trmAdvisorScript = Join-Path $repo "hermes-skills\storyworld-conveyor\scripts\trm_storyworld_rebalance.py"
$baselineRun = Join-Path $repo "hermes-skills\storyworld-conveyor\factory_runs\macbeth_patch_test"
$promptDir = Join-Path $repo "hermes-skills\storyworld-conveyor\runtime_prompts"
New-Item -ItemType Directory -Force -Path $promptDir | Out-Null

$stamp = if ($SessionStamp) { $SessionStamp } else { Get-Date -Format "yyyyMMdd-HHmmss" }
$sessionRoot = Join-Path $LogRoot ("macbeth-overnight-" + $stamp)
New-Item -ItemType Directory -Force -Path $sessionRoot | Out-Null

function To-WslPath([string]$winPath) {
  $path = $winPath -replace '\\', '/'
  if ($path -match '^([A-Za-z]):/(.*)$') {
    $drive = $matches[1].ToLower()
    $rest = $matches[2]
    return "/mnt/$drive/$rest"
  }
  throw "Cannot convert path to WSL format: $winPath"
}

function Write-LoopPrompt([int]$LoopIndex, [string]$PromptPath, [string]$LoopDir, [string]$LoopDirWsl, [string]$PreviousDir, [string]$PreviousDeltaPath, [string]$FactoryConfigWsl, [string]$AdvisorPacketWsl) {
  $previousLine = if ($PreviousDir) { "Previous loop artifacts: $PreviousDir" } else { "This is loop 1; no previous loop artifacts exist." }
  $deltaLine = if ($PreviousDeltaPath) { "Previous delta brief: $PreviousDeltaPath" } else { "No previous delta brief exists; compare against baseline macbeth_patch_test only." }
  $content = @"
Use skill storyworld-building-codex.
Use skill storyworld-conveyor-runner.
If the skill name is not discoverable, read and follow:
- /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/AGENTS.md
- /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/skills/storyworld-conveyor-runner/SKILL.md

Work only on Macbeth and leave artifacts on disk.
Target brief file: /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data/macbeth_overnight_brief.json
Primary world: /mnt/c/projects/GPTStoryworld/storyworlds/by-week/2026-W11/validated_macbeth.json
Overnight factory config: $FactoryConfigWsl
TRM rebalance advisor packet: $AdvisorPacketWsl
Baseline comparison run: /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/macbeth_patch_test

Objective for this loop:
- push Macbeth toward 4 standard endings, 2 secret endings, and 1 super secret witches/SCP inversion ending
- specifically intensify spool structure, character thread continuity, secret options, desirability formulas, richer effects, warped metric distance, Monte Carlo probe quality, and rebalance practicality
- preserve validator-first discipline
- run the storyworld factory and inspect the generated reports
- revise based on the reports and then rerun the most relevant checks

Preferred factory command for this loop:
python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/run_storyworld_factory.py --config $FactoryConfigWsl --run-id macbeth_loop_$LoopIndex --force

Primary artifact root to inspect after the run:
/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/macbeth_loop_$LoopIndex

Required behavior:
- filesystem claims must be backed by real command output
- never say complete without file paths and counts
- run from the WSL-mounted GPTStoryworld workspace
- start by running `pwd && ls -ld /mnt/c/projects/GPTStoryworld /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor`
- read the TRM advisor packet before planning edits; treat it as the default rebalance policy unless current artifacts prove it wrong
- use the factory config and its artifacts rather than freehand claims
- treat env truth and stage manifests as authoritative
- after the first checkpoint, do not reread AGENTS.md or SKILL.md unless you are editing those files directly
- do not read prior full session transcripts unless a concrete file path from the delta brief is missing; use the previous delta brief as the carry-forward memory packet
- do not spend turns summarizing unchanged reports; spend turns on code/config edits or reruns
- this loop is a failure if you do not make at least one concrete file edit under:
  - `/mnt/c/projects/GPTStoryworld/codex-skills/storyworld-building/scripts`
  - `/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data`
  - `/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/skills`
- if the candidate run matches baseline in metrics/distribution, treat that as a no-op and patch code/config rather than narrating
- your final step must run the delta auditor command below and print its paths

Required delta auditor command:
python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/audit_macbeth_loop.py --baseline-run /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/macbeth_patch_test --candidate-run /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/macbeth_loop_$LoopIndex --out-json $LoopDirWsl/delta_report.json --out-txt $LoopDirWsl/delta_brief.txt

Loop id: macbeth_loop_$LoopIndex
Loop output root: $LoopDirWsl
$previousLine
$deltaLine

Minimum command checklist:
1. read the brief and only the minimal runner instructions needed to execute
2. run the overnight factory config or a justified subset
3. inspect manifests, Monte Carlo output, multiple paths output, and quality report
4. make at least one concrete revision attempt aimed at endings/secret structure or desirability/effect structure
5. rerun validator and the relevant factory checks
6. run the delta auditor against `macbeth_patch_test`
7. print the exact artifact paths produced in this loop
8. print which stage failed or remained weak, and what should change in the next loop

Keep the run within this single query window.
"@
  Set-Content -Path $PromptPath -Value $content -NoNewline:$false
}

$briefCopy = Join-Path $sessionRoot "macbeth_overnight_brief.json"
Copy-Item $brief $briefCopy -Force

$previousLoopDir = ""
$previousDeltaPath = ""
for ($i = 1; $i -le $LoopCount; $i++) {
  $loopName = "loop-$i"
  $loopDir = Join-Path $sessionRoot $loopName
  New-Item -ItemType Directory -Force -Path $loopDir | Out-Null
  $promptPath = Join-Path $promptDir ("macbeth_loop_" + $i + ".prompt.txt")
  $loopFactoryConfig = Join-Path $loopDir ("factory_overnight_macbeth_loop_" + $i + ".json")
  $advisorPacket = Join-Path $loopDir "trm_rebalance_advice.json"

  $wslPrompt = To-WslPath $promptPath
  $wslLoopDir = To-WslPath $loopDir
  & python $trmAdvisorScript --base-config $baseFactoryConfig --factory-runs-root (Join-Path $repo "hermes-skills\storyworld-conveyor\factory_runs") --log-root $LogRoot --out-advice $advisorPacket --out-config $loopFactoryConfig | Out-Null
  $wslLoopFactoryConfig = To-WslPath $loopFactoryConfig
  $wslAdvisorPacket = To-WslPath $advisorPacket
  Write-LoopPrompt -LoopIndex $i -PromptPath $promptPath -LoopDir $loopDir -LoopDirWsl $wslLoopDir -PreviousDir $previousLoopDir -PreviousDeltaPath $previousDeltaPath -FactoryConfigWsl $wslLoopFactoryConfig -AdvisorPacketWsl $wslAdvisorPacket
  $stdoutPath = Join-Path $loopDir "launcher_stdout.log"
  $stderrPath = Join-Path $loopDir "launcher_stderr.log"
  $statusPath = Join-Path $loopDir "status.json"
  $bashCommand = "$runner '$wslPrompt' '$wslLoopDir'"
  $job = Start-Job -ScriptBlock {
    param($CommandString, $StdoutPath, $StderrPath)
    & wsl.exe -e bash -lc $CommandString 1> $StdoutPath 2> $StderrPath
    [pscustomobject]@{
      exit_code = $LASTEXITCODE
    }
  } -ArgumentList $bashCommand, $stdoutPath, $stderrPath
  $start = Get-Date

  while ($job.State -eq "Running") {
    $elapsed = (Get-Date) - $start
    $status = [ordered]@{
      loop = $loopName
      job_id = $job.Id
      started_at = $start.ToString("o")
      elapsed_seconds = [int]$elapsed.TotalSeconds
      timed_out = $false
      exited = $false
    }
    $status | ConvertTo-Json | Set-Content $statusPath -NoNewline:$false
    if ($elapsed.TotalMinutes -ge $TimeoutMinutes) {
      Stop-Job -Job $job -ErrorAction SilentlyContinue
      $status.timed_out = $true
      $status.exited = $true
      $status.exit_code = -1
      $status | ConvertTo-Json | Set-Content $statusPath -NoNewline:$false
      break
    }
    Start-Sleep -Seconds 60
    $job = Get-Job -Id $job.Id
  }

  if ($job.State -ne "Running") {
    $result = Receive-Job -Job $job -Keep -ErrorAction SilentlyContinue | Select-Object -Last 1
    $status = [ordered]@{
      loop = $loopName
      job_id = $job.Id
      started_at = $start.ToString("o")
      elapsed_seconds = [int](((Get-Date) - $start).TotalSeconds)
      timed_out = ($job.State -eq "Stopped")
      exited = $true
      exit_code = $(if ($null -ne $result) { $result.exit_code } else { $null })
    }
    $status | ConvertTo-Json | Set-Content $statusPath -NoNewline:$false
  }

  Remove-Job -Job $job -Force -ErrorAction SilentlyContinue

  $candidateRun = Join-Path $repo ("hermes-skills\storyworld-conveyor\factory_runs\macbeth_loop_" + $i)
  $deltaJson = Join-Path $loopDir "delta_report.json"
  $deltaTxt = Join-Path $loopDir "delta_brief.txt"
  if ((Test-Path $baselineRun) -and (Test-Path $candidateRun)) {
    & python $auditScript --baseline-run $baselineRun --candidate-run $candidateRun --out-json $deltaJson --out-txt $deltaTxt | Out-Null
    if (Test-Path $deltaTxt) {
      $previousDeltaPath = $deltaTxt
    }
  }

  $previousLoopDir = $loopDir
}

Write-Output $sessionRoot
