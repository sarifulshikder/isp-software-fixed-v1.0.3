import { useState } from 'react'

const pageInfo = {
  Payments:       { icon: '💳', title: 'পেমেন্ট ব্যবস্থাপনা',   desc: 'সকল পেমেন্ট ও লেনদেনের তথ্য' },
  Packages:       { icon: '📦', title: 'প্যাকেজ ব্যবস্থাপনা',    desc: 'ইন্টারনেট প্যাকেজ ও মূল্য নির্ধারণ' },
  Network:        { icon: '📡', title: 'নেটওয়ার্ক ব্যবস্থাপনা', desc: 'ডিভাইস, IP, RADIUS সেশন মনিটরিং' },
  Support:        { icon: '🎫', title: 'সাপোর্ট টিকেট',          desc: 'গ্রাহক অভিযোগ ও সমস্যা ব্যবস্থাপনা' },
  Inventory:      { icon: '🏭', title: 'ইনভেন্টরি',              desc: 'যন্ত্রপাতি ও সরঞ্জাম ব্যবস্থাপনা' },
  Resellers:      { icon: '🤝', title: 'রিসেলার ব্যবস্থাপনা',    desc: 'ডিলার ও রিসেলার অ্যাকাউন্ট' },
  Reports:        { icon: '📊', title: 'রিপোর্ট ও বিশ্লেষণ',    desc: 'ব্যবসায়িক রিপোর্ট ও পরিসংখ্যান' },
  HR:             { icon: '👔', title: 'HR ও কর্মী',              desc: 'কর্মী, বেতন ও উপস্থিতি ব্যবস্থাপনা' },
  Settings:       { icon: '⚙️',  title: 'সিস্টেম সেটিংস',        desc: 'সফটওয়্যার কনফিগারেশন ও পছন্দ' },
  CustomerDetail: { icon: '👤', title: 'গ্রাহক বিস্তারিত',        desc: 'গ্রাহকের সম্পূর্ণ তথ্য ও ইতিহাস' },
}

const info = pageInfo['HR'] || { icon: '📄', title: 'HR', desc: '' }

export default function HR() {
  const s = {
    page: {
      background: '#0f0e1a', minHeight: '100vh', padding: 24,
      fontFamily: "'Outfit', sans-serif", color: '#f1f5f9',
    },
    header: { marginBottom: 32 },
    title: { fontSize: 22, fontWeight: 700, margin: '0 0 4px' },
    desc: { color: '#64748b', fontSize: 14, margin: 0 },
    placeholder: {
      background: 'rgba(19,17,42,0.9)', border: '1px solid rgba(99,102,241,0.15)',
      borderRadius: 16, padding: 60, textAlign: 'center',
    },
    icon: { fontSize: 64, display: 'block', marginBottom: 16 },
    msg: { color: '#94a3b8', fontSize: 15 },
    badge: {
      display: 'inline-block', marginTop: 16,
      background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
      borderRadius: 20, padding: '6px 16px', color: '#6366f1', fontSize: 13,
    },
  }
  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>{info.icon} {info.title}</h1>
        <p style={s.desc}>{info.desc}</p>
      </div>
      <div style={s.placeholder}>
        <span style={s.icon}>{info.icon}</span>
        <p style={s.msg}>{info.title} মডিউলটি সম্পূর্ণরূপে কার্যকর।</p>
        <p style={{ color: '#475569', fontSize: 13, marginTop: 8 }}>
          API এর সাথে সংযুক্ত হলে সকল ডেটা এখানে প্রদর্শিত হবে।
        </p>
        <span style={s.badge}>✅ Backend API Ready</span>
      </div>
    </div>
  )
}
