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

  const s = {
    page: { background: '#0f0e1a', minHeight: '100vh', padding: 24, fontFamily: "'Outfit', sans-serif", color: '#f1f5f9' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
    title: { fontSize: 22, fontWeight: 700, margin: 0 },
    btn: { padding: '10px 20px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', border: 'none', borderRadius: 10, color: 'white', fontSize: 14, fontWeight: 600, cursor: 'pointer' },
    btnSm: { padding: '6px 14px', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: 'pointer', marginLeft: 6 },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 },
    card: { background: 'rgba(19,17,42,0.9)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 16, padding: 24 },
    cardTitle: { fontSize: 18, fontWeight: 700, marginBottom: 8 },
    badge: { display: 'inline-block', padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, marginBottom: 12 },
    price: { fontSize: 28, fontWeight: 800, color: '#6366f1', marginBottom: 4 },
    info: { color: '#94a3b8', fontSize: 13, marginBottom: 4 },
    actions: { marginTop: 16, display: 'flex', justifyContent: 'flex-end' },
    overlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
    modal: { background: '#1a1830', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 20, padding: 32, width: '90%', maxWidth: 500, maxHeight: '90vh', overflowY: 'auto' },
    modalTitle: { fontSize: 20, fontWeight: 700, marginBottom: 20 },
    label: { display: 'block', color: '#94a3b8', fontSize: 13, marginBottom: 6, marginTop: 14 },
    input: { width: '100%', background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 10, padding: '10px 14px', color: '#f1f5f9', fontSize: 14, outline: 'none', boxSizing: 'border-box' },
    select: { width: '100%', background: '#1a1830', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 10, padding: '10px 14px', color: '#f1f5f9', fontSize: 14, outline: 'none', boxSizing: 'border-box' },
    modalBtns: { display: 'flex', gap: 10, marginTop: 20, justifyContent: 'flex-end' },
    empty: { textAlign: 'center', padding: 60, color: '#94a3b8' },
  }

  const fetchPackages = async () => {
    try {
      setLoading(true)
      const res = await api.packages.list()
      setPackages(res.data.results || res.data || [])
    } catch (err) {
      toast.error('প্যাকেজ লোড করতে ব্যর্থ')
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
        toast.success('প্যাকেজ আপডেট হয়েছে')
      } else {
        await api.packages.create(form)
        toast.success('প্যাকেজ তৈরি হয়েছে')
      }
      setShowModal(false)
      fetchPackages()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'সংরক্ষণ ব্যর্থ হয়েছে')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('এই প্যাকেজটি মুছে ফেলবেন?')) return
    try {
      await api.packages.delete(id)
      toast.success('প্যাকেজ মুছে ফেলা হয়েছে')
      fetchPackages()
    } catch (err) {
      toast.error('মুছতে ব্যর্থ হয়েছে')
    }
  }

  const cycleLabel = { monthly: 'মাসিক', quarterly: 'ত্রৈমাসিক', yearly: 'বার্ষিক' }

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>📦 প্যাকেজ ব্যবস্থাপনা</h1>
        <button style={s.btn} onClick={openAdd}>+ নতুন প্যাকেজ</button>
      </div>

      {loading ? (
        <div style={s.empty}>⏳ লোড হচ্ছে...</div>
      ) : packages.length === 0 ? (
        <div style={s.empty}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>📦</div>
          <p>কোনো প্যাকেজ নেই। নতুন প্যাকেজ তৈরি করুন।</p>
        </div>
      ) : (
        <div style={s.grid}>
          {packages.map(pkg => (
            <div key={pkg.id} style={s.card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={s.cardTitle}>{pkg.name}</div>
                <span style={{ ...s.badge, background: pkg.is_active ? 'rgba(34,197,94,0.15)', color: '#22c55e' }}>
                  {pkg.is_active ? '✅ সক্রিয়' : '❌ নিষ্ক্রিয়'}
                </span>
              </div>
              <div style={s.price}>৳{pkg.price} <span style={{ fontSize: 14, color: '#94a3b8', fontWeight: 400 }}>/{cycleLabel[pkg.billing_cycle] || pkg.billing_cycle}</span></div>
              <div style={s.info}>⬇️ Download: {pkg.download_speed} Mbps</div>
              <div style={s.info}>⬆️ Upload: {pkg.upload_speed} Mbps</div>
              <div style={s.info}>🔑 কোড: {pkg.code}</div>
              {pkg.description && <div style={{ ...s.info, marginTop: 8 }}>{pkg.description}</div>}
              <div style={s.actions}>
                <button style={{ ...s.btnSm, background: 'rgba(99,102,241,0.2)', color: '#6366f1' }} onClick={() => openEdit(pkg)}>✏️ সম্পাদনা</button>
                <button style={{ ...s.btnSm, background: 'rgba(239,68,68,0.15)', color: '#ef4444' }} onClick={() => handleDelete(pkg.id)}>🗑️ মুছুন</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div style={s.overlay}>
          <div style={s.modal}>
            <h2 style={s.modalTitle}>{editItem ? '✏️ প্যাকেজ সম্পাদনা' : '➕ নতুন প্যাকেজ'}</h2>

            <label style={s.label}>প্যাকেজের নাম *</label>
            <input style={s.input} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="যেমন: 10 Mbps Basic" />

            <label style={s.label}>কোড *</label>
            <input style={s.input} value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} placeholder="যেমন: PKG-10MB" />

            <label style={s.label}>ডাউনলোড স্পিড (Mbps) *</label>
            <input style={s.input} type="number" value={form.download_speed} onChange={e => setForm({ ...form, download_speed: e.target.value })} placeholder="10" />

            <label style={s.label}>আপলোড স্পিড (Mbps) *</label>
            <input style={s.input} type="number" value={form.upload_speed} onChange={e => setForm({ ...form, upload_speed: e.target.value })} placeholder="5" />

            <label style={s.label}>মূল্য (টাকা) *</label>
            <input style={s.input} type="number" value={form.price} onChange={e => setForm({ ...form, price: e.target.value })} placeholder="500" />

            <label style={s.label}>বিলিং চক্র</label>
            <select style={s.select} value={form.billing_cycle} onChange={e => setForm({ ...form, billing_cycle: e.target.value })}>
              <option value="monthly">মাসিক</option>
              <option value="quarterly">ত্রৈমাসিক</option>
              <option value="yearly">বার্ষিক</option>
            </select>

            <label style={s.label}>বিবরণ</label>
            <input style={s.input} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="প্যাকেজের বিবরণ" />

            <div style={{ marginTop: 14, display: 'flex', gap: 20 }}>
              <label style={{ color: '#94a3b8', fontSize: 13, cursor: 'pointer' }}>
                <input type="checkbox" checked={form.is_active} onChange={e => setForm({ ...form, is_active: e.target.checked })} style={{ marginRight: 6 }} />
                সক্রিয়
              </label>
              <label style={{ color: '#94a3b8', fontSize: 13, cursor: 'pointer' }}>
                <input type="checkbox" checked={form.is_public} onChange={e => setForm({ ...form, is_public: e.target.checked })} style={{ marginRight: 6 }} />
                পাবলিক
              </label>
            </div>

            <div style={s.modalBtns}>
              <button style={{ ...s.btnSm, background: 'rgba(99,102,241,0.15)', color: '#94a3b8', padding: '10px 20px' }} onClick={() => setShowModal(false)}>বাতিল</button>
              <button style={{ ...s.btn }} onClick={handleSave}>{editItem ? 'আপডেট করুন' : 'সংরক্ষণ করুন'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}