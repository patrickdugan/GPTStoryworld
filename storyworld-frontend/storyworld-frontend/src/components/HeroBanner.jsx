import { Info, Play } from 'lucide-react'

export default function HeroBanner({ featured, onOpenReader }) {
  const heroStyle = {
    backgroundImage: `linear-gradient(90deg, rgba(7,11,18,0.95) 0%, rgba(7,11,18,0.62) 48%, rgba(7,11,18,0.92) 100%), url(${featured.image || featured.bannerImage})`
  }

  return (
    <header
      data-testid="hero-banner"
      className="relative w-full min-h-[29vh] sm:min-h-[40vh] lg:min-h-[48vh] overflow-hidden bg-cover bg-center animate-rise"
      style={heroStyle}
    >
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-[radial-gradient(circle_at_15%_25%,rgba(34,211,238,0.2),transparent_36%),radial-gradient(circle_at_85%_10%,rgba(249,115,22,0.18),transparent_38%)]"
      />
      <div className="relative mx-auto flex h-full max-w-screen-2xl flex-col justify-end px-4 pb-5 pt-10 sm:px-6 md:px-10 lg:pb-10">
        <p className="font-display text-xs uppercase tracking-[0.28em] text-cyan">Featured Storyworld</p>
        <div className="mt-2 flex flex-wrap gap-2">
          <span className="rounded-full border border-cyan/40 bg-cyan/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-cyan">
            {featured.genre || 'Genre'}
          </span>
          <span className="rounded-full border border-slate-300/30 bg-slate-700/25 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-200">
            {featured.size || 'Standard'}
          </span>
        </div>
        <h1 className="mt-3 max-w-3xl font-display text-3xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
          {featured.title}
        </h1>
        <p className="mt-2 line-clamp-2 max-w-2xl text-sm text-slate-200 sm:mt-3 sm:line-clamp-none sm:text-base">{featured.description}</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => onOpenReader(featured)}
            className="inline-flex items-center gap-2 rounded-md bg-white px-5 py-2.5 text-sm font-semibold text-ink transition hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            <Play className="h-4 w-4" />
            Open Reader
          </button>
          <button
            type="button"
            onClick={() => onOpenReader(featured)}
            className="inline-flex items-center gap-2 rounded-md bg-slate-700/75 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
          >
            <Info className="h-4 w-4" />
            Details
          </button>
        </div>
      </div>
    </header>
  )
}
