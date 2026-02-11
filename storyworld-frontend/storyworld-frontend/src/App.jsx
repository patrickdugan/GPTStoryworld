import { Database, RefreshCw, Search, Upload } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import BottomNav from './components/BottomNav'
import FilterTabs from './components/FilterTabs'
import HeroBanner from './components/HeroBanner'
import ReaderPanel from './components/ReaderPanel'
import StoryRow from './components/StoryRow'
import { demoStoryworlds } from './data/demoStoryworlds'
import {
  buildRows,
  defaultFacetState,
  facetOptionsFromApi,
  normalizeStoryworld,
  storyworldJsonToPayload
} from './lib/storyworldClient'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api').replace(/\/$/, '')

const toTabOptions = (list, allLabel) => [{ value: 'all', label: allLabel }, ...list.map((label) => ({ value: label, label }))]

const toLowerTabOptions = (list, allLabel) => [
  { value: 'all', label: allLabel },
  ...list.map((label) => ({ value: String(label).toLowerCase(), label: String(label) }))
]

function App() {
  const fileInputRef = useRef(null)

  const [storyworlds, setStoryworlds] = useState(demoStoryworlds.map(normalizeStoryworld))
  const [facets, setFacets] = useState(defaultFacetState)
  const [selectedGenre, setSelectedGenre] = useState('all')
  const [selectedSize, setSelectedSize] = useState('all')
  const [selectedTheme, setSelectedTheme] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeStoryworld, setActiveStoryworld] = useState(null)
  const [loading, setLoading] = useState(false)
  const [statusText, setStatusText] = useState('Using demo data until backend responds.')
  const [reloadKey, setReloadKey] = useState(0)

  const activeVisualTheme = selectedTheme === 'all' ? 'midnight' : selectedTheme

  const genreOptions = useMemo(() => toTabOptions(facets.genres, 'All Genres'), [facets.genres])
  const sizeOptions = useMemo(() => toLowerTabOptions(facets.sizes, 'All Sizes'), [facets.sizes])
  const themeOptions = useMemo(() => toLowerTabOptions(facets.themes, 'All Themes'), [facets.themes])

  const rows = useMemo(() => buildRows(storyworlds), [storyworlds])
  const featured = rows[0]?.items[0] || storyworlds[0] || demoStoryworlds[0]

  useEffect(() => {
    if (!activeStoryworld && storyworlds.length > 0) {
      setActiveStoryworld(storyworlds[0])
    }
  }, [activeStoryworld, storyworlds])

  useEffect(() => {
    const controller = new AbortController()

    const fetchStoryworlds = async () => {
      setLoading(true)
      const params = new URLSearchParams({
        limit: '60',
        sort: 'likes',
        order: 'desc'
      })
      if (selectedGenre !== 'all') params.set('genre', selectedGenre)
      if (selectedSize !== 'all') params.set('size', selectedSize)
      if (selectedTheme !== 'all') params.set('theme', selectedTheme)
      if (searchQuery.trim()) params.set('q', searchQuery.trim())

      try {
        const response = await fetch(`${API_BASE}/storyworlds?${params.toString()}`, {
          signal: controller.signal
        })
        if (!response.ok) throw new Error(`Backend returned ${response.status}`)

        const payload = await response.json()
        const normalized = (payload.storyworlds || []).map(normalizeStoryworld)
        if (normalized.length === 0) {
          setStoryworlds(demoStoryworlds.map(normalizeStoryworld))
          setFacets(facetOptionsFromApi(payload.facets, demoStoryworlds.map(normalizeStoryworld)))
          setStatusText('No DB rows for current filters. Showing demo catalog.')
          return
        }

        setStoryworlds(normalized)
        setFacets(facetOptionsFromApi(payload.facets, normalized))
        setStatusText(`Loaded ${normalized.length} storyworlds from backend DB.`)
      } catch (error) {
        if (error.name === 'AbortError') return
        const local = demoStoryworlds.map(normalizeStoryworld)
        setStoryworlds(local)
        setFacets(facetOptionsFromApi(null, local))
        setStatusText(`Backend unavailable (${error.message}). Showing demo catalog.`)
      } finally {
        setLoading(false)
      }
    }

    fetchStoryworlds()
    return () => controller.abort()
  }, [selectedGenre, selectedSize, selectedTheme, searchQuery, reloadKey])

  const refreshData = () => {
    setStatusText('Refreshing data from backend...')
    setReloadKey((value) => value + 1)
  }

  const openFilePicker = () => fileInputRef.current?.click()

  const handleImportJson = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const content = await file.text()
      const json = JSON.parse(content)
      const payload = storyworldJsonToPayload({
        json,
        fileName: file.name,
        selectedGenre,
        selectedSize,
        selectedTheme
      })

      const response = await fetch(`${API_BASE}/storyworlds`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.error || 'Failed to upload storyworld')
      }
      setStatusText(`Imported "${payload.title}" into backend DB.`)
      setReloadKey((value) => value + 1)
    } catch (error) {
      setStatusText(`Import failed: ${error.message}`)
    } finally {
      event.target.value = ''
    }
  }

  return (
    <div className={`theme-${activeVisualTheme} min-h-screen bg-ink font-body text-slate-100`}>
      <HeroBanner
        featured={{
          ...featured,
          image: featured.bannerImage || featured.coverImage
        }}
        onOpenReader={setActiveStoryworld}
      />

      <section className="mx-auto flex max-w-screen-2xl flex-col gap-3 px-4 pt-4 sm:px-6 md:px-10">
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[color:var(--sw-border)] bg-[color:var(--sw-panel)]/75 px-3 py-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              aria-label="Search storyworlds"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search by title, description, or prompt..."
              className="w-full rounded-md border border-slate-700 bg-slate-950/65 py-2 pl-9 pr-3 text-sm text-slate-100 placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={refreshData}
              className="inline-flex items-center gap-2 rounded-md border border-slate-700 bg-slate-900/70 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-200 hover:border-slate-500 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              type="button"
              onClick={openFilePicker}
              className="inline-flex items-center gap-2 rounded-md border border-[color:var(--sw-accent)]/45 bg-[color:var(--sw-accent-soft)] px-3 py-2 text-xs font-semibold uppercase tracking-wide text-white hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
            >
              <Upload className="h-4 w-4" />
              Import JSON
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,application/json"
              className="hidden"
              onChange={handleImportJson}
            />
          </div>
        </div>

        <div className="grid gap-3 rounded-xl border border-[color:var(--sw-border)] bg-[color:var(--sw-panel)]/45 p-3">
          <FilterTabs label="Genre" options={genreOptions} value={selectedGenre} onChange={setSelectedGenre} testId="genre-tabs" />
          <FilterTabs label="Size" options={sizeOptions} value={selectedSize} onChange={setSelectedSize} testId="size-tabs" />
          <FilterTabs label="Theme" options={themeOptions} value={selectedTheme} onChange={setSelectedTheme} testId="theme-tabs" />
        </div>

        <div className="inline-flex items-center gap-2 rounded-md border border-slate-700 bg-slate-900/55 px-3 py-2 text-xs text-slate-300">
          <Database className="h-4 w-4 text-cyan" />
          {statusText}
        </div>
      </section>

      <main className="mx-auto grid max-w-screen-2xl gap-8 px-4 pb-24 pt-4 sm:px-6 md:grid-cols-[minmax(0,1fr)_360px] md:px-10">
        <section className="flex min-w-0 flex-col gap-9">
          {rows.map((row, rowIndex) => (
            <StoryRow
              key={row.id}
              title={row.title}
              rowIndex={rowIndex}
              items={row.items.map((item) => ({
                id: item.id,
                title: item.title,
                image: item.coverImage,
                meta: `${item.likes} likes`,
                genre: item.genre,
                size: item.size
              }))}
              onSelect={(selected) => {
                const full = storyworlds.find((entry) => entry.id === selected.id)
                setActiveStoryworld(full || null)
              }}
            />
          ))}
        </section>
        <ReaderPanel storyworld={activeStoryworld} />
      </main>

      <BottomNav />
    </div>
  )
}

export default App
