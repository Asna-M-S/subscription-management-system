import { useState } from 'react'
import { CalendarDays, ChevronLeft, ChevronRight, Clock3, CreditCard } from 'lucide-react'
import { calendarPayments } from '../mock/dashboardData'
import { formatCurrency } from '../services/formatters'

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const getDateKey = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const statusClass = {
  Paid: 'bg-emerald-400',
  Pending: 'bg-amber-400',
  Failed: 'bg-rose-400',
}

export default function PaymentCalendar({ payments = calendarPayments }) {
  const [today] = useState(() => new Date())
  const [currentMonth, setCurrentMonth] = useState(() => new Date(today.getFullYear(), today.getMonth(), 1))
  const [selectedDate, setSelectedDate] = useState(() => new Date(today.getFullYear(), today.getMonth(), today.getDate()))
  const year = currentMonth.getFullYear()
  const month = currentMonth.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const leadingDays = new Date(year, month, 1).getDay()
  const dateCells = [...Array(leadingDays).fill(null), ...Array.from({ length: daysInMonth }, (_, index) => index + 1)]
  const selectedPayments = payments[getDateKey(selectedDate)] ?? []

  const moveMonth = (amount) => {
    const updatedMonth = new Date(year, month + amount, 1)
    setCurrentMonth(updatedMonth)
    setSelectedDate(new Date(updatedMonth.getFullYear(), updatedMonth.getMonth(), 1))
  }

  return (
    <section className="panel p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Schedule</p>
          <h2 className="text-lg font-semibold text-white sm:text-xl">Payment calendar</h2>
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-white/[0.07] bg-[#0b111c] p-1">
          <button type="button" onClick={() => moveMonth(-1)} aria-label="Previous month" className="rounded-md p-1.5 text-slate-400 transition hover:bg-slate-800 hover:text-white">
            <ChevronLeft size={17} />
          </button>
          <span className="min-w-[118px] text-center text-xs font-medium text-slate-200">
            {currentMonth.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}
          </span>
          <button type="button" onClick={() => moveMonth(1)} aria-label="Next month" className="rounded-md p-1.5 text-slate-400 transition hover:bg-slate-800 hover:text-white">
            <ChevronRight size={17} />
          </button>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-7 gap-y-1 text-center">
        {weekDays.map((day) => (
          <div key={day} className="py-2 text-[10px] font-medium uppercase tracking-wide text-slate-600 sm:text-[11px]">{day}</div>
        ))}
        {dateCells.map((day, index) => {
          if (day === null) return <div key={`empty-${index}`} aria-hidden="true" />
          const date = new Date(year, month, day)
          const key = getDateKey(date)
          const entries = payments[key] ?? []
          const isToday = key === getDateKey(today)
          const isSelected = key === getDateKey(selectedDate)
          return (
            <button
              key={key}
              type="button"
              onClick={() => setSelectedDate(date)}
              aria-label={`${date.toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}${entries.length ? `, ${entries.length} payments` : ''}`}
              aria-pressed={isSelected}
              className={`relative mx-auto flex aspect-square w-full max-w-10 flex-col items-center justify-center rounded-xl text-xs transition sm:text-sm ${
                isSelected ? 'bg-cyan-400 font-semibold text-slate-950 shadow-[0_0_20px_rgba(34,211,238,0.2)]'
                  : isToday ? 'border border-cyan-400/40 text-cyan-200 hover:bg-cyan-400/10'
                    : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              {day}
              {entries.length > 0 && (
                <span className="absolute bottom-1 flex gap-0.5">
                  {entries.slice(0, 3).map((entry, dotIndex) => (
                    <span key={`${entry.customer}-${dotIndex}`} className={`h-1 w-1 rounded-full ${isSelected ? 'bg-slate-950' : statusClass[entry.status]}`} />
                  ))}
                </span>
              )}
            </button>
          )
        })}
      </div>
      <div className="mt-3 flex items-center gap-2 text-[11px] text-slate-500">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Paid
        <span className="ml-2 h-1.5 w-1.5 rounded-full bg-amber-400" /> Pending
        <span className="ml-2 h-1.5 w-1.5 rounded-full bg-rose-400" /> Failed
      </div>

      <div className="mt-5 border-t border-white/[0.06] pt-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-slate-200">Payments on {selectedDate.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</p>
            <p className="mt-0.5 text-[11px] text-slate-500">{selectedDate.toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric' })}</p>
          </div>
          <CalendarDays size={16} className="text-slate-500" />
        </div>
        {selectedPayments.length ? (
          <div className="space-y-2.5">
            {selectedPayments.map((payment) => (
              <div key={`${payment.customer}-${payment.amount}`} className="flex items-center justify-between gap-3 rounded-xl border border-white/[0.06] bg-[#0b111c] p-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-200">{payment.customer}</p>
                  <p className="mt-1 flex items-center gap-1.5 text-[11px] text-slate-500">
                    <CreditCard size={11} /> {payment.method}
                    <span className="text-slate-700">·</span>
                    <Clock3 size={11} /> {payment.status}
                  </p>
                </div>
                <p className="shrink-0 text-sm font-semibold text-white">{formatCurrency(payment.amount)}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-white/[0.09] px-4 py-5 text-center text-xs text-slate-500">
            No payments scheduled for this date.
          </div>
        )}
      </div>
    </section>
  )
}
