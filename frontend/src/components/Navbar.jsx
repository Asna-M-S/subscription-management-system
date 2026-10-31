import { useState } from 'react'
import { Bell, ChevronDown, Search } from 'lucide-react'

export default function Navbar({ query, onQueryChange }) {
  const [dateLabel] = useState(() => new Intl.DateTimeFormat('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date()))

  return (
    <header className="sticky top-0 z-20 border-b border-white/[0.055] bg-[#080b14]/90 px-4 py-3.5 backdrop-blur-xl sm:px-6 lg:px-9">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-3">
        <label className="flex min-w-0 max-w-[420px] flex-1 items-center gap-2.5 rounded-xl border border-white/[0.07] bg-[#111827]/75 px-3.5 py-2.5 transition focus-within:border-cyan-300/30">
          <Search size={16} className="shrink-0 text-slate-500" />
          <input
            type="search"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Search transactions..."
            aria-label="Search transactions"
            className="w-full min-w-0 bg-transparent text-xs text-slate-200 outline-none placeholder:text-slate-600"
          />
          <kbd className="hidden rounded border border-white/[0.08] px-1.5 py-0.5 text-[10px] text-slate-600 sm:inline">⌘ K</kbd>
        </label>

        <div className="flex items-center gap-2 sm:gap-4">
          <p className="hidden text-xs text-slate-500 md:block">{dateLabel}</p>
          <span className="hidden h-5 w-px bg-white/[0.08] md:block" />
          <button type="button" aria-label="Notifications" className="relative grid h-9 w-9 place-items-center rounded-xl text-slate-400 transition hover:bg-white/[0.05] hover:text-white">
            <Bell size={17} />
            <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-cyan-300 ring-2 ring-[#080b14]" />
          </button>
          <button type="button" className="flex items-center gap-2 rounded-xl py-1 pl-1 pr-1.5 transition hover:bg-white/[0.04]" aria-label="Open profile menu">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-indigo-400 to-cyan-400 text-[11px] font-bold text-slate-950">VM</span>
            <span className="hidden text-left sm:block">
              <span className="block text-xs font-medium text-slate-200">Vishal Mehra</span>
              <span className="mt-0.5 block text-[10px] text-slate-500">Administrator</span>
            </span>
            <ChevronDown size={14} className="hidden text-slate-500 sm:block" />
          </button>
        </div>
      </div>
    </header>
  )
}
