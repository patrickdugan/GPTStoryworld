param(
    [string]$KeyFile,
    [switch]$SkipInstall,
    [switch]$SkipProfile,
    [string]$Distro = "Ubuntu"
)

$ErrorActionPreference = "Stop"

function Find-KeyFile {
    param([string]$UserSupplied)

    if ($UserSupplied) {
        if (-not (Test-Path -LiteralPath $UserSupplied)) {
            throw "Provided key file does not exist: $UserSupplied"
        }
        return (Resolve-Path -LiteralPath $UserSupplied).Path
    }

    $desktop = [Environment]::GetFolderPath("Desktop")
    $candidates = @(
        (Join-Path $desktop "Hermes\OPENAI_API_KEY.txt"),
        (Join-Path $desktop "Hermes\api_key.txt"),
        (Join-Path $desktop "Hermes.txt"),
        (Join-Path $desktop "GPTAPI.txt")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    return $null
}

function Read-ApiKey {
    param([string]$Path)

    $line = Get-Content -LiteralPath $Path -ErrorAction Stop |
        Where-Object { $_ -and $_.Trim().Length -gt 0 } |
        Select-Object -First 1

    if (-not $line) {
        throw "Key file is empty: $Path"
    }

    $key = $line.Trim()
    if ($key -notmatch "^(sk|sk-proj)-") {
        Write-Warning "Key in $Path does not match expected OpenAI prefix; continuing anyway."
    }

    return $key
}

Write-Host "[1/5] Checking WSL..."
$wslStatus = & wsl --status 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "WSL is not available. Install WSL2 first: wsl --install"
}

$distros = & wsl -l -q
if ($LASTEXITCODE -ne 0 -or -not $distros) {
    throw "No WSL distro found. Install Ubuntu first: wsl --install -d Ubuntu"
}

if (-not ($distros -contains $Distro)) {
    Write-Warning "Requested distro '$Distro' not found. Using default WSL distro."
    $Distro = ""
}

Write-Host "[2/5] Resolving API key file..."
$resolvedKeyFile = Find-KeyFile -UserSupplied $KeyFile
if (-not $resolvedKeyFile) {
    throw "No API key file found. Tried Desktop\\Hermes\\OPENAI_API_KEY.txt, Desktop\\Hermes.txt, Desktop\\GPTAPI.txt"
}

$apiKey = Read-ApiKey -Path $resolvedKeyFile
Write-Host "Using key file: $resolvedKeyFile"

if (-not $SkipInstall) {
    Write-Host "[3/5] Installing hermes-agent in WSL..."
    $installScriptWin = (Resolve-Path -LiteralPath ".\tools\hermes\install_hermes_headless.sh").Path
    $installScriptWinUnix = $installScriptWin -replace "\\", "/"
    $installScriptWsl = (& wsl wslpath -a $installScriptWinUnix | Select-Object -First 1).Trim()
    if (-not $installScriptWsl) {
        throw "Failed to translate install script path into WSL format: $installScriptWin"
    }
    $installCmd = "bash $installScriptWsl"
    if ($Distro) {
        & wsl -d $Distro -- bash -lc $installCmd
    } else {
        & wsl -- bash -lc $installCmd
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Hermes install failed in WSL."
    }
} else {
    Write-Host "[3/5] Skipping hermes-agent install (--SkipInstall)."
}

Write-Host "[4/5] Writing key into WSL secure location..."
$profileCmd = @"
set -euo pipefail
mkdir -p ~/.config/hermes
cat > ~/.config/hermes/openai_api_key <<'EOF'
$apiKey
EOF
chmod 600 ~/.config/hermes/openai_api_key
"@

if ($Distro) {
    & wsl -d $Distro -- bash -lc $profileCmd
} else {
    & wsl -- bash -lc $profileCmd
}
if ($LASTEXITCODE -ne 0) {
    throw "Failed to write API key into WSL."
}

if (-not $SkipProfile) {
    Write-Host "[5/5] Updating ~/.profile to auto-export OPENAI_API_KEY..."
    $bashrcCmd = @'
set -euo pipefail
MARK='# >>> GPTStoryworld Hermes key >>>'
if ! grep -Fq "$MARK" ~/.profile 2>/dev/null; then
  {
    echo ""
    echo "$MARK"
    echo 'if [ -f ~/.config/hermes/openai_api_key ]; then'
    echo '  export OPENAI_API_KEY="$(cat ~/.config/hermes/openai_api_key)"'
    echo 'fi'
  } >> ~/.profile
fi
'@

    if ($Distro) {
        & wsl -d $Distro -- bash -lc $bashrcCmd
    } else {
        & wsl -- bash -lc $bashrcCmd
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to update ~/.bashrc in WSL."
    }
} else {
    Write-Host "[5/5] Skipping ~/.bashrc update (--SkipProfile)."
}

Write-Host "Done. Open a new WSL shell and verify with: echo `$OPENAI_API_KEY | sed 's/./*/g'"
