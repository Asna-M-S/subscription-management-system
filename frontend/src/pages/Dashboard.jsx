import {
  ArrowUpRight,
  CircleDollarSign,
  CreditCard,
  AlertTriangle,
  Wallet,
  TrendingUp,
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

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar />

        <main className="flex-1">
          <Navbar />

          <div className="p-6 lg:p-8">
            <div className="mb-8 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.2em] text-sky-600">
                  Overview
                </p>
                <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                  Subscription dashboard
                </h1>
              </div>

              <button
                type="button"
                className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-slate-800"
              >
                <ArrowUpRight size={16} />
                Export report
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
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

            <div className="mt-8 grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-500">Collections</p>
                    <h2 className="mt-2 text-xl font-bold text-slate-900">Payment health</h2>
                  </div>
                  <div className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
                    +18.2%
                  </div>
                </div>

                <div className="mt-6 grid gap-4 sm:grid-cols-3">
                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-sm text-slate-500">Collected</p>
                    <p className="mt-2 text-2xl font-bold text-slate-900">
                      {currencyFormatter.format(dashboardData.revenueCollectedThisMonth)}
                    </p>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-sm text-slate-500">Overdue</p>
                    <p className="mt-2 text-2xl font-bold text-slate-900">
                      {currencyFormatter.format(dashboardData.overdueAmount)}
                    </p>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-sm text-slate-500">Invoices</p>
                    <p className="mt-2 text-2xl font-bold text-slate-900">
                      {dashboardData.overdueInvoicesCount}
                    </p>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-amber-100 p-2 text-amber-700">
                    <AlertTriangle size={20} />
                  </div>
                  <div>
                    <p className="text-sm text-amber-700">Attention needed</p>
                    <h2 className="text-xl font-bold text-slate-900">Overdue invoices</h2>
                  </div>
                </div>

                <div className="mt-6 space-y-3">
                  <div className="rounded-xl bg-white p-3">
                    <p className="text-sm text-slate-500">Invoice #2041</p>
                    <p className="mt-1 font-semibold text-slate-900">₹3,000</p>
                  </div>
                  <div className="rounded-xl bg-white p-3">
                    <p className="text-sm text-slate-500">Invoice #2045</p>
                    <p className="mt-1 font-semibold text-slate-900">₹3,000</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
