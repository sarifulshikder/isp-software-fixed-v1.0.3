import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

const NAV = [
  { to: '/',          icon: '🏠', label: 'Dashboard' },
  { to: '/customers', icon: '👥', label: 'গ্রাহক' },
  { to: '/billing',   icon: '📋', label: 'বিলিং' },
  { to: '/payments',  icon: '💳', label: 'পেমেন্ট' },
  { to: '/packages',  icon: '📦', label: 'প্যাকেজ' },
  { to: '/network',   icon: '📡', label: 'নেটওয়ার্ক' },
  { to: '/support',   icon: '🎫', label: 'সাপোর্ট' },
  { to: '/inventory', icon: '🏭', label: 'ইনভেন্টরি' },
  { to: '/resellers', icon: '🤝', label: 'রিসেলার' },
  { to: '/reports',   icon: '📊', label: 'রিপোর্ট' },
  { to: '/hr',        icon: '👔', label: 'HR' },
  { to: '/settings',  icon: '⚙️',  label: 'সেটিংস' },
]

const S = {
  root: {
    display: 'flex', minHeight: '100vh',
    background: '#0f0e1a', fontFamily: "'Outfit', sans-serif",
  },
  sidebar: (collapsed) => ({
    width: collapsed ? 64 : 220,
    background: 'linear-gradient(180deg, #13112a 0%, #0f0e1a 100%)',
    borderRight: '1px solid rgba(99,102,241,0.15)',
    display: 'flex', flexDirection: 'column',
    transition: 'width 0.25s ease',
    overflow: 'hidden', flexShrink: 0,
    position: 'sticky', top: 0, height: '100vh',
  }),
  logo: (collapsed) => ({
    padding: collapsed ? '20px 0' : '20px 16px',
    borderBottom: '1px solid rgba(99,102,241,0.15)',
    display: 'flex', alignItems: 'center', gap: 10,
    justifyContent: collapsed ? 'center' : 'flex-start',
  }),
  logoIcon: { fontSize: 24 },
  logoText: (collapsed) => ({
    color: '#818cf8', fontWeight: 800, fontSize: 14,
    display: collapsed ? 'none' : 'block',
    letterSpacing: '-0.02em', lineHeight: 1.2,
    whiteSpace: 'nowrap',
  }),
  nav: { flex: 1, padding: '12px 8px', overflowY: 'auto', overflowX: 'hidden' },
  navLink: (collapsed) => ({
    display: 'flex', alignItems: 'center', gap: 10,
    padding: collapsed ? '10px 0' : '10px 12px',
    borderRadius: 10, marginBottom: 2, cursor: 'pointer',
    textDecoration: 'none', color: '#64748b',
    transition: 'all 0.15s', fontSize: 13, fontWeight: 500,
    justifyContent: collapsed ? 'center' : 'flex-start',
    whiteSpace: 'nowrap',
  }),
  activeStyle: {
    color: '#a5b4fc',
    background: 'rgba(99,102,241,0.15)',
    fontWeight: 600,
  },
  icon: { fontSize: 18, flexShrink: 0 },
  label: (collapsed) => ({ display: collapsed ? 'none' : 'block' }),
  collapseBtn: {
    padding: '12px', display: 'flex', justifyContent: 'center',
    borderTop: '1px solid rgba(99,102,241,0.15)', cursor: 'pointer',
    color: '#64748b', fontSize: 16,
  },
  main: {
    flex: 1, display: 'flex', flexDirection: 'column',
    overflowX: 'hidden',
  },
  topbar: {
    background: 'rgba(15,14,26,0.9)', backdropFilter: 'blur(10px)',
    borderBottom: '1px solid rgba(99,102,241,0.1)',
    padding: '12px 24px', display: 'flex',
    alignItems: 'center', justifyContent: 'space-between',
    position: 'sticky', top: 0, zIndex: 10,
  },
  search: {
    background: 'rgba(99,102,241,0.08)',
    border: '1px solid rgba(99,102,241,0.2)',
    borderRadius: 10, padding: '8px 14px',
    color: '#94a3b8', fontSize: 13, outline: 'none',
    width: 280,
  },
  userBadge: {
    display: 'flex', alignItems: 'center', gap: 10,
    cursor: 'pointer',
  },
  avatar: {
    width: 36, height: 36, borderRadius: '50%',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: 'white', fontWeight: 700, fontSize: 14,
  },
  userName: { color: '#e2e8f0', fontSize: 13, fontWeight: 600 },
  userRole: { color: '#64748b', fontSize: 11 },
  content: { flex: 1, overflowY: 'auto' },
}

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const initial = user?.email?.[0]?.toUpperCase() || 'A'

  return (
    <div style={S.root}>
      {/* Sidebar */}
      <aside style={S.sidebar(collapsed)}>
        <div style={S.logo(collapsed)}>
          <span style={S.logoIcon}>📡</span>
          <div style={S.logoText(collapsed)}>
            <div>ISP</div>
            <div style={{ color: '#6366f1', fontSize: 10, fontWeight: 400 }}>Management</div>
          </div>
        </div>

        <nav style={S.nav}>
          {NAV.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              style={({ isActive }) => ({
                ...S.navLink(collapsed),
                ...(isActive ? S.activeStyle : {}),
              })}
            >
              <span style={S.icon}>{icon}</span>
              <span style={S.label(collapsed)}>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div style={S.collapseBtn} onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? '▶' : '◀'}
        </div>
      </aside>

      {/* Main */}
      <main style={S.main}>
        {/* Topbar */}
        <header style={S.topbar}>
          <input
            style={S.search}
            placeholder="🔍 গ্রাহক, ইনভয়েস, টিকেট খুঁজুন..."
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ color: '#6366f1', fontSize: 20, cursor: 'pointer' }} title="Notifications">🔔</span>
            <div style={S.userBadge} onClick={handleLogout} title="Logout">
              <div style={S.avatar}>{initial}</div>
              <div>
                <div style={S.userName}>{user?.email || 'Admin'}</div>
                <div style={S.userRole}>{user?.role || 'superadmin'} · Logout</div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div style={S.content}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}
