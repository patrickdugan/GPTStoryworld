import { BookOpenText, Castle, Cpu, Landmark, SearchCheck, Skull, Sparkles, Sword } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

const GENRE_TEMPLATES = {
  diplomacy: {
    key: 'diplomacy',
    label: 'Diplomatic Dossier',
    subtitle: 'Caucus Clock',
    icon: Landmark
  },
  strategy: {
    key: 'strategy',
    label: 'Command Grid',
    subtitle: 'Operations Ledger',
    icon: Sword
  },
  mystery: {
    key: 'mystery',
    label: 'Case File',
    subtitle: 'Evidence Thread',
    icon: SearchCheck
  },
  scifi: {
    key: 'scifi',
    label: 'Shipboard Terminal',
    subtitle: 'Signal Diagnostics',
    icon: Cpu
  },
  horror: {
    key: 'horror',
    label: 'Incident Log',
    subtitle: 'Containment Status',
    icon: Skull
  },
  fantasy: {
    key: 'fantasy',
    label: 'Arcane Chronicle',
    subtitle: 'Rune Sequence',
    icon: Castle
  },
  default: {
    key: 'default',
    label: 'Reader Console',
    subtitle: 'Narrative Runtime',
    icon: BookOpenText
  }
}

const normalizeGenreKey = (genre) => {
  const normalized = String(genre || '')
    .toLowerCase()
    .replace(/[^a-z]/g, '')
  if (normalized === 'scifi' || normalized === 'sciencefiction') return 'scifi'
  return normalized || 'default'
}

export default function ReaderPanel({ storyworld, templateOverride = 'auto' }) {
  const [selectedChoice, setSelectedChoice] = useState('')

  useEffect(() => {
    setSelectedChoice('')
  }, [storyworld?.id])

  const template = useMemo(() => {
    const overrideKey = templateOverride === 'auto' ? '' : normalizeGenreKey(templateOverride)
    const key = overrideKey || normalizeGenreKey(storyworld?.genre)
    return GENRE_TEMPLATES[key] || GENRE_TEMPLATES.default
  }, [storyworld?.genre, templateOverride])

  const details = useMemo(() => {
    if (!storyworld) {
      return {
        title: 'Select a storyworld card',
        description: 'Choose any card from a row to open a live reader panel.',
        choices: ['TODO: Select a card to start'],
        text: 'The reader panel mirrors storyworld_reader.html behavior: narrative + decisions + theme styling.'
      }
    }

    return {
      title: storyworld.title,
      description: `${storyworld.genre} | ${storyworld.size} | ${storyworld.numCharacters} characters | ${storyworld.numThemes} themes`,
      choices: storyworld.choices,
      text: storyworld.readerText
    }
  }, [storyworld])

  return (
    <section data-testid="reader-panel" className={`reader-template reader-template-${template.key} sticky top-2 h-fit rounded-xl border p-4 shadow-card`}>
      <div aria-hidden="true" className="reader-veil" />
      <div aria-hidden="true" className="reader-noise" />
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="font-display text-lg font-semibold text-white">
          <template.icon className="mr-2 inline h-5 w-5 text-[color:var(--reader-accent)]" />
          {template.label}
        </h2>
        <span
          data-testid="reader-template"
          className="rounded-full border border-[color:var(--reader-border)] bg-[color:var(--reader-chip)] px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--reader-accent)]"
        >
          {template.subtitle}
        </span>
      </div>

      <h3 className="text-base font-bold text-slate-100">{details.title}</h3>
      <p className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-300">{details.description}</p>

      <article className="reader-copy mt-4 rounded-lg border p-3">
        <p className="text-sm leading-relaxed text-slate-200">{details.text}</p>
      </article>

      <div className="mt-4 grid gap-2">
        {details.choices.slice(0, 4).map((choice) => {
          const active = choice === selectedChoice
          return (
            <button
              key={choice}
              type="button"
              onClick={() => setSelectedChoice(choice)}
              className={`reader-choice rounded-md border px-3 py-2 text-left text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan ${
                active
                  ? 'reader-choice-active text-white'
                  : 'text-slate-100 hover:text-white'
              }`}
            >
              {choice}
            </button>
          )
        })}
      </div>

      <div className="reader-footer mt-4 rounded-md border p-2.5 text-xs text-slate-200">
        <span className="reader-status-dot" aria-hidden="true" />
        <Sparkles className="mr-2 inline h-4 w-4 text-[color:var(--reader-accent)]" />
        TODO: Connect selected choice to live next-encounter generation and branch playback.
      </div>
    </section>
  )
}
