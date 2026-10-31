
import { useState } from 'react'
import {
  ArrowUpRight,
  CircleDollarSign,
  CreditCard,
  AlertTriangle,
  Wallet,
  TrendingUp,
  ChevronLeft,
  ChevronRight,
  CalendarDays,
  ArrowDownLeft,
  Clock,
} from 'lucide-react'

import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import StatCard from '../components/StatCard'
import { dashboardData } from '../mock/dashboardData'

const currencyFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})

const payments = {
  4: [{ name: 'Rahul Sharma', amount: 3000, method: 'UPI' }],
  9: [{ name: 'Ananya Thomas', amount: 4500, method: 'Card' }],
  14: [{ name: 'Arjun Nair', amount: 2500, method: 'UPI' }],
  20: [{ name: 'Meera Joseph', amount: 5000, method: 'Bank transfer' }],
  27: [{ name: 'Akhil Kumar', amount: 3500, method: 'Card' }],
}

const transactions = [
  { name: 'Rahul Sharma', id: '#INV-2041', amount: 3000, status: 'Paid', date: 'Today' },
  { name: 'Ananya Thomas', id: '#INV-2042', amount: 4500, status: 'Paid', date: 'Yesterday' },
  { name: 'Arjun Nair', id: '#INV-2043', amount: 2500, status: 'Pending', date: 'Oct 28' },
  { name: 'Meera Joseph', id: '#INV-2044', amount: 5000, status: 'Paid', date: 'Oct 27' },
]

const weeklyRevenue = [
  { day: 'Mon', amount: 4500 },
  { day: 'Tue', amount: 7000 },
  { day: 'Wed', amount: 5200 },
  { day: 'Thu', amount: 9000 },
  { day: 'Fri', amount: 6500 },
  { day: 'Sat', amount: 11000 },
  { day: 'Sun', amount: 8000 },
]

