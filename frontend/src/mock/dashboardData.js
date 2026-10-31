export const dashboardData = {
  currency: 'INR',
  activeSubscriptions: 1248,
  monthlyRecurringRevenue: 1842500,
  revenueCollectedThisMonth: 1624800,
  outstandingAmount: 217700,
  overdueAmount: 68400,
  overdueInvoicesCount: 8,
  pendingAmount: 8400,
}

export const transactions = [
  { name: 'Aarav Mehta', id: 'INV-2084', amount: 2499, method: 'UPI', status: 'Paid', date: 'Today, 10:42 AM' },
  { name: 'Priya Iyer', id: 'INV-2083', amount: 12999, method: 'Visa ···· 4242', status: 'Paid', date: 'Today, 9:18 AM' },
  { name: 'Kabir Khanna', id: 'INV-2082', amount: 5499, method: 'Net banking', status: 'Pending', date: 'Yesterday' },
  { name: 'Ananya Rao', id: 'INV-2081', amount: 7999, method: 'Mastercard ···· 8031', status: 'Failed', date: 'Yesterday' },
  { name: 'Ishaan Kapoor', id: 'INV-2080', amount: 3499, method: 'UPI', status: 'Paid', date: '28 Oct 2026' },
]

export const overdueInvoices = [
  { id: 'INV-2041', customer: 'Nisha Patel', dueDate: '24 Oct 2026', amount: 18400, daysOverdue: 7 },
  { id: 'INV-2038', customer: 'Dev Malhotra', dueDate: '19 Oct 2026', amount: 12500, daysOverdue: 12 },
  { id: 'INV-2032', customer: 'Tara Menon', dueDate: '12 Oct 2026', amount: 9750, daysOverdue: 19 },
]

const currentDate = new Date()
const paymentDateKey = (day) => {
  const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

export const calendarPayments = {
  [paymentDateKey(4)]: [
    { customer: 'Rahul Sharma', amount: 3000, method: 'UPI', status: 'Paid' },
    { customer: 'Mira Shah', amount: 6400, method: 'Visa ···· 2284', status: 'Paid' },
  ],
  [paymentDateKey(9)]: [
    { customer: 'Ananya Thomas', amount: 4500, method: 'Mastercard ···· 4021', status: 'Paid' },
  ],
  [paymentDateKey(14)]: [
    { customer: 'Arjun Nair', amount: 2500, method: 'UPI', status: 'Pending' },
    { customer: 'Zoya Khan', amount: 8200, method: 'Net banking', status: 'Failed' },
  ],
  [paymentDateKey(20)]: [
    { customer: 'Meera Joseph', amount: 5000, method: 'UPI', status: 'Paid' },
  ],
  [paymentDateKey(27)]: [
    { customer: 'Akhil Kumar', amount: 3500, method: 'Visa ···· 3910', status: 'Paid' },
    { customer: 'Rhea Bose', amount: 12900, method: 'Net banking', status: 'Pending' },
  ],
}

export const revenueSeries = {
  Weekly: [
    { label: 'Mon', revenue: 48000 }, { label: 'Tue', revenue: 72000 },
    { label: 'Wed', revenue: 61000 }, { label: 'Thu', revenue: 96000 },
    { label: 'Fri', revenue: 79000 }, { label: 'Sat', revenue: 124000 },
    { label: 'Sun', revenue: 108000 },
  ],
  Monthly: [
    { label: '1 Oct', revenue: 168000 }, { label: '4 Oct', revenue: 194000 },
    { label: '7 Oct', revenue: 182000 }, { label: '10 Oct', revenue: 248000 },
    { label: '13 Oct', revenue: 224000 }, { label: '16 Oct', revenue: 302000 },
    { label: '19 Oct', revenue: 276000 }, { label: '22 Oct', revenue: 348000 },
    { label: '25 Oct', revenue: 318000 }, { label: '28 Oct', revenue: 412000 },
    { label: '31 Oct', revenue: 384000 },
  ],
  Yearly: [
    { label: 'Jan', revenue: 185000 }, { label: 'Feb', revenue: 214000 },
    { label: 'Mar', revenue: 198000 }, { label: 'Apr', revenue: 264000 },
    { label: 'May', revenue: 248000 }, { label: 'Jun', revenue: 310000 },
    { label: 'Jul', revenue: 296000 }, { label: 'Aug', revenue: 352000 },
    { label: 'Sep', revenue: 326000 }, { label: 'Oct', revenue: 384000 },
    { label: 'Nov', revenue: 361000 }, { label: 'Dec', revenue: 428000 },
  ],
}

export const dashboardMockPayload = {
  summary: dashboardData,
  transactions,
  overdueInvoices,
  calendarPayments,
  revenueSeries,
  collectionSuccessRate: 94.8,
}
