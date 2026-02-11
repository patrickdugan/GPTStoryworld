import { Compass, Home, Search, Settings2 } from 'lucide-react'

const items = [
  { label: 'Home', icon: Home, active: true },
  { label: 'Discover', icon: Compass },
  { label: 'Search', icon: Search },
  { label: 'Settings', icon: Settings2 }
]

export default function BottomNav() {
  return (
    <nav
      aria-label="Primary navigation"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-slate-700/70 bg-slate-950/90 backdrop-blur-sm"
    >
      {/* TODO(Vision): Re-check icon vertical alignment against mobile screenshots. */}
      <ul className="mx-auto grid max-w-screen-md grid-cols-4">
        {items.map(({ label, icon: Icon, active }) => (
          <li key={label}>
            <button
              type="button"
              aria-current={active ? 'page' : undefined}
              className="mx-auto flex h-16 w-full flex-col items-center justify-center gap-1 py-2 text-[11px] font-medium leading-none text-slate-300 transition hover:bg-slate-800/60 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              <Icon className={`h-5 w-5 shrink-0 ${active ? 'text-accent' : 'text-slate-300'}`} />
              <span>{label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  )
}
