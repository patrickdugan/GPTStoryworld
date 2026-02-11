import { nanoid } from 'nanoid'
import { getDb } from './db.js'
import { exportHarnessDatasets } from './researchExport.js'

const allowedSortFields = new Set(['created_at', 'views', 'likes', 'fork_count', 'encounter_length', 'title'])
const allowedSize = new Set(['snack', 'standard', 'epic'])
const allowedTheme = new Set(['midnight', 'ember', 'verdant', 'ivory'])
const allowedSessionStatus = new Set(['active', 'completed', 'abandoned', 'errored'])
const allowedEventType = new Set(['choice', 'start', 'state', 'end', 'system'])

const clampInt = (value, min, max, fallback) => {
  const parsed = Number.parseInt(value, 10)
  if (Number.isNaN(parsed)) return fallback
  return Math.min(max, Math.max(min, parsed))
}

const clampFloat = (value, min, max, fallback) => {
  const parsed = Number.parseFloat(value)
  if (Number.isNaN(parsed)) return fallback
  return Math.min(max, Math.max(min, parsed))
}

const norm = (value, fallback = '') => {
  if (typeof value !== 'string') return fallback
  const trimmed = value.trim()
  return trimmed.length > 0 ? trimmed : fallback
}

const inferGenre = (body, title, description, prompt) => {
  const explicit = norm(body.genre)
  if (explicit) return explicit
  const bag = `${title} ${description} ${prompt}`.toLowerCase()
  if (bag.includes('horror')) return 'Horror'
  if (bag.includes('mystery')) return 'Mystery'
  if (bag.includes('space') || bag.includes('sci')) return 'Sci-Fi'
  if (bag.includes('strategy')) return 'Strategy'
  if (bag.includes('fantasy')) return 'Fantasy'
  return 'Diplomacy'
}

const inferSize = (sizeTag, encounterLength) => {
  const normalized = norm(sizeTag).toLowerCase()
  if (allowedSize.has(normalized)) return normalized
  if (encounterLength <= 420) return 'snack'
  if (encounterLength <= 900) return 'standard'
  return 'epic'
}

const inferTheme = (themeVariant) => {
  const normalized = norm(themeVariant, 'midnight').toLowerCase()
  return allowedTheme.has(normalized) ? normalized : 'midnight'
}

const toJson = (value, fallback) => {
  try {
    return JSON.parse(value)
  } catch {
    return fallback
  }
}

const toJsonText = (value, fallback) => {
  try {
    return JSON.stringify(value ?? fallback)
  } catch {
    return JSON.stringify(fallback)
  }
}

const rowToStoryworld = (row) => ({
  ...row,
  is_public: Boolean(row.is_public),
  encounter: toJson(row.encounter, {}),
  tags: toJson(row.tags || '[]', [])
})

const rowToPlaySession = (row) => ({
  ...row,
  meta: toJson(row.meta || '{}', {})
})

const rowToPlayEvent = (row) => ({
  ...row,
  options: toJson(row.options_json || '[]', []),
  state: toJson(row.state_json || '{}', {}),
  meta: toJson(row.meta || '{}', {})
})

const parseEncounter = (value) => {
  if (!value) return {}
  if (typeof value === 'string') {
    try {
      return JSON.parse(value)
    } catch {
      return { encounter: value }
    }
  }
  if (typeof value === 'object') return value
  return {}
}

