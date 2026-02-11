export default function FilterTabs({ label, options, value, onChange, testId }) {
  return (
    <section className="flex flex-col gap-2" data-testid={testId}>
      <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-400">{label}</h2>
      <div role="tablist" aria-label={label} className="flex gap-2 overflow-x-auto pb-1">
        {options.map((option) => {
          const active = option.value === value
          return (
            <button
              key={option.value}
              role="tab"
              aria-selected={active}
              type="button"
              className={`shrink-0 whitespace-nowrap rounded-full border px-3 py-1.5 text-xs font-semibold tracking-wide transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan ${
                active
                  ? 'border-cyan/60 bg-cyan/20 text-cyan'
                  : 'border-slate-700 bg-slate-900/55 text-slate-300 hover:border-slate-500 hover:text-white'
              }`}
              onClick={() => onChange(option.value)}
            >
              {option.label}
            </button>
          )
        })}
      </div>
    </section>
  )
}
