const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

async function getJson(path, signal) {
  if (!API_BASE_URL) {
    throw new Error('VITE_API_BASE_URL is missing from frontend/.env.local')
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { signal })

  if (!response.ok) {
    throw new Error(`Dashboard API request failed (${response.status})`)
  }

  return response.json()
}

const money = (value) => Number(value ?? 0)

export async function fetchDashboardOverview(_endpoint, signal) {
  const [summary, overdue, payments] = await Promise.all([
    getJson('/dashboard-api/summary', signal),
    getJson('/dashboard-api/invoices/overdue?page=1&limit=20', signal),
    getJson('/dashboard-api/payments?page=1&limit=100', signal),
  ])

  const transactions = (payments.items ?? []).map((payment) => ({
    id: String(payment.invoiceNumber ?? payment.invoiceId ?? payment.id),
    name: payment.customerName ?? 'Customer',
    date: payment.paidAt ?? '',
    amount: money(payment.amount),
    method: payment.method ?? '—',
    status: payment.status ?? 'Paid',
  }))

  const overdueInvoices = (overdue.items ?? []).map((invoice) => ({
    id: String(invoice.number ?? invoice.id),
    customer: invoice.customerName ?? 'Customer',
    dueDate: invoice.dueDate ?? '',
    amount: money(invoice.balanceDue),
    daysOverdue: invoice.dueDate
      ? Math.max(0, Math.floor((Date.now() - new Date(invoice.dueDate).getTime()) / 86400000))
      : 0,
  }))

  const calendarPayments = {}
  for (const payment of payments.items ?? []) {
    const date = payment.paidAt?.slice(0, 10)
    if (!date) continue

    calendarPayments[date] ??= []
    calendarPayments[date].push({
      customer: payment.customerName ?? 'Customer',
      method: payment.method ?? '—',
      status: payment.status ?? 'Paid',
      amount: money(payment.amount),
    })
  }

  return {
    summary: {
      ...summary,
      pendingAmount: 0,
    },
    transactions,
    overdueInvoices,
    calendarPayments,
    revenueSeries: { Weekly: [], Monthly: [], Yearly: [] },
    collectionSuccessRate: 0,
  }
}