export const registerLocalRoutes = (app) => {
  app.get('/api/health', async (_req, res) => {
    res.json({ ok: true, service: 'storyworld-local-backend' })
  })

  app.post('/api/play/sessions', async (req, res) => {
    try {
      const db = await getDb()
      const body = req.body || {}

      const id = norm(body.id, `sess_${nanoid(20)}`)
      const statusRaw = norm(body.status, 'active').toLowerCase()
      const status = allowedSessionStatus.has(statusRaw) ? statusRaw : 'active'
      const source = norm(body.source, 'storyworld-ui')
      const storyworldId = norm(body.storyworld_id, null)
      const storyworldTitle = norm(body.storyworld_title, null)
      const genre = norm(body.genre, null)
      const sizeTag = norm(body.size_tag, null)
      const themeVariant = norm(body.theme_variant, null)
      const startedAt = norm(body.started_at, null)
      const endedAt = norm(body.ended_at, null)
      const meta = body.meta && typeof body.meta === 'object' ? body.meta : {}

      await db.run(
        `
          INSERT INTO play_sessions (
            id, storyworld_id, storyworld_title, genre, size_tag, theme_variant, source, status, started_at, ended_at, meta, created_at, updated_at
          )
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, datetime('now')), ?, ?, datetime('now'), datetime('now'))
        `,
        [id, storyworldId, storyworldTitle, genre, sizeTag, themeVariant, source, status, startedAt, endedAt, toJsonText(meta, {})]
      )

      const row = await db.get(`SELECT * FROM play_sessions WHERE id = ? LIMIT 1`, [id])
      res.status(201).json({ success: true, session: rowToPlaySession(row) })
    } catch (error) {
      res.status(500).json({ error: 'Failed to create play session', details: error.message })
    }
  })

  app.patch('/api/play/sessions/:id', async (req, res) => {
    try {
      const db = await getDb()
      const { id } = req.params
      const body = req.body || {}

      const updates = []
      const values = []
      const push = (field, value) => {
        updates.push(`${field} = ?`)
        values.push(value)
      }

      if (body.status !== undefined) {
        const statusRaw = norm(body.status, 'active').toLowerCase()
        if (!allowedSessionStatus.has(statusRaw)) {
          return res.status(400).json({ error: 'Invalid play session status' })
        }
        push('status', statusRaw)
        if (!body.ended_at && statusRaw !== 'active') {
          push('ended_at', new Date().toISOString())
        }
      }
      if (body.ended_at !== undefined) push('ended_at', norm(body.ended_at, null))
      if (body.meta !== undefined && body.meta && typeof body.meta === 'object') {
        push('meta', toJsonText(body.meta, {}))
      }
      if (body.source !== undefined) push('source', norm(body.source, 'storyworld-ui'))

      if (updates.length === 0) return res.status(400).json({ error: 'No session fields to update' })

      updates.push(`updated_at = datetime('now')`)
      await db.run(`UPDATE play_sessions SET ${updates.join(', ')} WHERE id = ?`, [...values, id])
      const row = await db.get(`SELECT * FROM play_sessions WHERE id = ? LIMIT 1`, [id])

      if (!row) return res.status(404).json({ error: 'Play session not found' })
      res.json({ success: true, session: rowToPlaySession(row) })
    } catch (error) {
      res.status(500).json({ error: 'Failed to update play session', details: error.message })
    }
  })

  app.get('/api/play/sessions', async (req, res) => {
    try {
      const db = await getDb()
      const limit = clampInt(req.query.limit, 1, 1000, 100)
      const offset = clampInt(req.query.offset, 0, 20_000, 0)
      const storyworldId = norm(req.query.storyworld_id, '')
      const status = norm(req.query.status, '').toLowerCase()

      const where = ['1=1']
      const values = []
      if (storyworldId) {
        where.push(`storyworld_id = ?`)
        values.push(storyworldId)
      }
      if (status) {
        where.push(`status = ?`)
        values.push(status)
      }

      const rows = await db.all(
        `
          SELECT *
          FROM play_sessions
          WHERE ${where.join(' AND ')}
          ORDER BY started_at DESC
          LIMIT ? OFFSET ?
        `,
        [...values, limit, offset]
      )
      const total = await db.get(
        `SELECT COUNT(*) AS total FROM play_sessions WHERE ${where.join(' AND ')}`,
        values
      )

      res.json({
        sessions: rows.map(rowToPlaySession),
        total: total?.total || 0,
        limit,
        offset
      })
    } catch (error) {
      res.status(500).json({ error: 'Failed to list play sessions', details: error.message })
    }
  })

  app.post('/api/play/events', async (req, res) => {
    try {
      const db = await getDb()
      const body = req.body || {}
      const sessionId = norm(body.session_id, '')
      if (!sessionId) return res.status(400).json({ error: 'session_id is required' })

      const session = await db.get(`SELECT id FROM play_sessions WHERE id = ? LIMIT 1`, [sessionId])
      if (!session) return res.status(404).json({ error: 'Play session not found' })

      const currentMax = await db.get(`SELECT COALESCE(MAX(seq), -1) AS max_seq FROM play_events WHERE session_id = ?`, [sessionId])
      const fallbackSeq = Number(currentMax?.max_seq ?? -1) + 1
      const seq = clampInt(body.seq, 0, 2_000_000, fallbackSeq)
      const ts = norm(body.ts, null)
      const eventTypeRaw = norm(body.event_type, 'choice').toLowerCase()
      const eventType = allowedEventType.has(eventTypeRaw) ? eventTypeRaw : 'choice'
      const encounterId = norm(body.encounter_id, null)
      const nextEncounter = norm(body.next_encounter, null)
      const choiceIndex = Number.isInteger(body.choice_index)
        ? body.choice_index
        : Number.isNaN(Number.parseInt(body.choice_index, 10))
          ? null
          : Number.parseInt(body.choice_index, 10)
      const choiceText = norm(body.choice_text, '')
      const narrative = norm(body.narrative, '')
      const options = Array.isArray(body.options) ? body.options.slice(0, 16) : []
      const state = body.state && typeof body.state === 'object' ? body.state : {}
      const latencyMs = body.latency_ms === undefined ? null : clampInt(body.latency_ms, 0, 300_000, 0)
      const meta = body.meta && typeof body.meta === 'object' ? body.meta : {}

      const insertResult = await db.run(
        `
          INSERT INTO play_events (
            session_id, seq, ts, event_type, encounter_id, next_encounter, choice_index, choice_text, narrative,
            options_json, state_json, latency_ms, meta, created_at
          )
          VALUES (?, ?, COALESCE(?, datetime('now')), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        `,
        [
          sessionId,
          seq,
          ts,
          eventType,
          encounterId,
          nextEncounter,
          choiceIndex,
          choiceText,
          narrative,
          toJsonText(options, []),
          toJsonText(state, {}),
          latencyMs,
          toJsonText(meta, {})
        ]
      )

      await db.run(`UPDATE play_sessions SET updated_at = datetime('now') WHERE id = ?`, [sessionId])
      const event = await db.get(`SELECT * FROM play_events WHERE id = ? LIMIT 1`, [insertResult.lastID])
      res.status(201).json({ success: true, event: rowToPlayEvent(event) })
    } catch (error) {
      res.status(500).json({ error: 'Failed to record play event', details: error.message })
    }
  })

  app.get('/api/play/sessions/:id/events', async (req, res) => {
    try {
      const db = await getDb()
      const { id } = req.params
      const limit = clampInt(req.query.limit, 1, 5000, 1000)
      const rows = await db.all(
        `
          SELECT *
          FROM play_events
          WHERE session_id = ?
          ORDER BY seq ASC, id ASC
          LIMIT ?
        `,
        [id, limit]
      )
      res.json({
        session_id: id,
        events: rows.map(rowToPlayEvent),
        total: rows.length
      })
    } catch (error) {
      res.status(500).json({ error: 'Failed to list play events', details: error.message })
    }
  })

  app.post('/api/research/export', async (req, res) => {
    try {
      const db = await getDb()
      const body = req.body || {}
      const manifest = await exportHarnessDatasets(db, {
        maxSessions: clampInt(body.max_sessions, 1, 100_000, 5000),
        trmRoot: norm(body.trm_root, ''),
        hrmRoot: norm(body.hrm_root, ''),
        backendRoot: process.cwd()
      })
      res.json({ success: true, manifest })
    } catch (error) {
      res.status(500).json({ error: 'Failed to export research datasets', details: error.message })
    }
  })

  app.get('/api/research/summary', async (_req, res) => {
    try {
      const db = await getDb()
      const [sessionStats, eventStats] = await Promise.all([
        db.get(`SELECT COUNT(*) AS total_sessions FROM play_sessions`),
        db.get(`SELECT COUNT(*) AS total_events FROM play_events`)
      ])
      res.json({
        sessions: sessionStats?.total_sessions || 0,
        events: eventStats?.total_events || 0
      })
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch research summary', details: error.message })
    }
  })

  app.get('/api/storyworlds', async (req, res) => {
    try {
      const db = await getDb()
      const limit = clampInt(req.query.limit, 1, 100, 24)
      const offset = clampInt(req.query.offset, 0, 20_000, 0)
      const sort = allowedSortFields.has(req.query.sort) ? req.query.sort : 'created_at'
      const order = String(req.query.order).toLowerCase() === 'asc' ? 'ASC' : 'DESC'
      const genre = norm(req.query.genre, 'all')
      const size = norm(req.query.size, 'all')
      const theme = norm(req.query.theme, 'all')
      const q = norm(req.query.q, '')

      const where = ['is_public = 1']
      const values = []

      if (genre !== 'all') {
        values.push(genre.toLowerCase())
        where.push(`LOWER(COALESCE(genre,'')) = ?`)
      }
      if (size !== 'all') {
        values.push(size.toLowerCase())
        where.push(`LOWER(COALESCE(size_tag,'')) = ?`)
      }
      if (theme !== 'all') {
        values.push(theme.toLowerCase())
        where.push(`LOWER(COALESCE(theme_variant,'')) = ?`)
      }
      if (q) {
        values.push(`%${q}%`)
        where.push(`(title LIKE ? OR description LIKE ? OR custom_prompt LIKE ?)`)
        values.push(`%${q}%`, `%${q}%`)
      }

      const listSql = `
        SELECT
          id, title, description, num_characters, num_themes, num_variables, encounter_length,
          custom_prompt, encounter, system_prompt, is_public, genre, size_tag, theme_variant,
          cover_image, banner_image, tags, views, likes, fork_count, model_used, temperature, created_at, updated_at
        FROM storyworlds
        WHERE ${where.join(' AND ')}
        ORDER BY ${sort} ${order}
        LIMIT ? OFFSET ?
      `
      const rows = await db.all(listSql, [...values, limit, offset])

      const countSql = `SELECT COUNT(*) AS total FROM storyworlds WHERE ${where.join(' AND ')}`
      const count = await db.get(countSql, values)

      const [genres, sizes, themes] = await Promise.all([
        db.all(
          `SELECT COALESCE(NULLIF(genre,''),'Uncategorized') AS label, COUNT(*) AS count
           FROM storyworlds WHERE is_public = 1 GROUP BY 1 ORDER BY count DESC, label ASC`
        ),
        db.all(
          `SELECT COALESCE(NULLIF(size_tag,''),'standard') AS label, COUNT(*) AS count
           FROM storyworlds WHERE is_public = 1 GROUP BY 1 ORDER BY count DESC, label ASC`
        ),
        db.all(
          `SELECT COALESCE(NULLIF(theme_variant,''),'midnight') AS label, COUNT(*) AS count
           FROM storyworlds WHERE is_public = 1 GROUP BY 1 ORDER BY count DESC, label ASC`
        )
      ])

      res.json({
        storyworlds: rows.map(rowToStoryworld),
        total: count?.total || 0,
        limit,
        offset,
        facets: {
          genres,
          sizes,
          themes
        }
      })
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch storyworlds', details: error.message })
    }
  })

  app.post('/api/storyworlds', async (req, res) => {
    try {
      const db = await getDb()
      const body = req.body || {}

      const encounterObject = parseEncounter(body.encounter)
      if (Object.keys(encounterObject).length === 0) {
        return res.status(400).json({ error: 'Encounter payload is required' })
      }

      const title = norm(body.title, `Storyworld ${new Date().toISOString()}`)
      const description = norm(body.description, '')
      const numCharacters = clampInt(body.num_characters, 1, 10, 3)
      const numThemes = clampInt(body.num_themes, 1, 5, 2)
      const numVariables = clampInt(body.num_variables, 3, 20, 5)
      const encounterLength = clampInt(body.encounter_length, 200, 1500, 500)
      const customPrompt = norm(body.custom_prompt, '')
      const systemPrompt = norm(body.system_prompt, '')
      const isPublic = body.is_public === false ? 0 : 1
      const modelUsed = norm(body.model_used, 'gpt-4.1')
      const temperature = clampFloat(body.temperature, 0, 2, 0.8)
      const genre = inferGenre(body, title, description, customPrompt)
      const sizeTag = inferSize(body.size_tag, encounterLength)
      const themeVariant = inferTheme(body.theme_variant)
      const coverImage = norm(body.cover_image, null)
      const bannerImage = norm(body.banner_image, null)
      const tags = Array.isArray(body.tags) ? body.tags.filter((tag) => typeof tag === 'string').slice(0, 20) : []
      const id = body.id || nanoid(16)

      await db.run(
        `
          INSERT INTO storyworlds (
            id, title, description, num_characters, num_themes, num_variables, encounter_length,
            custom_prompt, encounter, system_prompt, is_public, genre, size_tag, theme_variant,
            cover_image, banner_image, tags, model_used, temperature, created_at, updated_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        `,
        [
          id,
          title,
          description,
          numCharacters,
          numThemes,
          numVariables,
          encounterLength,
          customPrompt,
          JSON.stringify(encounterObject),
          systemPrompt,
          isPublic,
          genre,
          sizeTag,
          themeVariant,
          coverImage,
          bannerImage,
          JSON.stringify(tags),
          modelUsed,
          temperature
        ]
      )

      const row = await db.get(`SELECT * FROM storyworlds WHERE id = ?`, [id])
      res.status(201).json({ success: true, storyworld: rowToStoryworld(row) })
    } catch (error) {
      res.status(500).json({ error: 'Failed to create storyworld', details: error.message })
    }
  })

  app.get('/api/storyworlds/:id', async (req, res) => {
    try {
      const db = await getDb()
      const { id } = req.params

      const row = await db.get(`SELECT * FROM storyworlds WHERE id = ? LIMIT 1`, [id])
      if (!row) return res.status(404).json({ error: 'Storyworld not found' })

      await db.run(`UPDATE storyworlds SET views = views + 1, updated_at = datetime('now') WHERE id = ?`, [id])
      const updated = await db.get(`SELECT * FROM storyworlds WHERE id = ? LIMIT 1`, [id])

      res.json({ storyworld: rowToStoryworld(updated) })
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch storyworld', details: error.message })
    }
  })

  app.patch('/api/storyworlds/:id', async (req, res) => {
    try {
      const db = await getDb()
      const { id } = req.params
      const body = req.body || {}

      const updates = []
      const values = []

      const pushField = (field, value) => {
        updates.push(`${field} = ?`)
        values.push(value)
      }

      if (body.title !== undefined) pushField('title', norm(body.title, 'Untitled Storyworld'))
      if (body.description !== undefined) pushField('description', norm(body.description, ''))
      if (body.is_public !== undefined) pushField('is_public', body.is_public ? 1 : 0)
      if (body.genre !== undefined) pushField('genre', norm(body.genre, 'Diplomacy'))
      if (body.size_tag !== undefined) pushField('size_tag', inferSize(body.size_tag, 500))
      if (body.theme_variant !== undefined) pushField('theme_variant', inferTheme(body.theme_variant))
      if (body.cover_image !== undefined) pushField('cover_image', norm(body.cover_image, null))
      if (body.banner_image !== undefined) pushField('banner_image', norm(body.banner_image, null))
      if (body.tags !== undefined && Array.isArray(body.tags)) {
        pushField('tags', JSON.stringify(body.tags.filter((tag) => typeof tag === 'string').slice(0, 20)))
      }
      if (body.encounter !== undefined) {
        pushField('encounter', JSON.stringify(parseEncounter(body.encounter)))
      }

      if (updates.length === 0) {
        return res.status(400).json({ error: 'No fields to update' })
      }

      updates.push(`updated_at = datetime('now')`)
      await db.run(`UPDATE storyworlds SET ${updates.join(', ')} WHERE id = ?`, [...values, id])
      const row = await db.get(`SELECT * FROM storyworlds WHERE id = ? LIMIT 1`, [id])

      if (!row) return res.status(404).json({ error: 'Storyworld not found' })
      res.json({ success: true, storyworld: rowToStoryworld(row) })
    } catch (error) {
      res.status(500).json({ error: 'Failed to update storyworld', details: error.message })
    }
  })

  app.delete('/api/storyworlds/:id', async (req, res) => {
    try {
      const db = await getDb()
      const { id } = req.params

      const row = await db.get(`SELECT id FROM storyworlds WHERE id = ? LIMIT 1`, [id])
      if (!row) return res.status(404).json({ error: 'Storyworld not found' })

      await db.run(`DELETE FROM storyworlds WHERE id = ?`, [id])
      res.json({ success: true, message: 'Storyworld deleted' })
    } catch (error) {
      res.status(500).json({ error: 'Failed to delete storyworld', details: error.message })
    }
  })

  app.post('/api/storyworlds/:id/like', async (req, res) => {
    try {
      const db = await getDb()
      const { id } = req.params
      const action = norm(req.query.action, '')

      if (action === 'like') {
        await db.run(`UPDATE storyworlds SET likes = likes + 1, updated_at = datetime('now') WHERE id = ?`, [id])
      } else if (action === 'unlike') {
        await db.run(
          `UPDATE storyworlds SET likes = CASE WHEN likes > 0 THEN likes - 1 ELSE 0 END, updated_at = datetime('now') WHERE id = ?`,
          [id]
        )
      } else {
        return res.status(400).json({ error: 'Invalid action. Use ?action=like or ?action=unlike' })
      }

      const row = await db.get(`SELECT id, likes FROM storyworlds WHERE id = ? LIMIT 1`, [id])
      if (!row) return res.status(404).json({ error: 'Storyworld not found' })

      res.json({ success: true, id: row.id, likes: row.likes })
    } catch (error) {
      res.status(500).json({ error: 'Failed to toggle like', details: error.message })
    }
  })

  app.get('/api/stats', async (_req, res) => {
    try {
      const db = await getDb()
      const totals = await db.get(
        `SELECT
          COUNT(*) AS total_storyworlds,
          COALESCE(SUM(views), 0) AS total_views,
          COALESCE(SUM(likes), 0) AS total_likes,
          COALESCE(SUM(fork_count), 0) AS total_forks
         FROM storyworlds
         WHERE is_public = 1`
      )
      const trending = await db.all(
        `SELECT * FROM storyworlds WHERE is_public = 1 ORDER BY likes DESC, views DESC LIMIT 10`
      )
      const recent = await db.all(
        `SELECT * FROM storyworlds WHERE is_public = 1 ORDER BY created_at DESC LIMIT 10`
      )
      const popular = await db.all(
        `SELECT * FROM storyworlds WHERE is_public = 1 ORDER BY views DESC LIMIT 10`
      )

      res.json({
        stats: totals,
        trending: trending.map(rowToStoryworld),
        recent: recent.map(rowToStoryworld),
        popular: popular.map(rowToStoryworld)
      })
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch stats', details: error.message })
    }
  })
}
