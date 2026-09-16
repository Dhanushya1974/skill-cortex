import { useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import Navbar from "../components/Navbar"
import { api } from "../services/api"

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get("token") ?? ""
  const navigate = useNavigate()
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [done, setDone] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError("")
    setSubmitting(true)
    try {
      await api.resetPassword({ token, new_password: password })
      setDone(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="mx-auto flex max-w-md flex-col px-6 py-20">
        <h1 className="text-2xl font-bold text-ink">Set a new password</h1>

        {!token && (
          <p className="mt-6 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            This link is missing its reset token. Request a new one from the forgot-password page.
          </p>
        )}

        {token && done && (
          <div className="mt-8">
            <p className="rounded-lg bg-primary/10 px-3 py-2 text-sm text-primary">
              Password updated. You can log in with your new password now.
            </p>
            <button
              onClick={() => navigate("/login")}
              className="mt-4 w-full rounded-lg bg-primary py-2.5 text-sm font-semibold text-white transition hover:bg-primary-dark"
            >
              Go to login
            </button>
          </div>
        )}

        {token && !done && (
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
            <div>
              <label className="text-sm font-medium text-ink/70">New password</label>
              <input
                type="password"
                required
                minLength={8}
                className="mt-1 w-full rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-lg bg-primary py-2.5 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:opacity-60"
            >
              {submitting ? "Updating..." : "Update password"}
            </button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-ink/60">
          <Link to="/login" className="font-semibold text-primary">
            Back to login
          </Link>
        </p>
      </div>
    </div>
  )
}
