param(
    [string]$SpecPath = "",
    [string]$PythonPath = "D:\Research_Engine\.venv-train\Scripts\python.exe",
    [int]$RamLimitMB = 2048,
    [int]$CpuLimitPct = 25,
    [int]$IoLimitMBs = 20,
    [int]$PollSeconds = 5,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Get-DirectoryBytes {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return 0L
    }
    $sum = Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
    return [long]($sum.Sum | ForEach-Object { $_ })
}

function Write-JsonLine {
    param(
        [string]$Path,
        [hashtable]$Payload
    )
    $Payload["ts"] = (Get-Date).ToUniversalTime().ToString("o")
    Add-Content -LiteralPath $Path -Value (($Payload | ConvertTo-Json -Compress) + "`n")
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$repoRoot = (Resolve-Path (Join-Path $skillRoot "..\..")).Path
if ([string]::IsNullOrWhiteSpace($SpecPath)) {
    $SpecPath = Join-Path $skillRoot "references\wiki-card-router-training-spec.safe.json"
}
$SpecPath = (Resolve-Path $SpecPath).Path
$spec = Get-Content -LiteralPath $SpecPath -Raw | ConvertFrom-Json
$runId = [string]$spec.run_id
$runDir = Join-Path $skillRoot ("runs\" + $runId)
$trainerOutDir = Join-Path $runDir "trainer_outputs"
$eventsPath = Join-Path $runDir "hrm_events.jsonl"
$summaryPath = Join-Path $runDir "hrm_summary.json"
$resolvedPlanPath = Join-Path $runDir "hrm_plan.resolved.json"

New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$plan = [ordered]@{
    training_task_id = "wiki-card-router-qwen2b-safe"
    run_id = $runId
    caps = @{
        ram_mb = $RamLimitMB
        cpu_pct = $CpuLimitPct
        io_mb_s = $IoLimitMBs
    }
    checkpoint_interval_steps = 10
    chunk_strategy = @{
        seq_len = $spec.train_hparams.seq_len
        max_steps = $spec.train_hparams.max_steps
        lora_r = $spec.train_hparams.lora_r
        grad_accum = $spec.train_hparams.grad_accum
    }
    paths = @{
        spec = $SpecPath
        repo_root = $repoRoot
        run_dir = $runDir
        trainer_outputs = $trainerOutDir
        events_jsonl = $eventsPath
        summary_json = $summaryPath
    }
}
$plan | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resolvedPlanPath -Encoding UTF8

if ($DryRun) {
    Write-Output $resolvedPlanPath
    exit 0
}

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class JobObject {
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
  public static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string lpName);

  [DllImport("kernel32.dll")]
  public static extern bool AssignProcessToJobObject(IntPtr hJob, IntPtr hProcess);

  [DllImport("kernel32.dll")]
  public static extern bool SetInformationJobObject(IntPtr hJob, int infoType, IntPtr lpJobObjectInfo, uint cbJobObjectInfoLength);

  public const int JobObjectExtendedLimitInformation = 9;
  public const int JobObjectCpuRateControlInformation = 15;
  public const uint JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100;
  public const uint JOB_OBJECT_CPU_RATE_CONTROL_ENABLE = 0x1;
  public const uint JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP = 0x4;

  [StructLayout(LayoutKind.Sequential)]
  public struct IO_COUNTERS { public ulong ReadOperationCount; public ulong WriteOperationCount; public ulong OtherOperationCount; public ulong ReadTransferCount; public ulong WriteTransferCount; public ulong OtherTransferCount; }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_BASIC_LIMIT_INFORMATION { public long PerProcessUserTimeLimit; public long PerJobUserTimeLimit; public uint LimitFlags; public UIntPtr MinimumWorkingSetSize; public UIntPtr MaximumWorkingSetSize; public uint ActiveProcessLimit; public long Affinity; public uint PriorityClass; public uint SchedulingClass; }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION { public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation; public IO_COUNTERS IoInfo; public UIntPtr ProcessMemoryLimit; public UIntPtr JobMemoryLimit; public UIntPtr PeakProcessMemoryUsed; public UIntPtr PeakJobMemoryUsed; }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_CPU_RATE_CONTROL_INFORMATION { public uint ControlFlags; public uint CpuRate; }
}
'@

$job = [JobObject]::CreateJobObject([IntPtr]::Zero, "wiki-card-router-qwen2b-safe")
$memoryLimitBytes = [long]$RamLimitMB * 1MB
$cpuRate = [uint32]([Math]::Max(1, [Math]::Min(10000, $CpuLimitPct * 100)))

$limit = New-Object JobObject+JOBOBJECT_EXTENDED_LIMIT_INFORMATION
$limit.BasicLimitInformation.LimitFlags = [JobObject]::JOB_OBJECT_LIMIT_PROCESS_MEMORY
$limit.ProcessMemoryLimit = [System.UIntPtr]::new([uint64]$memoryLimitBytes)
$size = [System.Runtime.InteropServices.Marshal]::SizeOf($limit)
$ptr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($size)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($limit, $ptr, $false)
[JobObject]::SetInformationJobObject($job, [JobObject]::JobObjectExtendedLimitInformation, $ptr, $size) | Out-Null
[System.Runtime.InteropServices.Marshal]::FreeHGlobal($ptr)

$cpu = New-Object JobObject+JOBOBJECT_CPU_RATE_CONTROL_INFORMATION
$cpu.ControlFlags = [JobObject]::JOB_OBJECT_CPU_RATE_CONTROL_ENABLE -bor [JobObject]::JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP
$cpu.CpuRate = $cpuRate
$size2 = [System.Runtime.InteropServices.Marshal]::SizeOf($cpu)
$ptr2 = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($size2)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($cpu, $ptr2, $false)
[JobObject]::SetInformationJobObject($job, [JobObject]::JobObjectCpuRateControlInformation, $ptr2, $size2) | Out-Null
[System.Runtime.InteropServices.Marshal]::FreeHGlobal($ptr2)

$launcher = Join-Path $scriptDir "run_trm_trainer_hermes.py"
$args = @($launcher, "--config", $SpecPath)
$proc = Start-Process -FilePath $PythonPath -ArgumentList $args -PassThru -NoNewWindow -WorkingDirectory $repoRoot
[JobObject]::AssignProcessToJobObject($job, $proc.Handle) | Out-Null

"" | Set-Content -LiteralPath $eventsPath -Encoding UTF8
Clear-Content -LiteralPath $eventsPath
Write-JsonLine -Path $eventsPath -Payload @{
    event = "start"
    run_id = $runId
    pid = $proc.Id
    caps = @{
        ram_mb = $RamLimitMB
        cpu_pct = $CpuLimitPct
        io_mb_s = $IoLimitMBs
    }
}

$peakRamMB = 0.0
$peakCpuPct = 0.0
$avgRamMB = 0.0
$avgCpuPct = 0.0
$peakIoMBs = 0.0
$samples = 0
$seenCheckpoints = @{}
$lastSample = Get-Date
$lastCpuSec = [double]0.0
$lastBytes = [double](Get-DirectoryBytes -Path $trainerOutDir)
$ioBreaches = 0
$abortReason = ""

while (-not $proc.HasExited) {
    Start-Sleep -Seconds $PollSeconds
    try {
        $proc.Refresh()
    } catch {
        break
    }
    $now = Get-Date
    $elapsedSec = [Math]::Max(1.0, ($now - $lastSample).TotalSeconds)
    $cpuSec = [double]$proc.CPU
    $cpuPct = [Math]::Round((($cpuSec - $lastCpuSec) / ($elapsedSec * [Environment]::ProcessorCount)) * 100.0, 2)
    $lastCpuSec = $cpuSec
    $lastSample = $now

    $ramMB = [Math]::Round(($proc.WorkingSet64 / 1MB), 2)
    $bytesNow = [double](Get-DirectoryBytes -Path $trainerOutDir)
    $ioMBs = [Math]::Round([Math]::Max(0.0, (($bytesNow - $lastBytes) / 1MB) / $elapsedSec), 3)
    $lastBytes = $bytesNow

    $peakRamMB = [Math]::Max($peakRamMB, $ramMB)
    $peakCpuPct = [Math]::Max($peakCpuPct, $cpuPct)
    $peakIoMBs = [Math]::Max($peakIoMBs, $ioMBs)
    $samples += 1
    $avgRamMB = [Math]::Round((($avgRamMB * ($samples - 1)) + $ramMB) / $samples, 2)
    $avgCpuPct = [Math]::Round((($avgCpuPct * ($samples - 1)) + $cpuPct) / $samples, 2)

    if ($ioMBs -gt $IoLimitMBs) {
        $ioBreaches += 1
    } else {
        $ioBreaches = 0
    }
    if ($ioBreaches -ge 3) {
        $abortReason = "io_cap_exceeded"
        Stop-Process -Id $proc.Id -Force
        break
    }

    $checkpoints = @(Get-ChildItem -LiteralPath $trainerOutDir -Directory -Filter "checkpoint-*" -ErrorAction SilentlyContinue)
    foreach ($checkpoint in $checkpoints) {
        if (-not $seenCheckpoints.ContainsKey($checkpoint.Name)) {
            $seenCheckpoints[$checkpoint.Name] = $true
            Write-JsonLine -Path $eventsPath -Payload @{
                event = "checkpoint"
                run_id = $runId
                checkpoint = $checkpoint.Name
                path = $checkpoint.FullName
            }
        }
    }
}

try {
    $proc.WaitForExit()
} catch {
}

$status = "completed"
if ($abortReason) {
    $status = "aborted"
} elseif ($proc.ExitCode -ne 0) {
    $status = "aborted"
    $abortReason = "trainer_nonzero_exit"
}

Write-JsonLine -Path $eventsPath -Payload @{
    event = "exit"
    run_id = $runId
    status = $status
    exit_code = $proc.ExitCode
    abort_reason = $abortReason
    peak_ram_mb = $peakRamMB
    peak_io_mb_s = $peakIoMBs
    peak_cpu_pct = $peakCpuPct
}

$summary = [ordered]@{
    run_id = $runId
    status = $status
    abort_reason = $abortReason
    exit_code = $proc.ExitCode
    peak_ram_mb = $peakRamMB
    avg_ram_mb = $avgRamMB
    peak_io_mb_s = $peakIoMBs
    avg_cpu_pct = $avgCpuPct
    peak_cpu_pct = $peakCpuPct
    steps_completed = @((Get-ChildItem -LiteralPath $trainerOutDir -Directory -Filter "checkpoint-*" -ErrorAction SilentlyContinue)).Count * 10
    checkpoints = @((Get-ChildItem -LiteralPath $trainerOutDir -Directory -Filter "checkpoint-*" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName))
    events_jsonl = $eventsPath
}
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
Write-Output $summaryPath
