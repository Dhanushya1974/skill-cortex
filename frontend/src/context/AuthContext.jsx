import { createContext, useContext, useEffect, useState } from "react"
import { api } from "../services/api"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("sc_token"))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(token))

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }
    api
      .me(token)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("sc_token")
        setToken(null)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [token])

  async function login(email, password) {
    const { access_token } = await api.login({ email, password })
    localStorage.setItem("sc_token", access_token)
    setToken(access_token)
    const me = await api.me(access_token)
    setUser(me)
    return me
  }

  async function register(payload) {
    await api.register(payload)
    return login(payload.email, payload.password)
  }

  function logout() {
    localStorage.removeItem("sc_token")
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
