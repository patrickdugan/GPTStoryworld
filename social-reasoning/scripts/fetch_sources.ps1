param(
  [string]$Root = "C:\projects\GPTStoryworld\social-reasoning\sources"
)

$ErrorActionPreference = "Continue"

$webDir = Join-Path $Root "web"
$pdfDir = Join-Path $Root "pdf"
$localDir = Join-Path $Root "local"

New-Item -ItemType Directory -Force -Path $Root, $webDir, $pdfDir, $localDir | Out-Null

$webSources = @(
  @{ key = "goodstart_research"; url = "https://goodstartlabs.com/research" },
  @{ key = "goodstart_diplomacy_leaderboard"; url = "https://goodstartlabs.com/leaderboards/diplomacy" },
  @{ key = "every_diplomacy_article"; url = "https://every.to/diplomacy" },

  @{ key = "arxiv_abs_2508_07485"; url = "https://arxiv.org/abs/2508.07485" },
  @{ key = "arxiv_abs_2310_08901"; url = "https://arxiv.org/abs/2310.08901" },
  @{ key = "arxiv_abs_2110_02924"; url = "https://arxiv.org/abs/2110.02924" },
  @{ key = "arxiv_abs_2006_04635"; url = "https://arxiv.org/abs/2006.04635" },
  @{ key = "arxiv_abs_2210_05492"; url = "https://arxiv.org/abs/2210.05492" },
  @{ key = "arxiv_abs_2304_03442"; url = "https://arxiv.org/abs/2304.03442" },
  @{ key = "arxiv_abs_2402_01680"; url = "https://arxiv.org/abs/2402.01680" },
  @{ key = "arxiv_abs_2308_08155"; url = "https://arxiv.org/abs/2308.08155" },
  @{ key = "arxiv_abs_2303_17760"; url = "https://arxiv.org/abs/2303.17760" },
  @{ key = "arxiv_abs_2308_10848"; url = "https://arxiv.org/abs/2308.10848" },

  @{ key = "history_frus_1952_54_v11_p2_d1149"; url = "https://history.state.gov/historicaldocuments/frus1952-54v11p2/d1149" },
  @{ key = "history_milestones_seato"; url = "https://history.state.gov/milestones/1953-1960/seato" },
  @{ key = "history_frus_1969_76_v11"; url = "https://history.state.gov/historicaldocuments/frus1969-76v11" },
  @{ key = "history_frus_1969_76_v11_d116"; url = "https://history.state.gov/historicaldocuments/frus1969-76v11/d116" },
  @{ key = "history_frus_1969_76_ve07_pressrelease"; url = "https://history.state.gov/historicaldocuments/frus1969-76ve07/pressrelease" }
)

$manifest = @()

foreach ($src in $webSources) {
  $out = Join-Path $webDir ($src.key + ".html")
  try {
    Invoke-WebRequest -UseBasicParsing -Uri $src.url -OutFile $out
    $size = (Get-Item $out).Length
    $manifest += [pscustomobject]@{
      group = "web"
      key = $src.key
      source = $src.url
      local_path = $out
      status = "ok"
      size_bytes = $size
      note = "html snapshot"
    }
    Write-Output "downloaded $($src.key)"
  }
  catch {
    $msg = $_.Exception.Message
    $manifest += [pscustomobject]@{
      group = "web"
      key = $src.key
      source = $src.url
      local_path = $out
      status = "error"
      size_bytes = 0
      note = $msg
    }
    Write-Warning "failed $($src.key): $msg"
  }
}

$arxivCopies = @(
  @{ id = "2508.07485"; file = "goodstartlabs_democratizing_diplomacy_2508.07485.pdf" },
  @{ id = "2310.08901"; file = "welfare_diplomacy_2310.08901.pdf" },
  @{ id = "2110.02924"; file = "no_press_diplomacy_from_scratch_2110.02924.pdf" },
  @{ id = "2006.04635"; file = "learning_no_press_diplomacy_2006.04635.pdf" },
  @{ id = "2210.05492"; file = "mastering_no_press_diplomacy_2210.05492.pdf" },
  @{ id = "2304.03442"; file = "generative_agents_2304.03442.pdf" },
  @{ id = "2402.01680"; file = "llm_multi_agent_survey_2402.01680.pdf" },
  @{ id = "2308.08155"; file = "autogen_2308.08155.pdf" },
  @{ id = "2303.17760"; file = "camel_2303.17760.pdf" },
  @{ id = "2308.10848"; file = "agentverse_2308.10848.pdf" }
)

