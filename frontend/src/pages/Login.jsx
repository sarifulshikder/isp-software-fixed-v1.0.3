import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { toast } from 'react-toastify'

export default function Login() {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading]   = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'লগইন ব্যর্থ হয়েছে!')
    } finally {
      setLoading(false)
    }
  }

  const s = {
    page: {
      minHeight: '100vh', background: '#0f0e1a',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: "'Outfit', sans-serif",
      backgroundImage: `
        radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(139,92,246,0.1) 0%, transparent 50%)
      `,
    },
    card: {
      width: 400, background: 'rgba(19,17,42,0.95)',
      border: '1px solid rgba(99,102,241,0.25)',
      borderRadius: 20, padding: '48px 40px',
      boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
    },
    logo: { textAlign: 'center', marginBottom: 36 },
    logoIcon: { fontSize: 48, display: 'block', marginBottom: 12 },
    logoTitle: { color: '#f1f5f9', fontSize: 24, fontWeight: 800, margin: 0 },
    logoSub: { color: '#64748b', fontSize: 13, marginTop: 4 },
    label: { display: 'block', color: '#94a3b8', fontSize: 13, fontWeight: 500, marginBottom: 6 },
    input: {
      width: '100%', boxSizing: 'border-box',
      background: 'rgba(99,102,241,0.08)',
      border: '1px solid rgba(99,102,241,0.2)',
      borderRadius: 10, padding: '12px 14px',
      color: '#f1f5f9', fontSize: 14, outline: 'none',
      marginBottom: 20, fontFamily: 'inherit',
      transition: 'border-color 0.2s',
    },
    btn: {
      width: '100%', padding: '13px',
      background: loading ? 'rgba(99,102,241,0.4)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
      border: 'none', borderRadius: 10, color: 'white',
      fontSize: 15, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
      fontFamily: 'inherit', marginTop: 8,
      boxShadow: '0 4px 20px rgba(99,102,241,0.4)',
    },
    hint: {
      marginTop: 24, padding: '14px',
      background: 'rgba(99,102,241,0.08)',
      border: '1px solid rgba(99,102,241,0.15)',
      borderRadius: 10, color: '#94a3b8', fontSize: 12,
    },
  }

  return (
    <div style={s.page}>
      <div style={s.card}>
        <div style={s.logo}>
          <span style={s.logoIcon}>📡</span>
          <h1 style={s.logoTitle}>ISP Management</h1>
          <p style={s.logoSub}>Billing & Network Control System</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div>
            <label style={s.label}>ইমেইল</label>
            <input
              style={s.input} type="email"
              placeholder="admin@myisp.com"
              value={email} onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label style={s.label}>পাসওয়ার্ড</label>
            <input
              style={s.input} type="password"
              placeholder="••••••••"
              value={password} onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          <button style={s.btn} type="submit" disabled={loading}>
            {loading ? '⏳ লগইন হচ্ছে...' : '🔐 লগইন করুন'}
          </button>
        </form>

        <div style={s.hint}>
          💡 <strong>Demo:</strong> admin@isp.com / admin123
        </div>
      </div>
    </div>
  )
}
