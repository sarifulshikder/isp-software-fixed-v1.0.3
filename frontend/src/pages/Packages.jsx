import { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'

export default function Packages() {
  const [packages, setPackages] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editItem, setEditItem] = useState(null)
  const [form, setForm] = useState({
    name: '', code: '', download_speed: '', upload_speed: '',
    price: '', billing_cycle: 'monthly', description: '',
    is_active: true, is_public: true,
  })

  const fetchPackages = async () => {
    try {
      setLoading(true)
      const res = await api.packages.list()
      setPackages(res.data.results || res.data || [])
    } catch (err) {
      toast.error('Failed to load packages')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchPackages() }, [])

  const openAdd = () => {
    setEditItem(null)
    setForm({ name: '', code: '', download_speed: '', upload_speed: '', price: '', billing_cycle: 'monthly', description: '', is_active: true, is_public: true })
    setShowModal(true)
  }

  const openEdit = (pkg) => {
    setEditItem(pkg)
    setForm({ name: pkg.name, code: pkg.code, download_speed: pkg.download_speed, upload_speed: pkg.upload_speed, price: pkg.price, billing_cycle: pkg.billing_cycle, description: pkg.description || '', is_active: pkg.is_active, is_public: pkg.is_public })
    setShowModal(true)
  }

  const handleSave = async () => {
    try {
      if (editItem) {
        await api.packages.update(editItem.id, form)
        toast.success('Package updated')
      } else {
        await api.packages.create(form)
        toast.success('Package created')
      }
      setShowModal(false)
      fetchPackages()
    } catch (err) {
      toast.error('Failed to save')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this package?')) return
    try {
      await api.packages.delete(id)
      toast.success('Package deleted')
      fetchPackages()
    } catch (err) {
      toast.error('Failed to delete')
    }
  }

  const page = { background: '#0f0e1a', minHeight: '100vh', padding: 24, fontFamily: "'Outfit', sans-serif", color: '#f1f5f9' }
  const hdr = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }
  const btn = { padding: '10px 20px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', border: 'none', borderRadius: 10, color: 'white', fontSize: 14, fontWeight: 600, cursor: 'pointer' }
  const grid = { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }
  const card = { background: 'rgba(19,17,42,0.9)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 16, padding: 24 }
  const overlay = { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }
  const modal = { background: '#1a1830', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 20, padding: 32, width: '90%', maxWidth: 500, maxHeight: '90vh', overflowY: 'auto' }
  const inp = { width: '100%', background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 10, padding: '10px 14px', color: '#f1f5f9', fontSize: 14, outline: 'none', boxSizing: 'border-box' }
  const sel = { width: '100%', background: '#1a1830', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 10, padding: '10px 14px', color: '#f1f5f9', fontSize: 14, outline: 'none', boxSizing: 'border-box' }
  const lbl = { display: 'block', color: '#94a3b8', fontSize: 13, marginBottom: 6, marginTop: 14 }
  const empty = { textAlign: 'center', padding: 60, color: '#94a3b8' }
  const btnSm = { padding: '6px 14px', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: 'pointer', marginLeft: 6 }

  return (
    <div style={page}>
      <div style={hdr}>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Package Management</h1>
        <button style={btn} onClick={openAdd}>+ New Package</button>
      </div>

      {loading ? (
        <div style={empty}>Loading...</div>
      ) : packages.length === 0 ? (
        <div style={empty}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>📦</div>
          <p>No packages found. Create a new package.</p>
        </div>
      ) : (
        <div style={grid}>
          {packages.map(pkg => (
            <div key={pkg.id} style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{pkg.name}</div>
                <span style={{ display: 'inline-block', padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, background: pkg.is_active ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)', color: pkg.is_active ? '#22c55e' : '#ef4444' }}>
                  {pkg.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#6366f1', marginBottom: 4 }}>
                {pkg.price} <span style={{ fontSize: 14, color: '#94a3b8', fontWeight: 400 }}>BDT/month</span>
              </div>
              <div style={{ color: '#94a3b8', fontSize: 13, marginBottom: 4 }}>Download: {pkg.download_speed} Mbps</div>
              <div style={{ color: '#94a3b8', fontSize: 13, marginBottom: 4 }}>Upload: {pkg.upload_speed} Mbps</div>
              <div style={{ color: '#94a3b8', fontSize: 13 }}>Code: {pkg.code}</div>
              {pkg.description && <div style={{ color: '#94a3b8', fontSize: 13, marginTop: 8 }}>{pkg.description}</div>}
              <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
                <button style={{ ...btnSm, background: 'rgba(99,102,241,0.2)', color: '#6366f1' }} onClick={() => openEdit(pkg)}>Edit</button>
                <button style={{ ...btnSm, background: 'rgba(239,68,68,0.15)', color: '#ef4444' }} onClick={() => handleDelete(pkg.id)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div style={overlay}>
          <div style={modal}>
            <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>{editItem ? 'Edit Package' : 'New Package'}</h2>
            <label style={lbl}>Package Name *</label>
            <input style={inp} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="10 Mbps Basic" />
            <label style={lbl}>Code *</label>
            <input style={inp} value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} placeholder="PKG-10MB" />
            <label style={lbl}>Download Speed (Mbps)</label>
            <input style={inp} type="number" value={form.download_speed} onChange={e => setForm({ ...form, download_speed: e.target.value })} placeholder="10" />
            <label style={lbl}>Upload Speed (Mbps)</label>
            <input style={inp} type="number" value={form.upload_speed} onChange={e => setForm({ ...form, upload_speed: e.target.value })} placeholder="5" />
            <label style={lbl}>Price (BDT)</label>
            <input style={inp} type="number" value={form.price} onChange={e => setForm({ ...form, price: e.target.value })} placeholder="500" />
            <label style={lbl}>Billing Cycle</label>
            <select style={sel} value={form.billing_cycle} onChange={e => setForm({ ...form, billing_cycle: e.target.value })}>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
            </select>
            <label style={lbl}>Description</label>
            <input style={inp} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Package description" />
            <div style={{ marginTop: 14, display: 'flex', gap: 20 }}>
              <label style={{ color: '#94a3b8', fontSize: 13, cursor: 'pointer' }}>
                <input type="checkbox" checked={form.is_active} onChange={e => setForm({ ...form, is_active: e.target.checked })} style={{ marginRight: 6 }} />
                Active
              </label>
              <label style={{ color: '#94a3b8', fontSize: 13, cursor: 'pointer' }}>
                <input type="checkbox" checked={form.is_public} onChange={e => setForm({ ...form, is_public: e.target.checked })} style={{ marginRight: 6 }} />
                Public
              </label>
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 20, justifyContent: 'flex-end' }}>
              <button style={{ ...btnSm, background: 'rgba(99,102,241,0.15)', color: '#94a3b8', padding: '10px 20px' }} onClick={() => setShowModal(false)}>Cancel</button>
              <button style={btn} onClick={handleSave}>{editItem ? 'Update' : 'Save'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
