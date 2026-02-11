const DEFAULT_COVERS = {
  diplomacy:
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1100&q=80',
  mystery:
    'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1100&q=80',
  scifi:
    'https://images.unsplash.com/photo-1516414447565-b14be0adf13e?auto=format&fit=crop&w=1100&q=80',
  strategy:
    'https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=1100&q=80',
  horror:
    'https://images.unsplash.com/photo-1526778548025-fa2f459cd5ce?auto=format&fit=crop&w=1100&q=80',
  fantasy:
    'https://images.unsplash.com/photo-1517022812141-23620dba5c23?auto=format&fit=crop&w=1100&q=80'
}

export const defaultFacetState = {
  genres: ['Diplomacy', 'Mystery', 'Strategy', 'Sci-Fi'],
  sizes: ['snack', 'standard', 'epic'],
  themes: ['midnight', 'ember', 'verdant', 'ivory']
}

const toSentenceCase = (value, fallback) => {
  if (!value || typeof value !== 'string') return fallback
  const cleaned = value.trim()
  if (!cleaned) return fallback
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1).toLowerCase()
}

const clamp = (value, min, max, fallback) => {
  const parsed = Number.parseInt(value, 10)
  if (Number.isNaN(parsed)) return fallback
  return Math.min(max, Math.max(min, parsed))
}

const parseEncounter = (encounter) => {
  if (!encounter) return {}
  if (typeof encounter === 'string') {
    try {
      return JSON.parse(encounter)
    } catch {
      return { encounter }
    }
  }
  return encounter
}

const normalizeChoices = (choices) => {
  if (!Array.isArray(choices)) return []
  return choices
    .map((choice, index) => {
      if (typeof choice === 'string') return choice
      if (choice && typeof choice === 'object') {
        return choice.label || choice.text || choice.choice || choice.name || `Choice ${index + 1}`
      }
      return null
    })
    .filter(Boolean)
}

const pickNarrative = (encounterJson) => {
  if (!encounterJson || typeof encounterJson !== 'object') {
    return {
      text: 'TODO: Add encounter narrative for this storyworld.',
      choices: ['Advance the plot']
    }
  }

  if (typeof encounterJson.encounter === 'string') {
    return {
      text: encounterJson.encounter,
      choices: normalizeChoices(encounterJson.choices || encounterJson.options).slice(0, 4)
    }
  }

  if (Array.isArray(encounterJson.encounters) && encounterJson.encounters.length > 0) {
    const first = encounterJson.encounters[0] || {}
    const text =
      first.encounter || first.text || first.description || first.narrative || 'TODO: Add encounter narrative.'
    const options = first.choices || first.options || encounterJson.choices || []
    return {
      text,
      choices: normalizeChoices(options).slice(0, 4)
    }
  }

  return {
    text: encounterJson.text || encounterJson.narrative || 'TODO: Add encounter narrative for this storyworld.',
    choices: normalizeChoices(encounterJson.choices || encounterJson.options).slice(0, 4)
  }
}

const estimateEncounterLength = (narrativeText, fallback) => {
  if (!narrativeText || typeof narrativeText !== 'string') return fallback
  const words = narrativeText.trim().split(/\s+/).filter(Boolean)
  return clamp(words.length, 200, 1500, fallback)
}

const deriveGenre = (raw) => {
  if (raw.genre) return toSentenceCase(raw.genre, 'Diplomacy')
  const bag = `${raw.title || ''} ${raw.description || ''} ${raw.custom_prompt || ''}`.toLowerCase()
  if (bag.includes('horror')) return 'Horror'
  if (bag.includes('mystery')) return 'Mystery'
  if (bag.includes('fantasy')) return 'Fantasy'
  if (bag.includes('sci') || bag.includes('space')) return 'Sci-Fi'
  if (bag.includes('strategy')) return 'Strategy'
  return 'Diplomacy'
}

const deriveSize = (rawLength) => {
  const length = clamp(rawLength, 200, 1500, 500)
  if (length <= 420) return 'snack'
  if (length <= 900) return 'standard'
  return 'epic'
}

const pickCover = (genre, id) => {
  const key = genre.toLowerCase().replace(/[^a-z]/g, '')
  if (DEFAULT_COVERS[key]) return DEFAULT_COVERS[key]
  const ordered = Object.values(DEFAULT_COVERS)
  const hash = (id || '').split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return ordered[hash % ordered.length]
}

