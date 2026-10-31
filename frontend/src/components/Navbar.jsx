import { Bell, Search, ChevronDown } from 'lucide-react'

export default function Navbar() {
  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
      <div className="flex items-center gap-3 bg-slate-100 rounded-xl px-3 py-2 w-full max-w-md">
        <Search size={18} className="text-slate-500" />
        <input
          type="text"
          placeholder="Search subscriptions"
          className="w-full bg-transparent border-0 outline-none text-sm text-slate-700 placeholder:text-slate-400"
        />
      </div>

      <div className="flex items-center gap-4 ml-6">
        <button type="button" className="relative p-2 rounded-full hover:bg-slate-100 text-slate-600">
          <Bell size={18} />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-rose-500" />
        </button>

        <div className="flex items-center gap-3 bg-slate-100 rounded-xl px-3 py-2">
          <div className="h-9 w-9 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-sm font-bold text-white">
            VM
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-sm font-semibold text-slate-800">Vishal Mehra</div>
            <div className="text-xs text-slate-500">Admin</div>
          </div>
          <ChevronDown size={16} className="text-slate-500" />
        </div>
      </div>
    </header>
  )
}
