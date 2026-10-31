export default function StatCard({ title, value, subtitle, tone = 'default', icon: Icon }) {
  const toneClasses = {
    default: 'bg-white text-slate-800',
    emerald: 'bg-emerald-50 text-emerald-700',
    sky: 'bg-sky-50 text-sky-700',
    amber: 'bg-amber-50 text-amber-700',
    rose: 'bg-rose-50 text-rose-700',
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <h3 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">{value}</h3>
        </div>

        {Icon ? (
          <div className={`rounded-xl p-2.5 ${toneClasses[tone]}`}>
            <Icon size={20} />
          </div>
        ) : null}
      </div>

      {subtitle ? <p className="mt-3 text-sm text-slate-500">{subtitle}</p> : null}
    </div>
  )
}
