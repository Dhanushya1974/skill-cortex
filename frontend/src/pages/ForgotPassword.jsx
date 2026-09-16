import { useState } from "react"
import { Link } from "react-router-dom"
import Navbar from "../components/Navbar"
import { api } from "../services/api"

export default function ForgotPassword() {
  const [email, setEmail] = useState("")
  const [message, setMessage] = useState("")
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      const res = await api.forgotPassword(email)
      setMessage(res.message)
    } catch (err) {
      setMessage(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="mx-auto flex max-w-md flex-col px-6 py-20">
        <h1 className="text-2xl font-bold text-ink">Reset your password</h1>
        <p className="mt-1 text-sm text-ink/60">Enter your account email and we'll send you a reset link.</p>

        {message ? (
          <p className="mt-8 rounded-lg bg-primary/10 px-3 py-2 text-sm text-primary">{message}</p>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div>
              <label className="text-sm font-medium text-ink/70">Email</label>
              <input
                type="email"
                required
                className="mt-1 w-full rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-lg bg-primary py-2.5 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:opacity-60"
            >
              {submitting ? "Sending..." : "Send reset link"}
            </button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-ink/60">
          Remembered it?{" "}
          <Link to="/login" className="font-semibold text-primary">
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}
