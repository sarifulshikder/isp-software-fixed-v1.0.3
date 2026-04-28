import { useState, useEffect } from 'react'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

// ─── Mock data (replace with API calls) ───
const revenueData = [
  { month: 'Jan', revenue: 420000, target: 400000 },
  { month: 'Feb', revenue: 380000, target: 400000 },
  { month: 'Mar', revenue: 510000, target: 450000 },
  { month: 'Apr', revenue: 490000, target: 450000 },
  { month: 'May', revenue: 580000, target: 500000 },
  { month: 'Jun', revenue: 620000, target: 550000 },
  { month: 'Jul', revenue: 710000, target: 600000 },
]

const bandwidthData = [
  { time: '00:00', down: 820, up: 240 },
  { time: '04:00', down: 420, up: 180 },
  { time: '08:00', down: 1200, up: 380 },
  { time: '12:00', down: 1800, up: 620 },
  { time: '16:00', down: 2100, up: 740 },
  { time: '20:00', down: 1950, up: 680 },
  { time: '23:59', down: 1100, up: 420 },
]

const packageDist = [
  { name: '10 Mbps', value: 312, color: '#6366f1' },
  { name: '20 Mbps', value: 487, color: '#8b5cf6' },
  { name: '50 Mbps', value: 298, color: '#a78bfa' },
  { name: '100 Mbps', value: 156, color: '#c4b5fd' },
  { name: '200 Mbps', value: 89, color: '#ddd6fe' },
]

const recentPayments = [
  { id: 'PAY-001', customer: 'রহিম উদ্দিন', amount: 750, method: 'bKash', time: '5 min ago' },
  { id: 'PAY-002', customer: 'সালমা বেগম', amount: 1200, method: 'Cash', time: '12 min ago' },
  { id: 'PAY-003', customer: 'করিম মিয়া', amount: 500, method: 'Nagad', time: '28 min ago' },
  { id: 'PAY-004', customer: 'জামাল হোসেন', amount: 2000, method: 'Bank', time: '1 hr ago' },
  { id: 'PAY-005', customer: 'নাসরিন আক্তার', amount: 800, method: 'bKash', time: '2 hr ago' },
]

const tickets = [
  { id: 'TKT-001', customer: 'আব্দুল হাকিম', issue: 'No Internet', priority: 'critical', time: '10m' },
  { id: 'TKT-002', customer: 'ফাতেমা খানম', issue: 'Slow Speed', priority: 'high', time: '1h' },
  { id: 'TKT-003', customer: 'মোহাম্মদ আলী', issue: 'Billing Issue', priority: 'medium', time: '3h' },
  { id: 'TKT-004', customer: 'সুমাইয়া বেগম', issue: 'Device Issue', priority: 'low', time: '5h' },
]

function StatCard({ title, value, sub, icon, color, trend }) {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #1e1b4b 0%, #1a1744 100%)',
      border: '1px solid rgba(99,102,241,0.2)',
      borderRadius: 16,
      padding: '24px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: -20, right: -20,
        width: 100, height: 100,
        background: color + '15',
        borderRadius: '50%',
      }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ color: '#94a3b8', fontSize: 13, margin: 0, fontFamily: 'Outfit, sans-serif' }}>{title}</p>
          <h2 style={{ color: '#f1f5f9', fontSize: 28, fontWeight: 700, margin: '8px 0 4px', fontFamily: 'Outfit, sans-serif' }}>{value}</h2>
          <p style={{ color: trend > 0 ? '#34d399' : '#f87171', fontSize: 12, margin: 0, fontFamily: 'Outfit, sans-serif' }}>
            {trend > 0 ? '▲' : '▼'} {Math.abs(trend)}% from last month
          </p>
          {sub && <p style={{ color: '#64748b', fontSize: 12, margin: '4px 0 0', fontFamily: 'Outfit, sans-serif' }}>{sub}</p>}
        </div>
        <div style={{
          background: color + '20',
          borderRadius: 12,
          padding: 12,
          fontSize: 24,
        }}>{icon}</div>
      </div>
    </div>
  )
}

