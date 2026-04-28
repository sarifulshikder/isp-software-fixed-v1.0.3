import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { customersAPI } from '../services/api'
import { toast } from 'react-toastify'

const STATUS_COLORS = {
  active:     '#22c55e', inactive: '#94a3b8',
  suspended:  '#f59e0b', terminated: '#ef4444', pending: '#6366f1',
}

const STATUS_BG = {
  active:     'rgba(34,197,94,0.1)',    inactive: 'rgba(148,163,184,0.1)',
  suspended:  'rgba(245,158,11,0.1)',   terminated: 'rgba(239,68,68,0.1)',
  pending:    'rgba(99,102,241,0.1)',
}

function StatusBadge({ status }) {
  return (
    <span style={{
      color: STATUS_COLORS[status] || '#94a3b8',
      background: STATUS_BG[status] || 'rgba(148,163,184,0.1)',
      borderRadius: 6, padding: '3px 10px', fontSize: 12, fontWeight: 600,
    }}>
      {status === 'active' ? '✅' : status === 'suspended' ? '⛔' : status === 'pending' ? '⏳' : '❌'} {status}
    </span>
  )
}

export default function Customers() {
  const navigate = useNavigate()
  const [search, setSearch]   = useState('')
  const [status, setStatus]   = useState('')
  const [page, setPage]       = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['customers', search, status, page],
    queryFn: () => customersAPI.list({ search, status, page, page_size: 20 }),
  })

  const { data: stats } = useQuery({
    queryKey: ['customer-stats'],
    queryFn: () => customersAPI.stats(),
  })

  const customers  = data?.data?.results || []
  const totalCount = data?.data?.count   || 0
  const st         = stats?.data         || {}

  const s = {
    page: { background: '#0f0e1a', minHeight: '100vh', padding: 24, fontFamily: "'Outfit', sans-serif", color: '#f1f5f9' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
    title: { fontSize: 22, fontWeight: 700, margin: 0 },
    addBtn: {
      background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
      border: 'none', borderRadius: 10, padding: '10px 20px',
      color: 'white', fontWeight: 600, cursor: 'pointer', fontSize: 14,
    },
    statsRow: { display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 12, marginBottom: 24 },
    statCard: {
      background: 'rgba(19,17,42,0.9)', border: '1px solid rgba(99,102,241,0.15)',
      borderRadius: 12, padding: '16px 20px',
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
    table: { width: '100%', borderCollapse: 'collapse' },
    th: {
      color: '#64748b', fontSize: 12, fontWeight: 600, textAlign: 'left',
      padding: '12px 16px', borderBottom: '1px solid rgba(99,102,241,0.15)',
      textTransform: 'uppercase', letterSpacing: '0.05em', background: 'rgba(19,17,42,0.9)',
    },
    td: { padding: '14px 16px', borderBottom: '1px solid rgba(99,102,241,0.08)', fontSize: 13, color: '#cbd5e1' },
    row: { cursor: 'pointer', transition: 'background 0.15s' },
    tableWrap: {
      background: 'rgba(19,17,42,0.9)', border: '1px solid rgba(99,102,241,0.15)',
      borderRadius: 12, overflow: 'hidden',
    },
    pagination: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 },
    pageBtn: {
      background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
      borderRadius: 8, padding: '8px 16px', color: '#94a3b8', cursor: 'pointer',
      fontSize: 13, fontFamily: 'inherit',
    },
  }

  const STAT_ITEMS = [
    { label: 'মোট গ্রাহক', value: st.total, icon: '👥', color: '#6366f1' },
    { label: 'সক্রিয়', value: st.active, icon: '✅', color: '#22c55e' },
    { label: 'স্থগিত', value: st.suspended, icon: '⛔', color: '#f59e0b' },
    { label: 'মেয়াদ শেষ হবে', value: st.expiring_soon, icon: '⏰', color: '#ef4444' },
    { label: 'অপেক্ষমান', value: st.pending, icon: '⏳', color: '#a78bfa' },
  ]

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>👥 গ্রাহক ব্যবস্থাপনা</h1>
        <button style={s.addBtn} onClick={() => navigate('/customers/new')}>
          ＋ নতুন গ্রাহক
        </button>
      </div>

      {/* Stats */}
      <div style={s.statsRow}>
        {STAT_ITEMS.map(item => (
          <div key={item.label} style={s.statCard}>
            <div style={{ fontSize: 22, marginBottom: 6 }}>{item.icon}</div>
            <div style={{ fontSize: 24, fontWeight: 700, color: item.color }}>{item.value ?? '—'}</div>
            <div style={{ color: '#64748b', fontSize: 12 }}>{item.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={s.filters}>
        <input style={s.input} placeholder="🔍 নাম, ফোন, আইডি দিয়ে খুঁজুন..."
          value={search} onChange={e => { setSearch(e.target.value); setPage(1) }} />
        <select style={s.select} value={status} onChange={e => { setStatus(e.target.value); setPage(1) }}>
          <option value="">সকল স্ট্যাটাস</option>
          <option value="active">সক্রিয়</option>
          <option value="suspended">স্থগিত</option>
          <option value="terminated">বাতিল</option>
          <option value="pending">অপেক্ষমান</option>
        </select>
      </div>

      {/* Table */}
      <div style={s.tableWrap}>
        {isLoading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#6366f1' }}>⏳ লোড হচ্ছে...</div>
        ) : (
          <table style={s.table}>
            <thead>
              <tr>
                {['আইডি', 'নাম', 'ফোন', 'প্যাকেজ', 'এলাকা', 'মেয়াদ', 'স্ট্যাটাস', 'কার্যক্রম'].map(h => (
                  <th key={h} style={s.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {customers.length === 0 ? (
                <tr><td colSpan={8} style={{ ...s.td, textAlign: 'center', color: '#64748b', padding: 40 }}>
                  কোনো গ্রাহক পাওয়া যায়নি
                </td></tr>
              ) : customers.map(c => (
                <tr key={c.id} style={s.row}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(99,102,241,0.05)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}
                  onClick={() => navigate(`/customers/${c.id}`)}>
                  <td style={{ ...s.td, color: '#6366f1', fontFamily: 'monospace', fontWeight: 600 }}>{c.customer_id}</td>
                  <td style={{ ...s.td, fontWeight: 600, color: '#e2e8f0' }}>{c.first_name} {c.last_name}</td>
                  <td style={s.td}>{c.phone}</td>
                  <td style={{ ...s.td, color: '#a78bfa' }}>{c.package_name}</td>
                  <td style={s.td}>{c.zone_name || '—'}</td>
                  <td style={{ ...s.td, color: c.expiry_date ? '#f59e0b' : '#64748b' }}>
                    {c.expiry_date ? new Date(c.expiry_date).toLocaleDateString('bn-BD') : '—'}
                  </td>
                  <td style={s.td}><StatusBadge status={c.status} /></td>
                  <td style={s.td}>
                    <button style={{
                      background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
                      borderRadius: 6, padding: '4px 10px', color: '#94a3b8', cursor: 'pointer', fontSize: 12,
                    }} onClick={e => { e.stopPropagation(); navigate(`/customers/${c.id}`) }}>
                      বিস্তারিত →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      <div style={s.pagination}>
        <span style={{ color: '#64748b', fontSize: 13 }}>
          মোট {totalCount} জন গ্রাহক
        </span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button style={s.pageBtn} onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>← আগে</button>
          <span style={{ color: '#94a3b8', padding: '8px 12px', fontSize: 13 }}>{page}</span>
          <button style={s.pageBtn} onClick={() => setPage(p => p + 1)} disabled={customers.length < 20}>পরে →</button>
        </div>
      </div>
    </div>
  )
}
