import { nanoid } from 'nanoid'
import { getDb } from './db.js'

const allowedSortFields = new Set(['created_at', 'views', 'likes', 'fork_count', 'encounter_length', 'title'])
const allowedSize = new Set(['snack', 'standard', 'epic'])
const allowedTheme = new Set(['midnight', 'ember', 'verdant', 'ivory'])

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

const rowToStoryworld = (row) => ({
  ...row,
  is_public: Boolean(row.is_public),
  encounter: toJson(row.encounter, {}),
  tags: toJson(row.tags || '[]', [])
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
