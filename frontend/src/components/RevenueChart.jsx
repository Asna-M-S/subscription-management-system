import { useState } from 'react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { ArrowUpRight, TrendingUp } from 'lucide-react'
import { revenueSeries as fallbackSeries } from '../mock/dashboardData'

const formatTooltipValue = (value) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value)

function RevenueTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl border border-slate-700 bg-[#0b1220] px-3.5 py-3 shadow-xl">
      <p className="text-xs text-slate-400">{label}</p>
      <p className="mt-1 text-sm font-semibold text-white">{formatTooltipValue(payload[0].value)}</p>
    </div>
  )
}

export default function RevenueChart({ seriesData = fallbackSeries }) {
  const [period, setPeriod] = useState('Monthly')
  const chartData = seriesData[period] ?? fallbackSeries[period]
  const total = chartData.reduce((sum, point) => sum + point.revenue, 0)
  const average = Math.round(total / chartData.length)

  return (
    <section className="panel min-w-0 overflow-hidden p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Performance</p>
          <h2 className="text-lg font-semibold text-white sm:text-xl">Revenue analytics</h2>
          <div className="mt-3 flex items-center gap-2">
            <span className="text-2xl font-semibold tracking-tight text-white">{formatTooltipValue(average)}</span>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-400/10 px-2 py-1 text-xs font-medium text-emerald-300">
              <ArrowUpRight size={13} /> 16.2%
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">Average revenue per {period.toLowerCase().replace(/ly$/, '')} period</p>
        </div>
        <div className="flex rounded-lg border border-white/[0.07] bg-[#0b111c] p-1" aria-label="Revenue chart period">
          {Object.keys(fallbackSeries).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setPeriod(option)}
              aria-pressed={period === option}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${period === option ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-500 hover:text-slate-200'}`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 h-[230px] w-full min-w-0 overflow-hidden sm:h-[270px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 8, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.28} />
                <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#ffffff" strokeOpacity={0.055} vertical={false} />
            <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} dy={10} />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={(value) => `₹${value / 1000}k`}
              width={48}
            />
            <Tooltip content={<RevenueTooltip />} cursor={{ stroke: '#94a3b8', strokeOpacity: 0.18 }} />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#22d3ee"
              strokeWidth={2.5}
              fill="url(#revenueFill)"
              activeDot={{ r: 5, fill: '#22d3ee', stroke: '#0b111c', strokeWidth: 3 }}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
        <TrendingUp size={14} className="text-cyan-300" />
        Revenue growth is trending above your monthly target
      </div>
    </section>
  )
}
