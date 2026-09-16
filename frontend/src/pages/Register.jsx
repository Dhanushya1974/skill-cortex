import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import Navbar from "../components/Navbar"
import { useAuth } from "../context/AuthContext"
import { api } from "../services/api"

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [departments, setDepartments] = useState([])
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "", department_id: "", department_other: "" })
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const selectedDepartment = departments.find((d) => String(d.id) === String(form.department_id))
  const isOtherSelected = selectedDepartment?.name === "Other"

  useEffect(() => {
    api
      .listDepartments()
      .then((depts) => {
        setDepartments(depts)
        if (depts.length) setForm((f) => ({ ...f, department_id: String(depts[0].id) }))
      })
      .catch(() => setError("Could not load departments. Is the backend running?"))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError("")
    setSubmitting(true)
    try {
      const user = await register({
        ...form,
        department_id: Number(form.department_id),
        department_other: isOtherSelected ? form.department_other.trim() : null,
      })
      navigate(user.role === "admin" ? "/admin" : "/dashboard")
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="mx-auto flex max-w-md flex-col px-6 py-16">
        <h1 className="text-2xl font-bold text-ink">Create your account</h1>
        <p className="mt-1 text-sm text-ink/60">Pick your department to see relevant webinars.</p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
          <div>
            <label className="text-sm font-medium text-ink/70">Full name</label>
            <input
              required
              className="mt-1 w-full rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-ink/70">Email</label>
            <input
              type="email"
              required
              className="mt-1 w-full rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-ink/70">Mobile number</label>
            <input
              required
              className="mt-1 w-full rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-ink/70">Department</label>
            <select
              required
              className="mt-1 w-full rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
              value={form.department_id}
              onChange={(e) => setForm({ ...form, department_id: e.target.value })}
            >
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
          {isOtherSelected && (
            <div>
              <label className="text-sm font-medium text-ink/70">Please specify your department</label>
              <textarea
                required
                rows={3}
                className="mt-1 w-full rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
                value={form.department_other}
                onChange={(e) => setForm({ ...form, department_other: e.target.value })}
              />
            </div>
          )}
          <div>
            <label className="text-sm font-medium text-ink/70">Password</label>
            <input
              type="password"
              required
              minLength={8}
              className="mt-1 w-full rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-primary py-2.5 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:opacity-60"
          >
            {submitting ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-ink/60">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-primary">
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}
