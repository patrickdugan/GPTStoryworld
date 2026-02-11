import { BookOpenText, Sparkles } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

export default function ReaderPanel({ storyworld }) {
  const [selectedChoice, setSelectedChoice] = useState('')

  useEffect(() => {
    setSelectedChoice('')
  }, [storyworld?.id])

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
    <section
      data-testid="reader-panel"
      className="sticky top-2 h-fit rounded-xl border border-[color:var(--sw-border)] bg-[color:var(--sw-panel)] p-4 shadow-card"
    >
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="font-display text-lg font-semibold text-white">
          <BookOpenText className="mr-2 inline h-5 w-5 text-[color:var(--sw-accent)]" />
          Reader Console
        </h2>
      </div>

      <h3 className="text-base font-bold text-slate-100">{details.title}</h3>
      <p className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-400">{details.description}</p>

      <article className="mt-4 rounded-lg border border-[color:var(--sw-border)] bg-slate-950/50 p-3">
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
              className={`rounded-md border px-3 py-2 text-left text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan ${
                active
                  ? 'border-[color:var(--sw-accent)] bg-[color:var(--sw-accent-soft)] text-white'
                  : 'border-[color:var(--sw-border)] bg-slate-900/70 text-slate-200 hover:border-slate-500'
              }`}
            >
              {choice}
            </button>
          )
        })}
      </div>

      <div className="mt-4 rounded-md border border-[color:var(--sw-border)] bg-slate-900/40 p-2.5 text-xs text-slate-300">
        <Sparkles className="mr-2 inline h-4 w-4 text-[color:var(--sw-accent)]" />
        TODO: Connect selected choice to live next-encounter generation and branch playback.
      </div>
    </section>
  )
}
