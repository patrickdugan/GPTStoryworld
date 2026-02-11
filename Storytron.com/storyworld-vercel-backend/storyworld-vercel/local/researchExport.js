import crypto from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'

const sha256 = (value) => crypto.createHash('sha256').update(value).digest('hex')

const stableOrder = (value) => {
  if (Array.isArray(value)) return value.map((entry) => stableOrder(entry))
  if (!value || typeof value !== 'object') return value
  return Object.keys(value)
    .sort()
    .reduce((acc, key) => {
      acc[key] = stableOrder(value[key])
      return acc
    }, {})
}

const stableJson = (value) => JSON.stringify(stableOrder(value))

const parseJson = (value, fallback) => {
  if (!value) return fallback
  if (typeof value === 'object') return value
  try {
    return JSON.parse(value)
  } catch {
    return fallback
  }
}

const norm = (value, fallback = '') => {
  if (typeof value !== 'string') return fallback
  const trimmed = value.trim()
  return trimmed.length ? trimmed : fallback
}

const merkleRootHex = (hexLeaves) => {
  if (!hexLeaves.length) return sha256('EMPTY')
  let level = hexLeaves.map((hex) => Buffer.from(hex, 'hex'))
  while (level.length > 1) {
    if (level.length % 2 === 1) level.push(level[level.length - 1])
    const next = []
    for (let i = 0; i < level.length; i += 2) {
      next.push(crypto.createHash('sha256').update(Buffer.concat([level[i], level[i + 1]])).digest())
    }
    level = next
  }
  return level[0].toString('hex')
}

const writeJsonl = (filePath, rows) => {
  fs.mkdirSync(path.dirname(filePath), { recursive: true })
  const body = rows.map((row) => JSON.stringify(row)).join('\n')
  fs.writeFileSync(filePath, `${body}${rows.length ? '\n' : ''}`, 'utf-8')
}

const writeJson = (filePath, payload) => {
  fs.mkdirSync(path.dirname(filePath), { recursive: true })
  fs.writeFileSync(filePath, JSON.stringify(payload, null, 2), 'utf-8')
}

const defaultRoots = () => {
  const trmPrimary = 'C:\\projects\\storyworldTRM\\TRMStoryworld'
  const trmFallback = 'C:\\projects\\TRMStoryworld'
  const hrmPrimary = 'C:\\projects\\HRM-re'
  const hrmFallback = 'C:\\projects\\storyworldTRM\\HRM-re'

  const trmRoot = fs.existsSync(trmPrimary) ? trmPrimary : trmFallback
  const hrmRoot = fs.existsSync(hrmPrimary) ? hrmPrimary : hrmFallback
  return { trmRoot, hrmRoot }
}

const ensureRoot = (candidate, fallback) => {
  if (candidate && fs.existsSync(candidate)) return candidate
  fs.mkdirSync(fallback, { recursive: true })
  return fallback
}

