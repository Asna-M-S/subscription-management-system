import axios from 'axios'

const isRecord = (value) => value !== null && typeof value === 'object' && !Array.isArray(value)

function assertDashboardPayload(payload) {
  const requiredSummaryValues = [
    'activeSubscriptions',
    'monthlyRecurringRevenue',
    'revenueCollectedThisMonth',
    'outstandingAmount',
    'pendingAmount',
    'overdueAmount',
    'overdueInvoicesCount',
  ]

  if (!isRecord(payload) || !isRecord(payload.summary)) {
    throw new Error('Dashboard API response must include a summary object.')
  }
  if (requiredSummaryValues.some((key) => !Number.isFinite(payload.summary[key]))) {
    throw new Error('Dashboard API summary is missing one or more numeric financial fields.')
  }
  if (!Array.isArray(payload.transactions) || !Array.isArray(payload.overdueInvoices)) {
    throw new Error('Dashboard API response must include transactions and overdueInvoices arrays.')
  }
  if (payload.transactions.some((item) =>
    !isRecord(item) ||
    !['name', 'id', 'date', 'method', 'status'].every((key) => typeof item[key] === 'string') ||
    !Number.isFinite(item.amount),
  )) {
    throw new Error('Dashboard API transactions contain an invalid record.')
  }
  if (payload.overdueInvoices.some((item) =>
    !isRecord(item) ||
    !['id', 'customer', 'dueDate'].every((key) => typeof item[key] === 'string') ||
    !Number.isFinite(item.amount) ||
    !Number.isFinite(item.daysOverdue),
  )) {
    throw new Error('Dashboard API overdueInvoices contain an invalid record.')
  }
  if (!isRecord(payload.calendarPayments)) {
    throw new Error('Dashboard API response must include a calendarPayments object keyed by YYYY-MM-DD.')
  }
  if (Object.entries(payload.calendarPayments).some(([date, items]) =>
    !/^\d{4}-\d{2}-\d{2}$/.test(date) ||
    !Array.isArray(items) ||
    items.some((item) =>
      !isRecord(item) ||
      !['customer', 'method', 'status'].every((key) => typeof item[key] === 'string') ||
      !Number.isFinite(item.amount),
    ),
  )) {
    throw new Error('Dashboard API calendarPayments must contain valid payment records keyed by YYYY-MM-DD.')
  }
  if (!isRecord(payload.revenueSeries) || ['Weekly', 'Monthly', 'Yearly'].some((period) =>
    !Array.isArray(payload.revenueSeries[period]) ||
    payload.revenueSeries[period].some((point) =>
      !isRecord(point) || typeof point.label !== 'string' || !Number.isFinite(point.revenue),
    ),
  )) {
    throw new Error('Dashboard API response must include valid Weekly, Monthly, and Yearly revenueSeries.')
  }
  if (!Number.isFinite(payload.collectionSuccessRate) || payload.collectionSuccessRate < 0 || payload.collectionSuccessRate > 100) {
    throw new Error('Dashboard API response must include a collectionSuccessRate between 0 and 100.')
  }

  return payload
}

export async function fetchDashboardOverview(endpoint, signal) {
  const response = await axios.get(endpoint, { signal })
  return assertDashboardPayload(response.data)
}