foreach ($item in $arxivCopies) {
  $srcPath = "C:\projects\GPTStoryworld\social-reasoning\papers\arxiv\$($item.file)"
  $dstPath = Join-Path $pdfDir $item.file
  if (Test-Path $srcPath) {
    Copy-Item -Force $srcPath $dstPath
    $size = (Get-Item $dstPath).Length
    $manifest += [pscustomobject]@{
      group = "pdf"
      key = "arxiv_pdf_$($item.id -replace '[^0-9]','_')"
      source = "https://arxiv.org/pdf/$($item.id).pdf"
      local_path = $dstPath
      status = "ok"
      size_bytes = $size
      note = "copied from papers/arxiv"
    }
    Write-Output "copied $($item.file)"
  }
  else {
    $manifest += [pscustomobject]@{
      group = "pdf"
      key = "arxiv_pdf_$($item.id -replace '[^0-9]','_')"
      source = "https://arxiv.org/pdf/$($item.id).pdf"
      local_path = $dstPath
      status = "missing"
      size_bytes = 0
      note = "source pdf not found in papers/arxiv"
    }
    Write-Warning "missing source pdf: $srcPath"
  }
}

$localCopies = @(
  @{ src = "C:\projects\AI_Diplomacy\rules.pdf"; dst = "rules_from_ai_diplomacy.pdf"; source = "C:\projects\AI_Diplomacy\rules.pdf" },
  @{ src = "C:\projects\GPTStoryworld\papers\SAE_Storyworlds.pdf"; dst = "SAE_Storyworlds.pdf"; source = "C:\projects\GPTStoryworld\papers\SAE_Storyworlds.pdf" },
  @{ src = "C:\projects\GPTStoryworld\papers\Spectral Triplet For Storyworlds — A Decoder & Evaluation Framework.pdf"; dst = "Spectral_Triplet_For_Storyworlds.pdf"; source = "C:\projects\GPTStoryworld\papers\Spectral Triplet For Storyworlds — A Decoder & Evaluation Framework.pdf" },
  @{ src = "C:\projects\GPTStoryworld\papers\Storyworld Saes & Multi‑agent Secret Ending Eval — Draft V0.pdf"; dst = "Storyworld_Saes_Multi_agent_Secret_Ending_Eval_Draft_V0.pdf"; source = "C:\projects\GPTStoryworld\papers\Storyworld Saes & Multi‑agent Secret Ending Eval — Draft V0.pdf" }
)

foreach ($item in $localCopies) {
  $dstPath = Join-Path $localDir $item.dst
  if (Test-Path $item.src) {
    Copy-Item -Force $item.src $dstPath
    $size = (Get-Item $dstPath).Length
    $manifest += [pscustomobject]@{
      group = "local"
      key = [IO.Path]::GetFileNameWithoutExtension($item.dst)
      source = $item.source
      local_path = $dstPath
      status = "ok"
      size_bytes = $size
      note = "copied local source"
    }
    Write-Output "copied local $($item.dst)"
  }
  else {
    $manifest += [pscustomobject]@{
      group = "local"
      key = [IO.Path]::GetFileNameWithoutExtension($item.dst)
      source = $item.source
      local_path = $dstPath
      status = "missing"
      size_bytes = 0
      note = "local source file missing"
    }
    Write-Warning "missing local source: $($item.src)"
  }
}

$manifestPath = Join-Path $Root "source_manifest.csv"
$manifest | Export-Csv -NoTypeInformation -Path $manifestPath -Encoding UTF8
Write-Output "wrote $manifestPath"