const episodeRowsFromSession = (session, events) => {
  const sessionId = session.id
  const worldId = norm(session.storyworld_id, norm(session.storyworld_title, `storyworld_${sessionId}`))
  const mode = 'human'
  const steps = []
  const leaves = []
  const traceRows = []

  events.forEach((event, idx) => {
    const options = parseJson(event.options_json, [])
    const visibleVars = parseJson(event.state_json, {})
    const pick = Number.isInteger(event.choice_index) ? event.choice_index : 0
    const encounterId = norm(event.encounter_id, `encounter_${idx + 1}`)
    const nextEncounter = norm(event.next_encounter, '')
    const label = `PICK ${pick}`
    const stateHash = sha256(stableJson(visibleVars))
    const outputHash = sha256(stableJson({ next: nextEncounter || 'END', label }))
    const receiptLeaf = sha256(`SWMDR|human|${sessionId}|${idx}|${stateHash}|${pick}|${outputHash}`)
    leaves.push(receiptLeaf)

    traceRows.push({
      _session_id: sessionId,
      _turn: idx,
      _world_id: worldId,
      _encounter: encounterId,
      _label: label,
      _pick: pick,
      _next: nextEncounter || 'END',
      _state_hash: stateHash,
      _receipt_leaf: receiptLeaf,
      _event: event,
      _options: Array.isArray(options) ? options : []
    })

    steps.push({
      t: idx,
      obs: {
        node_id: encounterId,
        node_text: norm(event.narrative, ''),
        choices: (Array.isArray(options) ? options : []).map((choice, optionIndex) => {
          if (typeof choice === 'string') return { id: `choice_${optionIndex}`, text: choice }
          return {
            id: norm(choice?.id, `choice_${optionIndex}`),
            text: norm(choice?.text || choice?.label, `Option ${optionIndex}`)
          }
        }),
        visible_vars: visibleVars && typeof visibleVars === 'object' ? visibleVars : {},
        turns_left: Math.max(0, events.length - idx)
      },
      action: norm(event.choice_text, `pick_${pick}`),
      plan: `Human play action at turn ${idx}`,
      outcome: {
        next_node_id: nextEncounter || `session_end_${sessionId}`,
        visible_vars: visibleVars && typeof visibleVars === 'object' ? visibleVars : {},
        done: idx === events.length - 1 || !nextEncounter,
        ending_id: idx === events.length - 1 || !nextEncounter ? 'ending_session_complete' : null
      }
    })
  })

  const traceRoot = merkleRootHex(leaves)
  const outputCommitment = sha256(
    stableJson({
      session_id: sessionId,
      mode,
      trace_root: traceRoot,
      labels: traceRows.map((row) => row._label),
      final_node: traceRows.length ? traceRows[traceRows.length - 1]._next : 'END'
    })
  )

  return {
    sessionId,
    worldId,
    traceRoot,
    outputCommitment,
    finalNode: traceRows.length ? traceRows[traceRows.length - 1]._next : 'END',
    traceRows,
    storyworldEpisode: {
      episode_id: `play_${sessionId}`,
      target_ending_id: 'ending_session_complete',
      max_turns: Math.max(1, steps.length),
      steps,
      meta: {
        source: 'storyworld_ui_play',
        storyworld_id: session.storyworld_id,
        storyworld_title: session.storyworld_title,
        genre: session.genre,
        size_tag: session.size_tag,
        theme_variant: session.theme_variant,
        started_at: session.started_at,
        ended_at: session.ended_at
      }
    }
  }
}

