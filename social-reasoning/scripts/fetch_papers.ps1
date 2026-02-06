param(
  [string]$OutDir = "C:\projects\GPTStoryworld\social-reasoning\papers\arxiv"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$papers = @(
  @{ id = "2508.07485"; file = "goodstartlabs_democratizing_diplomacy_2508.07485.pdf"; title = "Democratizing Diplomacy: A Harness for Evaluating Any Large Language Model on Full-Press Diplomacy"; topic = "diplomacy,benchmark" },
  @{ id = "2310.08901"; file = "welfare_diplomacy_2310.08901.pdf"; title = "Welfare Diplomacy: Benchmarking Language Model Cooperation"; topic = "diplomacy,cooperation" },
  @{ id = "2110.02924"; file = "no_press_diplomacy_from_scratch_2110.02924.pdf"; title = "No-Press Diplomacy from Scratch"; topic = "diplomacy,planning" },
  @{ id = "2006.04635"; file = "learning_no_press_diplomacy_2006.04635.pdf"; title = "Learning to Play No-Press Diplomacy with Best Response Policy Iteration"; topic = "diplomacy,rl" },
  @{ id = "2210.05492"; file = "mastering_no_press_diplomacy_2210.05492.pdf"; title = "Mastering the Game of No-Press Diplomacy via Human-Regularized Reinforcement Learning and Planning"; topic = "diplomacy,search" },
  @{ id = "2304.03442"; file = "generative_agents_2304.03442.pdf"; title = "Generative Agents: Interactive Simulacra of Human Behavior"; topic = "simulation,memory" },
  @{ id = "2402.01680"; file = "llm_multi_agent_survey_2402.01680.pdf"; title = "Large Language Model based Multi-Agents: A Survey of Progress and Challenges"; topic = "survey,multi-agent" },
  @{ id = "2308.08155"; file = "autogen_2308.08155.pdf"; title = "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"; topic = "framework,multi-agent" },
  @{ id = "2303.17760"; file = "camel_2303.17760.pdf"; title = "CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society"; topic = "framework,society" },
  @{ id = "2308.10848"; file = "agentverse_2308.10848.pdf"; title = "AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors"; topic = "framework,emergence" }
)

$index = @()
foreach ($p in $papers) {
  $url = "https://arxiv.org/pdf/$($p.id).pdf"
  $out = Join-Path $OutDir $p.file
  $needsDownload = $true
  if (Test-Path $out) {
    $size = (Get-Item $out).Length
    if ($size -gt 10000) {
      $needsDownload = $false
    }
  }

  if ($needsDownload) {
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $out
    Write-Output "downloaded $($p.id) -> $out"
  } else {
    Write-Output "cached $($p.id) -> $out"
  }

  $index += [pscustomobject]@{
    group = "arxiv"
    id = $p.id
    title = $p.title
    topic = $p.topic
    pdf = $out
    source = $url
  }
}

$indexPath = Join-Path (Split-Path $OutDir -Parent) "paper_index.csv"
$localDir = Join-Path (Split-Path $OutDir -Parent) "local"
if (Test-Path $localDir) {
  Get-ChildItem -File $localDir -Filter *.pdf | ForEach-Object {
    $index += [pscustomobject]@{
      group = "local"
      id = ""
      title = $_.BaseName
      topic = "local"
      pdf = $_.FullName
      source = $_.FullName
    }
  }
}

$index | Export-Csv -NoTypeInformation -Path $indexPath -Encoding UTF8
Write-Output "wrote index to $indexPath"
