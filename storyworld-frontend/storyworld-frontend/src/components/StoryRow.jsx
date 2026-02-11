import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useRef } from 'react'

function Card({ item, onSelect }) {
  return (
    <button
      type="button"
      data-testid="story-card"
      className="group relative h-40 w-40 shrink-0 snap-start overflow-hidden rounded-lg bg-slate-900 shadow-card transition duration-200 hover:-translate-y-1 hover:scale-[1.02] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent sm:h-48 sm:w-52"
      aria-label={item.title}
      onClick={() => onSelect(item)}
    >
      <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-br from-slate-800 via-slate-900 to-black" />
      <img
        src={item.image}
        alt=""
        className="h-full w-full object-cover opacity-75 transition group-hover:opacity-90"
        onError={(event) => {
          event.currentTarget.style.display = 'none'
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 p-3">
        <h3 className="font-display text-sm font-semibold text-white">{item.title}</h3>
        <p className="mt-0.5 text-[10px] uppercase tracking-[0.14em] text-slate-300">
          {item.genre} - {item.size}
        </p>
        <p className="mt-1 line-clamp-2 text-xs text-slate-200">{item.meta}</p>
      </div>
    </button>
  )
}

export default function StoryRow({ title, items, rowIndex, onSelect }) {
  const rowRef = useRef(null)

  const scrollByAmount = (amount) => {
    if (!rowRef.current) return
    rowRef.current.scrollBy({ left: amount, behavior: 'smooth' })
  }

  return (
    <section data-testid="carousel-row" aria-label={title} className="animate-rise" style={{ animationDelay: `${120 + rowIndex * 90}ms` }}>
      <div className="mb-3 flex items-center justify-between gap-4">
        <h2 className="font-display text-lg font-semibold tracking-tight text-slate-100 sm:text-2xl">{title}</h2>
        <div className="hidden items-center gap-2 sm:flex">
          <button
            type="button"
            onClick={() => scrollByAmount(-320)}
            className="rounded-md border border-slate-700 bg-slate-900/70 p-2 text-slate-200 transition hover:border-slate-500 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
            aria-label={`Scroll ${title} left`}
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => scrollByAmount(320)}
            className="rounded-md border border-slate-700 bg-slate-900/70 p-2 text-slate-200 transition hover:border-slate-500 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
            aria-label={`Scroll ${title} right`}
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div
        ref={rowRef}
        className="flex snap-x gap-4 overflow-x-auto pb-2"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === 'ArrowRight') scrollByAmount(240)
          if (event.key === 'ArrowLeft') scrollByAmount(-240)
        }}
      >
        {items.map((item) => (
          <Card key={item.id} item={item} onSelect={onSelect} />
        ))}
      </div>
    </section>
  )
}
