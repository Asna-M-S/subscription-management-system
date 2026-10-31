import { LayoutGrid, FileText, CreditCard, BarChart3, Settings, HelpCircle } from 'lucide-react'

const navItems = [
  { label: 'Dashboard', icon: LayoutGrid, active: true },
  { label: 'Invoices', icon: FileText },
  { label: 'Payments', icon: CreditCard },
  { label: 'Reports', icon: BarChart3 },
  { label: 'Settings', icon: Settings },
  { label: 'Support', icon: HelpCircle },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-slate-100 p-6 hidden md:flex md:flex-col">
      <div className="mb-10">
        <div className="text-2xl font-bold tracking-tight">BrightLoop</div>
      </div>

      <nav className="space-y-2">
        {navItems.map(({ label, icon: Icon, active }) => (
          <button
            key={label}
            type="button"
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition ${
              active ? 'bg-slate-800 text-white' : 'text-slate-300 hover:bg-slate-800/70'
            }`}
          >
            <Icon size={18} />
            <span className="font-medium">{label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
