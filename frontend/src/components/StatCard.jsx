import { ArrowDownRight, ArrowUpRight } from 'lucide-react'

const accents = {
  blue: { icon: 'bg-blue-400/10 text-blue-300', glow: 'from-blue-500/10' },
  cyan: { icon: 'bg-cyan-400/10 text-cyan-200', glow: 'from-cyan-500/10' },
  green: { icon: 'bg-emerald-400/10 text-emerald-300', glow: 'from-emerald-500/10' },
  violet: { icon: 'bg-violet-400/10 text-violet-300', glow: 'from-violet-500/10' },
}

export default function StatCard({ title, value, change, description, icon: Icon, accent = 'cyan', trend = 'up' }) {
  const style = accents[accent] ?? accents.cyan
  const TrendIcon = trend === 'down' ? ArrowDownRight : ArrowUpRight
  const positive = trend === 'up'

  return (
    <article className="panel group relative overflow-hidden p-5 transition duration-300 hover:-translate-y-1 hover:border-cyan-300/20 hover:shadow-[0_16px_45px_rgba(0,0,0,0.22)]">
      <div className={`pointer-events-none absolute -right-10 -top-12 h-32 w-32 rounded-full bg-gradient-to-br ${style.glow} to-transparent opacity-0 blur-2xl transition duration-500 group-hover:opacity-100`} />
      <div className="relative flex items-start justify-between gap-3">
        <div>
          <p className="text-[13px] text-slate-400">{title}</p>
          <p className="mt-4 whitespace-nowrap text-[25px] font-semibold tracking-tight text-white sm:text-[28px]">{value}</p>
        </div>
        <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl ${style.icon}`}>
          <Icon size={19} strokeWidth={1.8} />
        </span>
      </div>
      <div className="relative mt-4 flex flex-wrap items-center gap-2">
        <span className={`inline-flex items-center gap-0.5 rounded-md px-1.5 py-1 text-[11px] font-semibold ${positive ? 'bg-emerald-400/10 text-emerald-300' : 'bg-cyan-400/10 text-cyan-200'}`}>
          <TrendIcon size={13} /> {change}
        </span>
        <span className="text-[11px] text-slate-500">{description}</span>
      </div>
    </article>
  )
}