function PriorityBadge({ priority }) {
  const colors = {
    critical: { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
    high:     { bg: '#fff7ed', color: '#ea580c', border: '#fed7aa' },
    medium:   { bg: '#fefce8', color: '#ca8a04', border: '#fef08a' },
    low:      { bg: '#f0fdf4', color: '#16a34a', border: '#bbf7d0' },
  }
  const c = colors[priority] || colors.low
  return (
    <span style={{
      background: c.bg, color: c.color, border: `1px solid ${c.border}`,
      borderRadius: 6, padding: '2px 8px', fontSize: 11, fontWeight: 600,
      textTransform: 'uppercase', letterSpacing: '0.05em',
    }}>{priority}</span>
  )
}

function MethodBadge({ method }) {
  const colors = {
    'bKash': '#e91e8c', 'Nagad': '#f97316', 'Cash': '#22c55e',
    'Bank': '#3b82f6', 'Rocket': '#8b5cf6',
  }
  return (
    <span style={{
      background: (colors[method] || '#6366f1') + '20',
      color: colors[method] || '#6366f1',
      borderRadius: 6, padding: '2px 8px', fontSize: 12, fontWeight: 600,
    }}>{method}</span>
  )
}

export default function Dashboard() {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  const s = {
    page: {
      background: '#0f0e1a',
      minHeight: '100vh',
      padding: '24px',
      fontFamily: "'Outfit', sans-serif",
      color: '#f1f5f9',
    },
    header: {
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      marginBottom: 28,
    },
    title: { fontSize: 24, fontWeight: 700, color: '#f1f5f9', margin: 0 },
    subtitle: { fontSize: 14, color: '#94a3b8', margin: '4px 0 0' },
    clock: { fontSize: 13, color: '#6366f1', fontWeight: 600,
      background: 'rgba(99,102,241,0.1)', padding: '8px 16px',
      borderRadius: 20, border: '1px solid rgba(99,102,241,0.2)' },
    grid4: { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 },
    grid2: { display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 24 },
    grid3: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 24 },
    card: {
      background: 'linear-gradient(135deg, #1e1b4b 0%, #1a1744 100%)',
      border: '1px solid rgba(99,102,241,0.2)',
      borderRadius: 16, padding: 24,
    },
    cardTitle: { fontSize: 15, fontWeight: 600, color: '#e2e8f0', marginBottom: 20, margin: '0 0 20px' },
    table: { width: '100%', borderCollapse: 'collapse' },
    th: { color: '#64748b', fontSize: 12, fontWeight: 600, textAlign: 'left',
      padding: '8px 12px', borderBottom: '1px solid rgba(99,102,241,0.15)',
      textTransform: 'uppercase', letterSpacing: '0.05em' },
    td: { padding: '12px', borderBottom: '1px solid rgba(99,102,241,0.08)',
      fontSize: 13, color: '#cbd5e1' },
  }

  return (
    <div style={s.page}>
      {/* Header */}
      <div style={s.header}>
        <div>
          <h1 style={s.title}>📡 ISP Dashboard</h1>
          <p style={s.subtitle}>Welcome back, Admin · Real-time network overview</p>
        </div>
        <div style={s.clock}>
          🕐 {time.toLocaleTimeString('bn-BD')} · {time.toLocaleDateString('bn-BD')}
        </div>
      </div>

      {/* KPI Cards */}
      <div style={s.grid4}>
        <StatCard title="মোট গ্রাহক" value="1,342" sub="48 pending activation" icon="👥" color="#6366f1" trend={12} />
        <StatCard title="এই মাসের আয়" value="৳7,10,500" sub="৳2,34,000 বাকি" icon="💰" color="#22c55e" trend={8} />
        <StatCard title="সক্রিয় সংযোগ" value="1,287" sub="55 suspended" icon="📶" color="#3b82f6" trend={5} />
        <StatCard title="খোলা টিকেট" value="23" sub="4 critical" icon="🎫" color="#f59e0b" trend={-15} />
      </div>

      {/* Revenue Chart + Package Distribution */}
      <div style={s.grid2}>
        <div style={s.card}>
          <p style={s.cardTitle}>📊 মাসিক আয় (Revenue vs Target)</p>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={revenueData}>
              <defs>
                <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
              <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false}
                tickFormatter={v => `৳${(v/1000).toFixed(0)}k`} />
              <Tooltip
                contentStyle={{ background: '#1e1b4b', border: '1px solid #6366f1', borderRadius: 8, color: '#f1f5f9' }}
                formatter={v => [`৳${v.toLocaleString()}`, '']}
              />
              <Area type="monotone" dataKey="revenue" stroke="#6366f1" fill="url(#rev)" strokeWidth={2} name="আয়" />
              <Area type="monotone" dataKey="target" stroke="#22c55e" fill="none" strokeWidth={1.5} strokeDasharray="4 4" name="লক্ষ্য" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div style={s.card}>
          <p style={s.cardTitle}>📦 প্যাকেজ বিতরণ</p>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={packageDist} cx="50%" cy="50%" innerRadius={50} outerRadius={80}
                dataKey="value" paddingAngle={3}>
                {packageDist.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1e1b4b', border: '1px solid #6366f1', borderRadius: 8, color: '#f1f5f9' }} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
            {packageDist.map(p => (
              <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color }} />
                <span style={{ fontSize: 11, color: '#94a3b8' }}>{p.name} ({p.value})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bandwidth Chart */}
      <div style={{ ...s.card, marginBottom: 24 }}>
        <p style={s.cardTitle}>📡 নেটওয়ার্ক ব্যান্ডউইথ ব্যবহার (Mbps)</p>
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={bandwidthData}>
            <defs>
              <linearGradient id="down" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="up" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
            <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} />
            <Tooltip contentStyle={{ background: '#1e1b4b', border: '1px solid #6366f1', borderRadius: 8, color: '#f1f5f9' }} />
            <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
            <Area type="monotone" dataKey="down" stroke="#3b82f6" fill="url(#down)" strokeWidth={2} name="Download" />
            <Area type="monotone" dataKey="up" stroke="#22c55e" fill="url(#up)" strokeWidth={2} name="Upload" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Payments + Open Tickets */}
      <div style={s.grid2}>
        <div style={s.card}>
          <p style={s.cardTitle}>💳 সাম্প্রতিক পেমেন্ট</p>
          <table style={s.table}>
            <thead>
              <tr>
                <th style={s.th}>ID</th>
                <th style={s.th}>গ্রাহক</th>
                <th style={s.th}>পরিমাণ</th>
                <th style={s.th}>মাধ্যম</th>
                <th style={s.th}>সময়</th>
              </tr>
            </thead>
            <tbody>
              {recentPayments.map(p => (
                <tr key={p.id}>
                  <td style={{ ...s.td, color: '#6366f1', fontFamily: 'monospace' }}>{p.id}</td>
                  <td style={s.td}>{p.customer}</td>
                  <td style={{ ...s.td, color: '#34d399', fontWeight: 600 }}>৳{p.amount.toLocaleString()}</td>
                  <td style={s.td}><MethodBadge method={p.method} /></td>
                  <td style={{ ...s.td, color: '#64748b' }}>{p.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={s.card}>
          <p style={s.cardTitle}>🎫 সক্রিয় টিকেট</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {tickets.map(t => (
              <div key={t.id} style={{
                background: 'rgba(99,102,241,0.08)',
                borderRadius: 10, padding: '12px 14px',
                border: '1px solid rgba(99,102,241,0.12)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontSize: 12, color: '#6366f1', fontFamily: 'monospace' }}>{t.id}</span>
                  <PriorityBadge priority={t.priority} />
                </div>
                <p style={{ margin: 0, fontSize: 13, color: '#e2e8f0', fontWeight: 500 }}>{t.customer}</p>
                <p style={{ margin: '2px 0 0', fontSize: 12, color: '#94a3b8' }}>{t.issue} · {t.time} ago</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Stats Row */}
      <div style={s.grid3}>
        {[
          { label: 'আজকের আয়', value: '৳28,500', icon: '💵', color: '#22c55e' },
          { label: 'নতুন গ্রাহক (এ মাসে)', value: '47', icon: '👤', color: '#6366f1' },
          { label: 'নেটওয়ার্ক আপটাইম', value: '99.94%', icon: '📶', color: '#3b82f6' },
          { label: 'বকেয়া ইনভয়েস', value: '156', icon: '📋', color: '#f59e0b' },
          { label: 'আজকের পেমেন্ট', value: '89', icon: '✅', color: '#10b981' },
          { label: 'সাসপেন্ড গ্রাহক', value: '23', icon: '⛔', color: '#ef4444' },
        ].map(item => (
          <div key={item.label} style={{
            background: 'linear-gradient(135deg, #1e1b4b 0%, #1a1744 100%)',
            border: '1px solid rgba(99,102,241,0.2)',
            borderRadius: 12, padding: '16px 20px',
            display: 'flex', alignItems: 'center', gap: 16,
          }}>
            <div style={{ fontSize: 28 }}>{item.icon}</div>
            <div>
              <p style={{ margin: 0, fontSize: 12, color: '#64748b' }}>{item.label}</p>
              <p style={{ margin: '4px 0 0', fontSize: 20, fontWeight: 700, color: item.color }}>{item.value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
