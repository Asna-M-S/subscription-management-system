import {
  Activity,
  CreditCard,
  FileText,
  LayoutDashboard,
  Settings2,
  UsersRound,
  WalletCards,
} from 'lucide-react'

const navigation = [
  { label: 'Dashboard', icon: LayoutDashboard, active: true },
  { label: 'Subscriptions', icon: CreditCard },
  { label: 'Customers', icon: UsersRound },
  { label: 'Invoices', icon: FileText },
  { label: 'Payments', icon: WalletCards },
  { label: 'Analytics', icon: Activity },
  { label: 'Settings', icon: Settings2 },
]

function Brand() {
  return (
    <a href="#overview" className="flex items-center gap-3" aria-label="BrightLoop dashboard">
      <span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-cyan-300 to-blue-500 text-slate-950 shadow-lg shadow-cyan-500/10">
        <span className="text-xl font-black leading-none">B</span>
      </span>
      <span>
        <span className="block text-[17px] font-semibold tracking-tight text-white">BrightLoop</span>
        <span className="block text-[10px] font-medium uppercase tracking-[0.16em] text-slate-500">Finance workspace</span>
      </span>
    </a>
  )
}

function Navigation({ mobile = false }) {
  return (
    <nav aria-label="Main navigation" className={mobile ? 'flex min-w-max items-center gap-1 px-4 pb-3' : 'space-y-1'}>
      {navigation.map(({ label, icon: Icon, active }) => (
        <a
          key={label}
          href={active ? '#overview' : `#${label.toLowerCase()}`}
          aria-current={active ? 'page' : undefined}
          className={`${mobile ? 'flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-xs' : 'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px]'} transition ${
            active
              ? 'border border-cyan-300/10 bg-gradient-to-r from-cyan-400/15 to-blue-500/[0.04] text-cyan-200'
              : 'text-slate-400 hover:bg-white/[0.04] hover:text-slate-100'
          }`}
        >
          <Icon size={17} strokeWidth={active ? 2 : 1.8} />
          <span className={active ? 'font-medium' : ''}>{label}</span>
          {active && !mobile && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_8px_rgba(103,232,249,0.8)]" />}
        </a>
      ))}
    </nav>
  )
}

export default function Sidebar() {
  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[258px] flex-col border-r border-white/[0.055] bg-[#0b101a] px-5 py-6 lg:flex">
        <Brand />
        <div className="mt-10 px-3 text-[10px] font-semibold uppercase tracking-[0.17em] text-slate-600">Workspace</div>
        <div className="mt-3"><Navigation /></div>
        <div className="mt-auto rounded-2xl border border-cyan-300/10 bg-gradient-to-br from-cyan-400/[0.08] to-blue-500/[0.025] p-4">
          <div className="mb-3 grid h-8 w-8 place-items-center rounded-lg bg-cyan-300/10 text-cyan-200">
            <Activity size={16} />
          </div>
          <p className="text-xs font-medium text-slate-200">Everything in sync</p>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-500">Your financial workspace is up to date.</p>
          <div className="mt-3 flex items-center gap-1.5 text-[10px] font-medium text-emerald-300">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> All systems operational
          </div>
        </div>
        <div className="mt-5 border-t border-white/[0.06] pt-4 text-[11px] text-slate-600">© 2026 BrightLoop</div>
      </aside>
      <div className="border-b border-white/[0.06] bg-[#0b101a] lg:hidden">
        <div className="px-4 py-4 sm:px-6"><Brand /></div>
        <div className="overflow-x-auto"><Navigation mobile /></div>
      </div>
    </>
  )
}