export const exportHarnessDatasets = async (
  db,
  {
    maxSessions = 5000,
    trmRoot: trmRootOverride = '',
    hrmRoot: hrmRootOverride = '',
    backendRoot = process.cwd()
  } = {}
) => {
  const roots = defaultRoots()
  const trmRoot = ensureRoot(
    trmRootOverride || roots.trmRoot,
    path.join(backendRoot, 'out', 'trm_fallback')
  )
  const hrmRoot = ensureRoot(
    hrmRootOverride || roots.hrmRoot,
    path.join(backendRoot, 'out', 'hrm_fallback')
  )

  const sessions = await db.all(
    `
      SELECT *
      FROM play_sessions
      ORDER BY started_at DESC
      LIMIT ?
    `,
    [maxSessions]
  )

  const trmControllerRows = []
  const trmRolloutRows = []
  const trmQblotRows = []
  const hrmStoryworldRows = []
  const hrmConductorRows = []

  for (let episode = 0; episode < sessions.length; episode += 1) {
    const session = sessions[episode]
    const events = await db.all(
      `
        SELECT *
        FROM play_events
        WHERE session_id = ?
        ORDER BY seq ASC, id ASC
      `,
      [session.id]
    )
    if (!events.length) continue

    const bundle = episodeRowsFromSession(session, events)
    hrmStoryworldRows.push(bundle.storyworldEpisode)

    for (const trace of bundle.traceRows) {
      const promptLines = [
        '<SW-PLAY-CTRL>',
        `SESSION ${trace._session_id}`,
        `WORLD ${bundle.worldId}`,
        `GENRE ${norm(session.genre, 'Unknown')}`,
        `ENCOUNTER ${trace._encounter}`,
        `NARRATIVE ${norm(trace._event.narrative, '')}`,
        ...trace._options.map((choice, optionIndex) => {
          if (typeof choice === 'string') return `C${optionIndex} ${choice}`
          return `C${optionIndex} ${norm(choice?.text || choice?.label, `Option ${optionIndex}`)}`
        }),
        '</SW-PLAY-CTRL>'
      ]

      trmControllerRows.push({
        input: promptLines.join('\n'),
        target: `PICK ${trace._pick}`,
        meta: {
          source: 'storyworld_ui_play',
          session_id: trace._session_id,
          event_id: trace._event.id,
          storyworld_id: session.storyworld_id,
          encounter_id: trace._encounter,
          created_at: trace._event.created_at || trace._event.ts,
          genre: session.genre,
          size_tag: session.size_tag,
          theme_variant: session.theme_variant,
          swmd_hash: ''
        }
      })

      const rolloutRow = {
        episode,
        turn: trace._turn,
        mode: 'human',
        encounter_id: trace._encounter,
        label: trace._label,
        state_hash: trace._state_hash,
        receipt_leaf: trace._receipt_leaf,
        next_encounter: trace._next,
        trace_root: bundle.traceRoot,
        output_commitment: bundle.outputCommitment,
        final_node: bundle.finalNode,
        session_id: trace._session_id,
        storyworld_id: session.storyworld_id
      }
      trmRolloutRows.push(rolloutRow)

      trmQblotRows.push({
        id: sha256(
          stableJson({
            session_id: trace._session_id,
            event_id: trace._event.id,
            turn: trace._turn,
            encounter: trace._encounter
          })
        ),
        text: `world=${bundle.worldId} mode=human episode=${episode} turn=${trace._turn} encounter=${trace._encounter} action=${trace._label} next=${trace._next}`,
        meta: {
          world_id: bundle.worldId,
          target: `db://play_sessions/${trace._session_id}`,
          swmd_hash: '',
          summary_path: 'db_export',
          run_modes: 'human-only',
          mode: 'human',
          episode,
          turn: trace._turn,
          encounter_id: trace._encounter,
          label: trace._label,
          next_encounter: trace._next,
          state_hash: trace._state_hash,
          receipt_leaf: trace._receipt_leaf,
          trace_root: bundle.traceRoot,
          output_commitment: bundle.outputCommitment,
          final_node: bundle.finalNode
        }
      })

      hrmConductorRows.push({
        state: `WORLD_ID: ${bundle.worldId}\nSESSION_ID: ${trace._session_id}\nENCOUNTER_ID: ${trace._encounter}\nNARRATIVE: ${norm(trace._event.narrative, '')}\nTURN: ${trace._turn}`,
        tools: ['storyworld-ui', 'player-telemetry', 'branch-simulator'],
        action: `PICK_${trace._pick}`,
        meta: {
          session_id: trace._session_id,
          storyworld_id: session.storyworld_id,
          theme_variant: session.theme_variant
        }
      })
    }
  }

  const trmOutRoot = path.join(trmRoot, 'tools', 'bench', 'out', 'play_data_db')
  const hrmOutRoot = path.join(hrmRoot, 'experiments', 'storyworld_play_data')

  const outputPaths = {
    trm_controller_sft: path.join(trmOutRoot, 'controller_sft_from_play.jsonl'),
    trm_rollout_traces: path.join(trmOutRoot, 'rollout_human_traces.jsonl'),
    trm_qblot_corpus: path.join(trmOutRoot, 'qblot_human_play_corpus.jsonl'),
    trm_manifest: path.join(trmOutRoot, 'manifest.json'),
    hrm_storyworld_dataset: path.join(hrmOutRoot, 'storyworld_secret_episodes.jsonl'),
    hrm_conductor_dataset: path.join(hrmOutRoot, 'conductor_dataset_from_play.jsonl'),
    hrm_manifest: path.join(hrmOutRoot, 'manifest.json')
  }

  writeJsonl(outputPaths.trm_controller_sft, trmControllerRows)
  writeJsonl(outputPaths.trm_rollout_traces, trmRolloutRows)
  writeJsonl(outputPaths.trm_qblot_corpus, trmQblotRows)
  writeJsonl(outputPaths.hrm_storyworld_dataset, hrmStoryworldRows)
  writeJsonl(outputPaths.hrm_conductor_dataset, hrmConductorRows)

  const manifest = {
    generated_at: new Date().toISOString(),
    sources: {
      sessions_total: sessions.length,
      max_sessions: maxSessions
    },
    rows: {
      trm_controller_sft: trmControllerRows.length,
      trm_rollout_traces: trmRolloutRows.length,
      trm_qblot_corpus: trmQblotRows.length,
      hrm_storyworld_dataset: hrmStoryworldRows.length,
      hrm_conductor_dataset: hrmConductorRows.length
    },
    paths: outputPaths
  }

  writeJson(outputPaths.trm_manifest, manifest)
  writeJson(outputPaths.hrm_manifest, manifest)

  return manifest
}
