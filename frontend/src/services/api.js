import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

function readAuth() {
  try {
    return JSON.parse(localStorage.getItem('isp-auth') || '{}')
  } catch {
    return {}
  }
}

function clearAuthAndRedirect() {
  localStorage.removeItem('isp-auth')
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

// Request interceptor - attach token
api.interceptors.request.use(
  (config) => {
    const token = readAuth()?.state?.token
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// Single in-flight refresh promise to avoid stampedes
let refreshPromise = null

async function refreshAccessToken() {
  const refresh = readAuth()?.state?.refreshToken
  if (!refresh) throw new Error('no refresh token')
  const baseURL = api.defaults.baseURL || '/api/v1'
  const res = await axios.post(`${baseURL}/auth/refresh/`, { refresh })
  const newToken = res.data.access
  const stored = readAuth()
  if (stored.state) {
    stored.state.token = newToken
    if (res.data.refresh) stored.state.refreshToken = res.data.refresh
    localStorage.setItem('isp-auth', JSON.stringify(stored))
  }
  return newToken
}

// Response interceptor - auto refresh token on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        if (!refreshPromise) refreshPromise = refreshAccessToken()
        const newToken = await refreshPromise
        refreshPromise = null
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      } catch (_) {
        refreshPromise = null
        clearAuthAndRedirect()
      }
    }
    return Promise.reject(error)
  }
)

export default api

// ── Customers API ──
export const customersAPI = {
  list:   (params) => api.get('/customers/', { params }),
  get:    (id)     => api.get(`/customers/${id}/`),
  create: (data)   => api.post('/customers/', data),
  update: (id, data) => api.patch(`/customers/${id}/`, data),
  delete: (id)     => api.delete(`/customers/${id}/`),
  stats:  ()       => api.get('/customers/stats/'),
  suspend:(id)     => api.post(`/customers/${id}/suspend/`),
  activate:(id)    => api.post(`/customers/${id}/activate/`),
  billingHistory: (id) => api.get(`/customers/${id}/billing_history/`),
  paymentHistory: (id) => api.get(`/customers/${id}/payment_history/`),
  addNote:(id, data) => api.post(`/customers/${id}/add_note/`, data),
  zones:  (params) => api.get('/customers/zones/', { params }),
}

// ── Billing API ──
export const billingAPI = {
  list:     (params) => api.get('/billing/invoices/', { params }),
  get:      (id)     => api.get(`/billing/invoices/${id}/`),
  create:   (data)   => api.post('/billing/invoices/', data),
  update:   (id, d)  => api.patch(`/billing/invoices/${id}/`, d),
  summary:  ()       => api.get('/billing/invoices/summary/'),
  waive:    (id, d)  => api.post(`/billing/invoices/${id}/waive/`, d),
  remind:   (id)     => api.post(`/billing/invoices/${id}/send_reminder/`),
  runBilling:()      => api.post('/billing/invoices/run_billing/'),
  discounts:(params) => api.get('/billing/discounts/', { params }),
}

// ── Payments API ──
export const paymentsAPI = {
  list:    (params) => api.get('/payments/', { params }),
  create:  (data)   => api.post('/payments/', data),
  daily:   ()       => api.get('/payments/daily_summary/'),
  monthly: ()       => api.get('/payments/monthly_summary/'),
  refund:  (id, d)  => api.post(`/payments/${id}/refund/`, d),
}

// ── Packages API ──
export const packagesAPI = {
  list:   (params) => api.get('/packages/', { params }),
  get:    (id)     => api.get(`/packages/${id}/`),
  create: (data)   => api.post('/packages/', data),
  update: (id, d)  => api.patch(`/packages/${id}/`, d),
  delete: (id)     => api.delete(`/packages/${id}/`),
}

// ── Network API ──
export const networkAPI = {
  devices:  (params) => api.get('/network/devices/', { params }),
  sessions: (params) => api.get('/network/sessions/', { params }),
  alerts:   (params) => api.get('/network/alerts/', { params }),
  resolveAlert: (id) => api.post(`/network/alerts/${id}/resolve/`),
  ipPools:  (params) => api.get('/network/ip-pools/', { params }),
  pingDevice:(id)    => api.post(`/network/devices/${id}/ping/`),
}

// ── Support API ──
export const supportAPI = {
  list:       (params) => api.get('/support/tickets/', { params }),
  get:        (id)     => api.get(`/support/tickets/${id}/`),
  create:     (data)   => api.post('/support/tickets/', data),
  update:     (id, d)  => api.patch(`/support/tickets/${id}/`, d),
  stats:      ()       => api.get('/support/tickets/stats/'),
  addComment: (id, d)  => api.post(`/support/tickets/${id}/add_comment/`, d),
  resolve:    (id, d)  => api.post(`/support/tickets/${id}/resolve/`, d),
}

// ── Reports API ──
export const reportsAPI = {
  revenue:   (params) => api.get('/reports/revenue/', { params }),
  customers: (params) => api.get('/reports/customers/', { params }),
  network:   (params) => api.get('/reports/network/', { params }),
}
