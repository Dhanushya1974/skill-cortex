import { useEffect, useState } from "react"
import { useAuth } from "../../context/AuthContext"
import { api } from "../../services/api"

export default function DepartmentManager() {
  const { token } = useAuth()
  const [departments, setDepartments] = useState([])
  const [form, setForm] = useState({ name: "", description: "" })
  const [error, setError] = useState("")

  function refresh() {
    api.listAllDepartments(token).then(setDepartments).catch(() => {})
  }

  useEffect(refresh, [token])

  async function handleSubmit(e) {
    e.preventDefault()
    setError("")
    try {
      await api.createDepartment(form, token)
      setForm({ name: "", description: "" })
      refresh()
    } catch (err) {
      setError(err.message)
    }
  }

  async function toggleActive(d) {
    setError("")
    try {
      await api.updateDepartment(d.id, { is_active: !d.is_active }, token)
      refresh()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-4">
      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
      <div className="grid gap-4 md:grid-cols-3">
        {departments.map((d) => (
          <div
            key={d.id}
            className={`rounded-xl border border-black/5 bg-white p-5 shadow-sm ${d.is_active ? "" : "opacity-50"}`}
          >
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold text-ink">{d.name}</h3>
              {!d.is_active && (
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600">
                  Inactive
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-ink/60">{d.description}</p>
            <button
              onClick={() => toggleActive(d)}
              className="mt-3 text-xs font-semibold text-primary hover:underline"
            >
              {d.is_active ? "Deactivate" : "Activate"}
            </button>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-2 rounded-xl border border-black/5 bg-white p-4 shadow-sm">
        <input
          required
          placeholder="Department name"
          className="flex-1 rounded-lg border border-black/10 px-3 py-2 text-sm"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <input
          placeholder="Description"
          className="flex-[2] rounded-lg border border-black/10 px-3 py-2 text-sm"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <button className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary-dark">
          Add department
        </button>
      </form>
    </div>
  )
}
