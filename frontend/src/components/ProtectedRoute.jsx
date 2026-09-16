import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function ProtectedRoute({ children, requireAdmin = false }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-ink/50">Loading...</div>
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  if (requireAdmin && user.role !== "admin") {
    return <Navigate to="/dashboard" replace />
  }
  return children
}
