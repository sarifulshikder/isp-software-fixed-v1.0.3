import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

// Decode a JWT payload safely. Handles base64url, padding, and unicode.
function decodeJwt(token) {
  try {
    const part = token.split('.')[1]
    if (!part) return {}
    const b64 = part.replace(/-/g, '+').replace(/_/g, '/')
    const padded = b64 + '==='.slice((b64.length + 3) % 4)
    const json = decodeURIComponent(
      atob(padded)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(json)
  } catch {
    return {}
  }
}

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      refreshToken: null,
      user: null,

      login: async (email, password) => {
        const res = await api.post('/auth/login/', { email, password })
        const access = res.data.access
        const refresh = res.data.refresh
        const payload = decodeJwt(access)
        const user = res.data.user || {
          id: payload.user_id,
          email: payload.email || email,
          full_name: payload.full_name || '',
          role: payload.role || 'customer',
          is_staff: !!payload.is_staff,
        }
        set({ token: access, refreshToken: refresh, user })
        api.defaults.headers.common['Authorization'] = `Bearer ${access}`
        return res.data
      },

      logout: async () => {
        try {
          await api.post('/auth/logout/', { refresh: get().refreshToken })
        } catch (_) {}
        set({ token: null, refreshToken: null, user: null })
        delete api.defaults.headers.common['Authorization']
      },

      setToken: (token) => {
        set({ token })
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      },
    }),
    {
      name: 'isp-auth',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
)
