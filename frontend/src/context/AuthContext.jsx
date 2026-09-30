import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [token, setToken]     = useState(() => localStorage.getItem('voyage_token'))
  const [loading, setLoading] = useState(true)

  // Fetch current user profile when token is available
  const fetchProfile = useCallback(async () => {
    if (!token) { setLoading(false); return }
    try {
      const { data } = await api.get('/user/profile')
      setUser(data)
    } catch {
      setToken(null)
      localStorage.removeItem('voyage_token')
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => { fetchProfile() }, [fetchProfile])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('voyage_token', data.access_token)
    setToken(data.access_token)
    const profile = await api.get('/user/profile', {
      headers: { Authorization: `Bearer ${data.access_token}` },
    })
    setUser(profile.data)
    return data
  }

  const register = async (payload) => {
    const { data } = await api.post('/auth/register', payload)
    localStorage.setItem('voyage_token', data.access_token)
    setToken(data.access_token)
    const profile = await api.get('/user/profile', {
      headers: { Authorization: `Bearer ${data.access_token}` },
    })
    setUser(profile.data)
    return data
  }

  const logout = () => {
    localStorage.removeItem('voyage_token')
    setToken(null)
    setUser(null)
    toast.success('Logged out successfully')
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
