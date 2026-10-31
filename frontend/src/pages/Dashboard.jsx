import { Suspense, lazy, useEffect, useMemo, useState } from 'react'
import {
  BadgeIndianRupee,
  CircleDollarSign,
  CreditCard,
  Download,
  FileClock,
  ReceiptText,
  ShieldCheck,
  Wallet,
} from 'lucide-react'
import Navbar from '../components/Navbar'
import PaymentCalendar from '../components/PaymentCalendar'
import Sidebar from '../components/Sidebar'
import StatCard from '../components/StatCard'
import { dashboardMockPayload } from '../mock/dashboardData'
import { fetchDashboardOverview } from '../services/dashboardApi'
import { formatCurrency } from '../services/formatters'

const RevenueChart = lazy(() => import('../components/RevenueChart'))
const dashboardEndpoint = import.meta.env.VITE_DASHBOARD_API_URL

const statusStyles = {
  Paid: 'bg-emerald-400/10 text-emerald-300 ring-emerald-400/20',
  Pending: 'bg-amber-400/10 text-amber-200 ring-amber-400/20',
  Failed: 'bg-rose-400/10 text-rose-300 ring-rose-400/20',
  Overdue: 'bg-rose-400/10 text-rose-300 ring-rose-400/20',
}

function SectionHeading({ eyebrow, title, action }) {
  return (
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div>
        {eyebrow && <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">{eyebrow}</p>}
        <h2 className="text-lg font-semibold tracking-tight text-white sm:text-xl">{title}</h2>
      </div>
      {action}
    </div>
  )
}

function PaymentHealth({ summary, successRate }) {
  const paymentHealth = [
    {
      label: 'Total collected',
      value: summary.revenueCollectedThisMonth,
      progress: 82,
      icon: Wallet,
      color: 'bg-emerald-400',
      text: 'text-emerald-300',
    },
    {
      label: 'Pending payments',
      value: summary.pendingAmount,
      progress: 12,
      icon: FileClock,
      color: 'bg-amber-400',
      text: 'text-amber-300',
    },
    {
      label: 'Overdue payments',
      value: summary.overdueAmount,
      progress: 6,
      icon: ReceiptText,
      color: 'bg-rose-400',
      text: 'text-rose-300',
    },
  ]

  return (
    <section className="panel p-5 sm:p-6">
      <SectionHeading eyebrow="Collections" title="Payment health" />
      <div className="space-y-5">
        {paymentHealth.map(({ label, value, progress, icon: Icon, color, text }) => (
          <div key={label}>
            <div className="mb-2 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2.5 text-sm text-slate-300">
                <Icon size={16} className={text} />
                {label}
              </div>
              <span className="text-sm font-semibold text-white">{formatCurrency(value)}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
              <div className={`h-full rounded-full ${color}`} style={{ width: `${progress}%` }} />
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 flex items-center justify-between rounded-xl border border-emerald-400/10 bg-emerald-400/[0.06] p-4">
        <div>
          <p className="text-xs text-slate-400">Collection success rate</p>
          <p className="mt-1 text-2xl font-semibold text-white">{successRate.toFixed(1)}%</p>
        </div>
        <div className="grid h-11 w-11 place-items-center rounded-full border-[3px] border-emerald-400/80 text-emerald-300">
          <ShieldCheck size={19} />
        </div>
      </div>
    </section>
  )
}

function TransactionsTable({ transactions: rows }) {
  return (
    <section className="panel overflow-hidden">
      <div className="px-5 pt-5 sm:px-6 sm:pt-6">
        <SectionHeading
          eyebrow="Latest activity"
          title="Recent transactions"
          action={
            <button type="button" className="text-sm font-medium text-cyan-300 transition hover:text-cyan-200">
              View all
            </button>
          }
        />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[780px] text-left text-sm">
          <thead>
            <tr className="border-y border-white/[0.06] bg-white/[0.015] text-[11px] uppercase tracking-[0.12em] text-slate-500">
              <th className="px-6 py-3 font-medium">Customer</th>
              <th className="px-4 py-3 font-medium">Invoice</th>
              <th className="px-4 py-3 font-medium">Payment date</th>
              <th className="px-4 py-3 font-medium">Amount</th>
              <th className="px-4 py-3 font-medium">Method</th>
              <th className="px-6 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((item) => (
              <tr key={item.id} className="border-b border-white/[0.045] transition hover:bg-white/[0.025] last:border-0">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-slate-800 text-xs font-semibold text-slate-300">
                      {item.name.split(' ').map((part) => part[0]).join('')}
                    </span>
                    <span className="font-medium text-slate-200">{item.name}</span>
                  </div>
                </td>
                <td className="px-4 py-4 font-mono text-xs text-slate-400">{item.id}</td>
                <td className="px-4 py-4 text-slate-400">{item.date}</td>
                <td className="px-4 py-4 font-medium text-white">{formatCurrency(item.amount)}</td>
                <td className="px-4 py-4 text-slate-400">{item.method}</td>
                <td className="px-6 py-4">
                  <span className={`rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${statusStyles[item.status]}`}>
                    {item.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function OverdueInvoices({ invoices }) {
  return (
    <section className="panel p-5 sm:p-6">
      <SectionHeading
        eyebrow="Needs attention"
        title="Overdue invoices"
        action={<span className="rounded-full bg-rose-400/10 px-2.5 py-1 text-xs font-medium text-rose-300">{invoices.length} overdue</span>}
      />
      <div className="space-y-3">
        {invoices.map((invoice) => (
          <div key={invoice.id} className="rounded-xl border border-rose-400/10 bg-rose-400/[0.035] p-4 transition hover:border-rose-400/20">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-xs text-slate-400">{invoice.id}</p>
                <p className="mt-1.5 text-sm font-medium text-slate-200">{invoice.customer}</p>
              </div>
              <span className="rounded-full bg-rose-400/10 px-2 py-1 text-[10px] font-medium text-rose-300">{invoice.daysOverdue} days late</span>
            </div>
            <div className="mt-4 flex items-end justify-between">
              <div>
                <p className="text-[11px] text-slate-500">Due {invoice.dueDate}</p>
                <p className="mt-1 text-lg font-semibold text-rose-200">{formatCurrency(invoice.amount)}</p>
              </div>
              <button type="button" className="rounded-lg border border-white/[0.08] px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-rose-300/30 hover:text-white">
                Remind
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default function Dashboard() {
  const [query, setQuery] = useState('')
  const [dashboard, setDashboard] = useState(dashboardMockPayload)
  const [usingSampleData, setUsingSampleData] = useState(true)
  const [apiError, setApiError] = useState('')

  useEffect(() => {
    if (!dashboardEndpoint) return undefined

    const controller = new AbortController()
    fetchDashboardOverview(dashboardEndpoint, controller.signal)
      .then((payload) => {
        setDashboard(payload)
        setUsingSampleData(false)
        setApiError('')
      })
      .catch((error) => {
        if (controller.signal.aborted) return
        setUsingSampleData(true)
        setApiError(error instanceof Error ? error.message : 'The dashboard API request failed.')
      })

    return () => controller.abort()
  }, [])

  const visibleTransactions = useMemo(() => {
    const search = query.trim().toLowerCase()
    if (!search) return dashboard.transactions
    return dashboard.transactions.filter((item) =>
      [item.name, item.id, item.status, item.method].some((value) => value.toLowerCase().includes(search)),
    )
  }, [dashboard.transactions, query])
  const summary = dashboard.summary

  const cards = [
    { title: 'Active subscriptions', value: summary.activeSubscriptions.toLocaleString('en-IN'), change: '+12.8%', description: 'vs. last month', icon: CreditCard, accent: 'blue', trend: 'up' },
    { title: 'Monthly recurring revenue', value: formatCurrency(summary.monthlyRecurringRevenue), change: '+8.4%', description: 'vs. last month', icon: CircleDollarSign, accent: 'cyan', trend: 'up' },
    { title: 'Revenue collected', value: formatCurrency(summary.revenueCollectedThisMonth), change: '+16.2%', description: 'vs. last month', icon: BadgeIndianRupee, accent: 'green', trend: 'up' },
    { title: 'Outstanding amount', value: formatCurrency(summary.outstandingAmount), change: '-4.6%', description: 'vs. last month', icon: Wallet, accent: 'violet', trend: 'down' },
  ]

  return (
    <div className="min-h-screen bg-[#080b14] text-slate-100">
      <Sidebar />
      <div className="min-h-screen lg:pl-[258px]">
        <Navbar query={query} onQueryChange={setQuery} />
        <main className="mx-auto max-w-[1600px] space-y-7 px-4 pb-10 pt-7 sm:px-6 lg:px-9 lg:pt-9">
          <section id="overview" className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-cyan-300/80">BrightLoop / Overview</p>
              <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-[30px]">Financial Overview</h1>
              <p className="mt-2 text-sm text-slate-400">Track revenue, subscriptions and payment activity.</p>
            </div>
            <button type="button" className="inline-flex items-center gap-2 rounded-xl border border-white/[0.09] bg-[#111827] px-4 py-2.5 text-sm font-medium text-slate-200 shadow-lg shadow-black/10 transition hover:border-cyan-400/30 hover:bg-slate-800">
              <Download size={16} className="text-cyan-300" />
              Export report
            </button>
          </section>

          {apiError && (
            <div role="alert" className="rounded-xl border border-amber-400/20 bg-amber-400/[0.06] px-4 py-3 text-sm text-amber-200">
              Could not load live dashboard data. Showing sample data instead. <span className="text-amber-100/70">{apiError}</span>
            </div>
          )}

          <section aria-label="Financial summary" className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
            {cards.map((card) => <StatCard key={card.title} {...card} />)}
          </section>

          <div className="grid gap-5 2xl:grid-cols-[minmax(0,1.65fr)_minmax(330px,0.85fr)]">
            <Suspense fallback={<div className="panel h-[390px] animate-pulse bg-slate-900" aria-label="Loading revenue chart" />}>
              <RevenueChart seriesData={dashboard.revenueSeries} />
            </Suspense>
            <PaymentHealth summary={summary} successRate={dashboard.collectionSuccessRate} />
          </div>

          <div className="grid gap-5 2xl:grid-cols-[minmax(0,1.25fr)_minmax(360px,0.75fr)]">
            <PaymentCalendar payments={dashboard.calendarPayments} />
            <OverdueInvoices invoices={dashboard.overdueInvoices} />
          </div>

          <TransactionsTable transactions={visibleTransactions} />
          <p className="text-center text-xs text-slate-600">
            {usingSampleData ? 'Showing sample data. Set VITE_DASHBOARD_API_URL to connect your Django REST API.' : 'Live dashboard data connected.'}
          </p>
        </main>
      </div>
    </div>
  )
}