export default function Dashboard() {
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(new Date())

  const year = currentMonth.getFullYear()
  const month = currentMonth.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstDay = new Date(year, month, 1).getDay()

  const selectedPayments =
    selectedDate.getMonth() === month &&
    selectedDate.getFullYear() === year
      ? payments[selectedDate.getDate()] || []
      : []

  const changeMonth = (direction) => {
    setCurrentMonth(new Date(year, month + direction, 1))
  }

  const monthName = currentMonth.toLocaleDateString('en-IN', {
    month: 'long',
    year: 'numeric',
  })

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="flex min-h-screen">
        <Sidebar />

        <main className="min-w-0 flex-1">
          <Navbar />

          <div className="space-y-8 p-5 md:p-8">

            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium uppercase tracking-widest text-cyan-400">
                  Financial overview
                </p>
                <h1 className="mt-2 text-3xl font-bold">
                  Subscription Dashboard
                </h1>
                <p className="mt-2 text-sm text-slate-400">
                  Monitor your revenue and subscription performance.
                </p>
              </div>

              <div className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-300">
                <CalendarDays className="mr-2 inline" size={17} />
                {new Date().toLocaleDateString('en-IN', {
                  day: 'numeric',
                  month: 'short',
                  year: 'numeric',
                })}
              </div>
            </div>

            {/* Summary cards */}
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                title="Active subscriptions"
                value={dashboardData.activeSubscriptions}
                subtitle="Across all plans"
                tone="sky"
                icon={TrendingUp}
              />

              <StatCard
                title="Monthly recurring revenue"
                value={currencyFormatter.format(dashboardData.monthlyRecurringRevenue)}
                subtitle="This month"
                tone="emerald"
                icon={CircleDollarSign}
              />

              <StatCard
                title="Revenue collected"
                value={currencyFormatter.format(dashboardData.revenueCollectedThisMonth)}
                subtitle="Collected this month"
                tone="amber"
                icon={Wallet}
              />

              <StatCard
                title="Outstanding amount"
                value={currencyFormatter.format(dashboardData.outstandingAmount)}
                subtitle="Due for follow-up"
                tone="rose"
                icon={CreditCard}
              />
            </div>

            {/* Revenue chart */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-xl font-bold">Revenue analytics</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Weekly collection overview
                  </p>
                </div>
                <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-400">
                  <TrendingUp className="mr-1 inline" size={15} />
                  Revenue trend
                </span>
              </div>

              <div className="mt-8 flex h-52 items-end justify-between gap-3">
                {weeklyRevenue.map((item) => (
                  <div key={item.day} className="flex h-full flex-1 flex-col items-center justify-end gap-3">
                    <div className="text-xs text-slate-400">
                      ₹{(item.amount / 1000).toFixed(1)}k
                    </div>
                    <div
                      title={`${item.day}: ${currencyFormatter.format(item.amount)}`}
                      className="w-full max-w-12 rounded-t-lg bg-cyan-500 transition-all hover:bg-cyan-300"
                      style={{ height: `${(item.amount / 11000) * 65}%` }}
                    />
                    <span className="text-xs text-slate-400">{item.day}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Calendar and selected payments */}
            <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">

              <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold">Payment calendar</h2>
                    <p className="mt-1 text-sm text-slate-400">
                      Select a date to view payments
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => changeMonth(-1)}
                      className="rounded-lg border border-slate-700 p-2 hover:bg-slate-800"
                      aria-label="Previous month"
                    >
                      <ChevronLeft size={18} />
                    </button>
                    <span className="min-w-28 text-center text-sm font-semibold">
                      {monthName}
                    </span>
                    <button
                      onClick={() => changeMonth(1)}
                      className="rounded-lg border border-slate-700 p-2 hover:bg-slate-800"
                      aria-label="Next month"
                    >
                      <ChevronRight size={18} />
                    </button>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-7 gap-2 text-center">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                    <div key={day} className="py-2 text-xs text-slate-500">
                      {day}
                    </div>
                  ))}

                  {Array.from({ length: firstDay }).map((_, index) => (
                    <div key={`empty-${index}`} />
                  ))}

                  {Array.from({ length: daysInMonth }, (_, index) => index + 1).map((day) => {
                    const hasPayment = Boolean(payments[day])
                    const isSelected =
                      selectedDate.getDate() === day &&
                      selectedDate.getMonth() === month &&
                      selectedDate.getFullYear() === year

                    return (
                      <button
                        key={day}
                        onClick={() => setSelectedDate(new Date(year, month, day))}
                        className={`relative flex aspect-square items-center justify-center rounded-xl text-sm transition
                          ${isSelected
                            ? 'bg-cyan-500 font-bold text-slate-950'
                            : 'text-slate-300 hover:bg-slate-800'}
                        `}
                      >
                        {day}
                        {hasPayment && (
                          <span className={`absolute bottom-1 h-1 w-1 rounded-full ${isSelected ? 'bg-slate-950' : 'bg-emerald-400'}`} />
                        )}
                      </button>
                    )
                  })}
                </div>
                <p className="mt-4 text-xs text-slate-500">
                  <span className="mr-2 inline-block h-2 w-2 rounded-full bg-emerald-400" />
                  Payment recorded
                </p>
              </section>

              <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <h2 className="text-xl font-bold">Daily payments</h2>
                <p className="mt-1 text-sm text-slate-400">
                  {selectedDate.toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })}
                </p>

                {selectedPayments.length > 0 ? (
                  <div className="mt-6 space-y-4">
                    {selectedPayments.map((payment, index) => (
                      <div key={index} className="rounded-xl border border-slate-700 bg-slate-800 p-4">
                        <p className="font-semibold">{payment.name}</p>
                        <p className="mt-1 text-sm text-slate-400">{payment.method}</p>
                        <p className="mt-3 text-lg font-bold text-emerald-400">
                          {currencyFormatter.format(payment.amount)}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mt-8 rounded-xl border border-dashed border-slate-700 p-8 text-center">
                    <Clock className="mx-auto text-slate-500" size={28} />
                    <p className="mt-3 text-sm text-slate-400">
                      No demo payments recorded for this date.
                    </p>
                  </div>
                )}
              </section>
            </div>

            {/* Payment health */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-bold">Payment health</h2>
              <div className="mt-5 grid gap-4 sm:grid-cols-3">
                <div className="rounded-xl bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">Collected</p>
                  <p className="mt-2 text-xl font-bold text-emerald-400">
                    {currencyFormatter.format(dashboardData.revenueCollectedThisMonth)}
                  </p>
                </div>
                <div className="rounded-xl bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">Overdue</p>
                  <p className="mt-2 text-xl font-bold text-rose-400">
                    {currencyFormatter.format(dashboardData.overdueAmount)}
                  </p>
                </div>
                <div className="rounded-xl bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">Overdue invoices</p>
                  <p className="mt-2 text-xl font-bold">
                    {dashboardData.overdueInvoicesCount}
                  </p>
                </div>
              </div>
            </section>

            {/* Recent transactions */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold">Recent transactions</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Latest payment activity
                  </p>
                </div>
                <ArrowUpRight className="text-slate-400" />
              </div>

              <div className="mt-5 overflow-x-auto">
                <table className="w-full min-w-[550px] text-left text-sm">
                  <thead className="border-b border-slate-700 text-slate-500">
                    <tr>
                      <th className="pb-3">Customer</th>
                      <th className="pb-3">Invoice</th>
                      <th className="pb-3">Date</th>
                      <th className="pb-3">Amount</th>
                      <th className="pb-3">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((item) => (
                      <tr key={item.id} className="border-b border-slate-800">
                        <td className="py-4 font-medium">{item.name}</td>
                        <td className="py-4 text-slate-400">{item.id}</td>
                        <td className="py-4 text-slate-400">{item.date}</td>
                        <td className="py-4 font-semibold">
                          {currencyFormatter.format(item.amount)}
                        </td>
                        <td className="py-4">
                          <span className={`rounded-full px-3 py-1 text-xs ${
                            item.status === 'Paid'
                              ? 'bg-emerald-500/10 text-emerald-400'
                              : 'bg-amber-500/10 text-amber-400'
                          }`}>
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Overdue invoices */}
            <section className="rounded-2xl border border-rose-500/20 bg-rose-500/5 p-6">
              <div className="flex items-center gap-3">
                <AlertTriangle className="text-rose-400" size={22} />
                <div>
                  <h2 className="text-lg font-bold">Attention needed</h2>
                  <p className="text-sm text-slate-400">Overdue invoices need follow-up</p>
                </div>
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {[2041, 2045].map((invoice) => (
                  <div key={invoice} className="rounded-xl border border-slate-800 bg-slate-900 p-4">
                    <p className="text-sm text-slate-400">Invoice #{invoice}</p>
                    <p className="mt-2 font-bold text-rose-400">₹3,000</p>
                  </div>
                ))}
              </div>
            </section>

            <p className="text-center text-xs text-slate-500">
              Demo dashboard data. Live Odoo integration is not connected yet.
            </p>
          </div>
        </main>
      </div>
    </div>
  )
}
