import { createContext, useCallback, useContext, useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)

  const persist = (access, refresh) => {
    if (access) localStorage.setItem('access', access)
    else localStorage.removeItem('access')
    if (refresh) localStorage.setItem('refresh', refresh)
    else localStorage.removeItem('refresh')
  }

  const logout = useCallback(() => {
    persist(null, null)
    setUser(null)
  }, [])

  const fetchMe = (token) =>
    fetch(`${API_BASE}/api/auth/me/`, { headers: { Authorization: `Bearer ${token}` } })

  const tryRefresh = async () => {
    const refresh = localStorage.getItem('refresh')
    if (!refresh) return null
    const res = await fetch(`${API_BASE}/api/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    })
    if (!res.ok) return null
    const data = await res.json()
    persist(data.access, refresh)
    return data.access
  }

  // On first load, validate any stored token by fetching the current user.
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      const token = localStorage.getItem('access')
      if (!token) {
        setReady(true)
        return
      }
      try {
        let res = await fetchMe(token)
        if (res.status === 401) {
          const refreshed = await tryRefresh()
          res = refreshed ? await fetchMe(refreshed) : res
        }
        if (res.ok && !cancelled) setUser(await res.json())
        else if (!res.ok) logout()
      } catch {
        /* backend offline — leave logged out */
      }
      if (!cancelled) setReady(true)
    })()
    return () => {
      cancelled = true
    }
  }, [logout])

  const login = async (username, password) => {
    const res = await fetch(`${API_BASE}/api/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!res.ok) throw new Error('Invalid username or password.')
    const data = await res.json()
    persist(data.access, data.refresh)
    const me = await fetchMe(data.access)
    setUser(await me.json())
  }

  const register = async (username, email, password) => {
    const res = await fetch(`${API_BASE}/api/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    })
    const data = await res.json()
    if (!res.ok) {
      const msg =
        data.username?.[0] || data.email?.[0] || data.password?.[0] || 'Could not create account.'
      throw new Error(msg)
    }
    persist(data.access, data.refresh)
    setUser(data.user)
  }

  // Authenticated fetch: attaches the Bearer token and retries once after a
  // refresh on a 401. `path` is API-relative, e.g. "/api/collection/".
  const authFetch = useCallback(
    async (path, options = {}) => {
      const call = (token) =>
        fetch(`${API_BASE}${path}`, {
          ...options,
          headers: {
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        })
      let res = await call(localStorage.getItem('access'))
      if (res.status === 401) {
        const refreshed = await tryRefresh()
        if (refreshed) res = await call(refreshed)
        else logout()
      }
      return res
    },
    [logout]
  )

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
