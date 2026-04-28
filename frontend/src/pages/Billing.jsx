import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { billingAPI } from '../services/api'
import { toast } from 'react-toastify'

const STATUS_STYLE = {
  pending:   { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
  paid:      { color: '#22c55e', bg: 'rgba(34,197,94,0.1)' },
  overdue:   { color: '#ef4444', bg: 'rgba(239,68,68,0.1)' },
  partial:   { color: '#3b82f6', bg: 'rgba(59,130,246,0.1)' },
  cancelled: { color: '#64748b', bg: 'rgba(100,116,139,0.1)' },
  waived:    { color: '#a78bfa', bg: 'rgba(167,139,250,0.1)' },
}

function InvoiceBadge({ status }) {
  const s = STATUS_STYLE[status] || STATUS_STYLE.pending
  return (
    <span style={{ color: s.color, background: s.bg, borderRadius: 6, padding: '3px 10px', fontSize: 12, fontWeight: 600 }}>
      {status}
    </span>
  )
}

export default function Billing() {
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['invoices', statusFilter, search, page],
    queryFn: () => billingAPI.list({ status: statusFilter, search, page, page_size: 25 }),
  })

  const { data: summary } = useQuery({
    queryKey: ['invoice-summary'],
    queryFn: () => billingAPI.summary(),
  })

  const runBilling = useMutation({
    mutationFn: billingAPI.runBilling,
    onSuccess: () => toast.success('বিলিং প্রক্রিয়া শুরু হয়েছে!'),
  })

  const invoices = data?.data?.results || []
  const total    = data?.data?.count   || 0
  const sm       = summary?.data       || {}

  const s = {
    page: { background: '#0f0e1a', minHeight: '100vh', padding: 24, fontFamily: "'Outfit', sans-serif", color: '#f1f5f9' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
    title: { fontSize: 22, fontWeight: 700, margin: 0 },
    btnRow: { display: 'flex', gap: 10 },
    btn: (color) => ({
      background: color || 'rgba(99,102,241,0.15)',
      border: '1px solid rgba(99,102,241,0.3)',
      borderRadius: 10, padding: '10px 18px',
      color: 'white', fontWeight: 600, cursor: 'pointer', fontSize: 13,
      fontFamily: 'inherit',
    }),
    statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 24 },
    statCard: {
      background: 'rgba(19,17,42,0.9)', border: '1px solid rgba(99,102,241,0.15)',
      borderRadius: 12, padding: '18px 20px',
    },
    filters: {
      display: 'flex', gap: 12, marginBottom: 20,
      background: 'rgba(19,17,42,0.9)', padding: 16,
      borderRadius: 12, border: '1px solid rgba(99,102,241,0.15)',
    },
    input: {
      background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)',
      borderRadius: 8, padding: '8px 12px', color: '#f1f5f9', fontSize: 13,
      outline: 'none', fontFamily: 'inherit', flex: 1,
    },
    select: {
      background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)',
      borderRadius: 8, padding: '8px 12px', color: '#f1f5f9', fontSize: 13,
      outline: 'none', fontFamily: 'inherit',
    },
    tableWrap: {
      background: 'rgba(19,17,42,0.9)', border: '1px solid rgba(99,102,241,0.15)',
      borderRadius: 12, overflow: 'hidden',
    },
    table: { width: '100%', borderCollapse: 'collapse' },
    th: { color: '#64748b', fontSize: 12, fontWeight: 600, textAlign: 'left', padding: '12px 16px', borderBottom: '1px solid rgba(99,102,241,0.15)', textTransform: 'uppercase' },
    td: { padding: '14px 16px', borderBottom: '1px solid rgba(99,102,241,0.08)', fontSize: 13, color: '#cbd5e1' },
  }

  const STATS = [
    { label: 'মোট বিল', value: `৳${(sm.total_billed||0).toLocaleString()}`, icon: '📋', color: '#6366f1' },
    { label: 'সংগ্রহ হয়েছে', value: `৳${(sm.total_collected||0).toLocaleString()}`, icon: '💰', color: '#22c55e' },
    { label: 'বকেয়া', value: `৳${(sm.total_outstanding||0).toLocaleString()}`, icon: '⚠️', color: '#ef4444' },
    { label: 'মেয়াদ পেরিয়েছে', value: sm.overdue || 0, icon: '🔴', color: '#f59e0b' },
  ]

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>📋 বিলিং ব্যবস্থাপনা</h1>
        <div style={s.btnRow}>
          <button style={s.btn('rgba(34,197,94,0.2)')} onClick={() => runBilling.mutate()}>
            ⚡ মাসিক বিল তৈরি করুন
          </button>
          <button style={s.btn('linear-gradient(135deg, #6366f1, #8b5cf6)')}>
            ＋ নতুন ইনভয়েস
          </button>
        </div>
      </div>

      <div style={s.statsGrid}>
        {STATS.map(item => (
          <div key={item.label} style={s.statCard}>
            <div style={{ fontSize: 22, marginBottom: 6 }}>{item.icon}</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: item.color }}>{item.value}</div>
            <div style={{ color: '#64748b', fontSize: 12 }}>{item.label}</div>
          </div>
        ))}
      </div>

      <div style={s.filters}>
        <input style={s.input} placeholder="🔍 ইনভয়েস নম্বর বা গ্রাহক খুঁজুন..."
          value={search} onChange={e => setSearch(e.target.value)} />
        <select style={s.select} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">সকল স্ট্যাটাস</option>
          <option value="pending">মুলতুবি</option>
          <option value="paid">পরিশোধিত</option>
          <option value="overdue">মেয়াদ পেরিয়েছে</option>
          <option value="partial">আংশিক</option>
          <option value="cancelled">বাতিল</option>
        </select>
      </div>

      <div style={s.tableWrap}>
        {isLoading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#6366f1' }}>⏳ লোড হচ্ছে...</div>
        ) : (
          <table style={s.table}>
            <thead>
              <tr>
                {['ইনভয়েস নং', 'গ্রাহক', 'ধরন', 'মোট', 'পরিশোধ', 'বাকি', 'নির্ধারিত তারিখ', 'স্ট্যাটাস', ''].map(h => (
                  <th key={h} style={s.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr><td colSpan={9} style={{ ...s.td, textAlign: 'center', color: '#64748b', padding: 40 }}>
                  কোনো ইনভয়েস পাওয়া যায়নি
                </td></tr>
              ) : invoices.map(inv => (
                <tr key={inv.id}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(99,102,241,0.05)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}>
                  <td style={{ ...s.td, color: '#6366f1', fontFamily: 'monospace', fontWeight: 600 }}>{inv.invoice_number}</td>
                  <td style={{ ...s.td, color: '#e2e8f0' }}>{inv.customer_name}<br/>
                    <span style={{ color: '#64748b', fontSize: 11 }}>{inv.customer_id}</span></td>
                  <td style={s.td}>{inv.invoice_type}</td>
                  <td style={{ ...s.td, fontWeight: 600, color: '#e2e8f0' }}>৳{parseFloat(inv.total).toLocaleString()}</td>
                  <td style={{ ...s.td, color: '#22c55e' }}>৳{parseFloat(inv.amount_paid).toLocaleString()}</td>
                  <td style={{ ...s.td, color: parseFloat(inv.balance_due) > 0 ? '#ef4444' : '#22c55e' }}>
                    ৳{parseFloat(inv.balance_due).toLocaleString()}</td>
                  <td style={{ ...s.td, color: '#f59e0b' }}>
                    {inv.due_date ? new Date(inv.due_date).toLocaleDateString('bn-BD') : '—'}</td>
                  <td style={s.td}><InvoiceBadge status={inv.status} /></td>
                  <td style={s.td}>
                    <button style={{
                      background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.2)',
                      borderRadius: 6, padding: '4px 10px', color: '#22c55e', cursor: 'pointer', fontSize: 12,
                    }}>💳 পেমেন্ট</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 }}>
        <span style={{ color: '#64748b', fontSize: 13 }}>মোট {total} টি ইনভয়েস</span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, padding: '8px 16px', color: '#94a3b8', cursor: 'pointer', fontSize: 13 }}
            onClick={() => setPage(p => Math.max(1, p-1))} disabled={page===1}>← আগে</button>
          <span style={{ color: '#94a3b8', padding: '8px 12px', fontSize: 13 }}>{page}</span>
          <button style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, padding: '8px 16px', color: '#94a3b8', cursor: 'pointer', fontSize: 13 }}
            onClick={() => setPage(p => p+1)} disabled={invoices.length < 25}>পরে →</button>
        </div>
      </div>
    </div>
  )
}
