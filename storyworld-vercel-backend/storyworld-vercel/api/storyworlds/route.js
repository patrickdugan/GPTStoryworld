import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export const runtime = 'edge'

const allowedSortFields = new Set(['created_at', 'views', 'likes', 'fork_count', 'encounter_length', 'title'])
const allowedSize = new Set(['snack', 'standard', 'epic'])
const allowedTheme = new Set(['midnight', 'ember', 'verdant', 'ivory'])

const clampInt = (value, min, max, fallback) => {
  const parsed = Number.parseInt(value, 10)
  if (Number.isNaN(parsed)) return fallback
  return Math.max(min, Math.min(max, parsed))
}

const clampFloat = (value, min, max, fallback) => {
  const parsed = Number.parseFloat(value)
  if (Number.isNaN(parsed)) return fallback
  return Math.max(min, Math.min(max, parsed))
}

const normalizeText = (value, fallback = null) => {
  if (typeof value !== 'string') return fallback
  const trimmed = value.trim()
  return trimmed.length ? trimmed : fallback
}

const toEncounter = (value) => {
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

const inferGenre = ({ genre, title, description, customPrompt }) => {
  const provided = normalizeText(genre)
  if (provided) return provided.slice(0, 64)
  const bag = `${title || ''} ${description || ''} ${customPrompt || ''}`.toLowerCase()
  if (bag.includes('horror')) return 'Horror'
  if (bag.includes('mystery')) return 'Mystery'
  if (bag.includes('sci') || bag.includes('space')) return 'Sci-Fi'
  if (bag.includes('fantasy')) return 'Fantasy'
  if (bag.includes('strategy')) return 'Strategy'
  return 'Diplomacy'
}

const inferSize = (sizeTag, encounterLength) => {
  const normalized = normalizeText(sizeTag, '').toLowerCase()
  if (allowedSize.has(normalized)) return normalized
  if (encounterLength <= 420) return 'snack'
  if (encounterLength <= 900) return 'standard'
  return 'epic'
}

const inferTheme = (themeVariant) => {
  const normalized = normalizeText(themeVariant, '').toLowerCase()
  if (allowedTheme.has(normalized)) return normalized
  return 'midnight'
}

// POST /api/storyworlds - Create a new storyworld
export async function POST(request) {
  try {
    const body = await request.json()
    const encounter = toEncounter(body.encounter)

    const title = normalizeText(body.title, `Storyworld ${new Date().toISOString()}`)
    const description = normalizeText(body.description, '')
    const customPrompt = normalizeText(body.custom_prompt, '')
    const systemPrompt = normalizeText(body.system_prompt, '')
    const numCharacters = clampInt(body.num_characters, 1, 10, 3)
    const numThemes = clampInt(body.num_themes, 1, 5, 2)
    const numVariables = clampInt(body.num_variables, 3, 20, 5)
    const encounterLength = clampInt(body.encounter_length, 200, 1500, 500)
    const modelUsed = normalizeText(body.model_used, 'gpt-4.1')
    const temperature = clampFloat(body.temperature, 0, 2, 0.8)
    const isPublic = body.is_public !== false
    const genre = inferGenre({ genre: body.genre, title, description, customPrompt })
    const sizeTag = inferSize(body.size_tag, encounterLength)
    const themeVariant = inferTheme(body.theme_variant)
    const coverImage = normalizeText(body.cover_image, null)
    const bannerImage = normalizeText(body.banner_image, null)
    const tags = Array.isArray(body.tags) ? body.tags.filter((tag) => typeof tag === 'string').slice(0, 20) : []

    if (!encounter || Object.keys(encounter).length === 0) {
      return NextResponse.json({ error: 'Encounter payload is required' }, { status: 400 })
    }

    const insertResult = await sql`
      INSERT INTO storyworlds (
        title,
        description,
        num_characters,
        num_themes,
        num_variables,
        encounter_length,
        custom_prompt,
        encounter,
        system_prompt,
        is_public,
        model_used,
        temperature,
        genre,
        size_tag,
        theme_variant,
        cover_image,
        banner_image,
        tags
      ) VALUES (
        ${title},
        ${description},
        ${numCharacters},
        ${numThemes},
        ${numVariables},
        ${encounterLength},
        ${customPrompt},
        ${JSON.stringify(encounter)},
        ${systemPrompt},
        ${isPublic},
        ${modelUsed},
        ${temperature},
        ${genre},
        ${sizeTag},
        ${themeVariant},
        ${coverImage},
        ${bannerImage},
        ${tags}
      )
      RETURNING
        id,
        title,
        description,
        num_characters,
        num_themes,
        num_variables,
        encounter_length,
        encounter,
        likes,
        views,
        fork_count,
        genre,
        size_tag,
        theme_variant,
        cover_image,
        banner_image,
        tags,
        created_at
    `

    return NextResponse.json({
      success: true,
      storyworld: insertResult.rows[0]
    })
  } catch (error) {
    console.error('Error creating storyworld:', error)
    return NextResponse.json(
      { error: 'Failed to create storyworld', details: error.message },
      { status: 500 }
    )
  }
}

// GET /api/storyworlds - List public storyworlds with optional filters
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)

    const limit = clampInt(searchParams.get('limit'), 1, 100, 24)
    const offset = clampInt(searchParams.get('offset'), 0, 10_000, 0)
    const sort = searchParams.get('sort') || 'created_at'
    const order = searchParams.get('order') === 'asc' ? 'ASC' : 'DESC'
    const sortField = allowedSortFields.has(sort) ? sort : 'created_at'

    const genreFilter = normalizeText(searchParams.get('genre'), 'all')
    const sizeFilter = normalizeText(searchParams.get('size'), 'all')
    const themeFilter = normalizeText(searchParams.get('theme'), 'all')
    const queryText = normalizeText(searchParams.get('q'), '')

    const where = ['is_public = true']
    const values = []

    if (genreFilter !== 'all') {
      values.push(genreFilter.toLowerCase())
      where.push(`LOWER(COALESCE(genre, '')) = $${values.length}`)
    }
    if (sizeFilter !== 'all') {
      values.push(sizeFilter.toLowerCase())
      where.push(`LOWER(COALESCE(size_tag, '')) = $${values.length}`)
    }
    if (themeFilter !== 'all') {
      values.push(themeFilter.toLowerCase())
      where.push(`LOWER(COALESCE(theme_variant, '')) = $${values.length}`)
    }
    if (queryText) {
      values.push(`%${queryText}%`)
      where.push(`(title ILIKE $${values.length} OR description ILIKE $${values.length} OR custom_prompt ILIKE $${values.length})`)
    }

    const listQuery = `
      SELECT
        id,
        title,
        description,
        num_characters,
        num_themes,
        num_variables,
        encounter_length,
        custom_prompt,
        encounter,
        views,
        likes,
        fork_count,
        model_used,
        genre,
        size_tag,
        theme_variant,
        cover_image,
        banner_image,
        tags,
        created_at
      FROM storyworlds
      WHERE ${where.join(' AND ')}
      ORDER BY ${sortField} ${order}
      LIMIT $${values.length + 1}
      OFFSET $${values.length + 2}
    `

    const listResult = await sql.query(listQuery, [...values, limit, offset])

    const countQuery = `
      SELECT COUNT(*)::int AS total
      FROM storyworlds
      WHERE ${where.join(' AND ')}
    `
    const countResult = await sql.query(countQuery, values)

    const [genres, sizes, themes] = await Promise.all([
      sql`
        SELECT
          COALESCE(NULLIF(genre, ''), 'Uncategorized') AS label,
          COUNT(*)::int AS count
        FROM storyworlds
        WHERE is_public = true
        GROUP BY 1
        ORDER BY count DESC, label ASC
      `,
      sql`
        SELECT
          COALESCE(NULLIF(size_tag, ''), 'standard') AS label,
          COUNT(*)::int AS count
        FROM storyworlds
        WHERE is_public = true
        GROUP BY 1
        ORDER BY count DESC, label ASC
      `,
      sql`
        SELECT
          COALESCE(NULLIF(theme_variant, ''), 'midnight') AS label,
          COUNT(*)::int AS count
        FROM storyworlds
        WHERE is_public = true
        GROUP BY 1
        ORDER BY count DESC, label ASC
      `
    ])

    return NextResponse.json({
      storyworlds: listResult.rows,
      total: countResult.rows[0].total,
      limit,
      offset,
      facets: {
        genres: genres.rows,
        sizes: sizes.rows,
        themes: themes.rows
      }
    })
  } catch (error) {
    console.error('Error fetching storyworlds:', error)
    return NextResponse.json(
      { error: 'Failed to fetch storyworlds', details: error.message },
      { status: 500 }
    )
  }
}