export const normalizeStoryworld = (raw) => {
  const encounter = parseEncounter(raw.encounter)
  const reader = pickNarrative(encounter)
  const genre = deriveGenre(raw)
  const size = (raw.size_tag || '').toLowerCase() || deriveSize(raw.encounter_length || reader.text.length)
  const theme = (raw.theme_variant || 'midnight').toLowerCase()
  const fallbackDescription = reader.text.slice(0, 140).trim()

  return {
    id: raw.id || `demo-${Math.random().toString(36).slice(2, 8)}`,
    title: raw.title || 'Untitled Storyworld',
    description: raw.description || `${fallbackDescription}${fallbackDescription.length === 140 ? '...' : ''}`,
    genre,
    size,
    theme,
    likes: Number(raw.likes || 0),
    views: Number(raw.views || 0),
    forkCount: Number(raw.fork_count || 0),
    createdAt: raw.created_at || new Date(0).toISOString(),
    numCharacters: clamp(raw.num_characters, 1, 10, 3),
    numThemes: clamp(raw.num_themes, 1, 5, 2),
    numVariables: clamp(raw.num_variables, 3, 20, 5),
    encounterLength: clamp(raw.encounter_length, 200, 1500, estimateEncounterLength(reader.text, 500)),
    coverImage: raw.cover_image || pickCover(genre, raw.id),
    bannerImage: raw.banner_image || raw.cover_image || pickCover(genre, raw.id),
    readerText: reader.text,
    choices: reader.choices.length > 0 ? reader.choices : ['Advance the plot'],
    encounter
  }
}

export const buildRows = (storyworlds) => {
  if (storyworlds.length === 0) return []

  const trending = [...storyworlds]
    .sort((a, b) => b.likes + b.views / 10 - (a.likes + a.views / 10))
    .slice(0, 12)
  const recent = [...storyworlds]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 12)

  const rows = [
    { id: 'row-trending', title: 'Trending Now', items: trending },
    { id: 'row-recent', title: 'New Arrivals', items: recent }
  ]

  const byGenre = new Map()
  for (const storyworld of storyworlds) {
    const list = byGenre.get(storyworld.genre) || []
    list.push(storyworld)
    byGenre.set(storyworld.genre, list)
  }

  Array.from(byGenre.entries())
    .sort((a, b) => b[1].length - a[1].length)
    .slice(0, 4)
    .forEach(([genre, list]) => {
      rows.push({
        id: `row-genre-${genre.toLowerCase().replace(/\s+/g, '-')}`,
        title: `${genre} Worlds`,
        items: list.slice(0, 12)
      })
    })

  return rows.filter((row) => row.items.length > 0)
}

export const facetOptionsFromApi = (facets, items) => {
  if (facets) {
    return {
      genres: facets.genres?.map((entry) => entry.label) || defaultFacetState.genres,
      sizes: facets.sizes?.map((entry) => entry.label) || defaultFacetState.sizes,
      themes: facets.themes?.map((entry) => entry.label) || defaultFacetState.themes
    }
  }

  const genres = [...new Set(items.map((item) => item.genre))]
  const sizes = [...new Set(items.map((item) => item.size))]
  const themes = [...new Set(items.map((item) => item.theme))]
  return {
    genres: genres.length ? genres : defaultFacetState.genres,
    sizes: sizes.length ? sizes : defaultFacetState.sizes,
    themes: themes.length ? themes : defaultFacetState.themes
  }
}

export const storyworldJsonToPayload = ({ json, fileName, selectedGenre, selectedSize, selectedTheme }) => {
  const titleFromFile = (fileName || 'uploaded_storyworld').replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ').trim()
  const encounter = json.encounter ? json : { encounters: json.encounters || [], ...json }
  const firstEncounter = pickNarrative(encounter)

  const numCharacters = Array.isArray(json.characters) ? json.characters.length : 3
  const numThemes = Array.isArray(json.themes) ? json.themes.length : 2
  const numVariables = Array.isArray(json.variables || json.state_variables)
    ? (json.variables || json.state_variables).length
    : 5

  const encounterLength = estimateEncounterLength(firstEncounter.text, 500)
  const genre = selectedGenre === 'all' ? deriveGenre(json) : selectedGenre
  const sizeTag = selectedSize === 'all' ? deriveSize(encounterLength) : selectedSize
  const themeVariant = selectedTheme === 'all' ? 'midnight' : selectedTheme

  return {
    title: json.title || titleFromFile || 'Imported Storyworld',
    description: json.description || firstEncounter.text.slice(0, 180),
    num_characters: clamp(numCharacters, 1, 10, 3),
    num_themes: clamp(numThemes, 1, 5, 2),
    num_variables: clamp(numVariables, 3, 20, 5),
    encounter_length: encounterLength,
    custom_prompt: json.custom_prompt || 'Imported from Storyworld JSON',
    encounter,
    system_prompt: json.system_prompt || '',
    is_public: true,
    model_used: json.model_used || 'gpt-4.1',
    temperature: 0.8,
    genre,
    size_tag: sizeTag,
    theme_variant: themeVariant,
    cover_image: json.cover_image || null,
    banner_image: json.banner_image || null,
    tags: Array.isArray(json.tags) ? json.tags : []
  }
}
