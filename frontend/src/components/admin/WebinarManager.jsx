import { useEffect, useState } from "react"
import { useAuth } from "../../context/AuthContext"
import { api } from "../../services/api"

const emptyWebinarForm = { title: "", description: "", department_id: "", price: "", duration_minutes: "" }
const emptySlotForm = { date: "", start_time: "", end_time: "", capacity: "" }

export default function WebinarManager() {
  const { token } = useAuth()
  const [departments, setDepartments] = useState([])
  const [webinars, setWebinars] = useState([])
  const [expandedId, setExpandedId] = useState(null)
  const [webinarDetails, setWebinarDetails] = useState({})
  const [webinarForm, setWebinarForm] = useState(emptyWebinarForm)
  const [slotForm, setSlotForm] = useState(emptySlotForm)
  const [error, setError] = useState("")

  function refreshWebinars() {
    api.listAllWebinars(token).then(setWebinars).catch(() => {})
  }

  useEffect(() => {
    api.listDepartments().then((depts) => {
      setDepartments(depts)
      setWebinarForm((f) => ({ ...f, department_id: depts[0] ? String(depts[0].id) : "" }))
    })
    refreshWebinars()
  }, [token])

  async function handleCreateWebinar(e) {
    e.preventDefault()
    setError("")
    try {
      await api.createWebinar(
        {
          ...webinarForm,
          department_id: Number(webinarForm.department_id),
          price: Number(webinarForm.price),
          duration_minutes: Number(webinarForm.duration_minutes),
        },
        token,
      )
      setWebinarForm((f) => ({ ...emptyWebinarForm, department_id: f.department_id }))
      refreshWebinars()
    } catch (err) {
      setError(err.message)
    }
  }

  async function toggleExpand(webinarId) {
    if (expandedId === webinarId) {
      setExpandedId(null)
      return
    }
    setExpandedId(webinarId)
    if (!webinarDetails[webinarId]) {
      const detail = await api.getWebinar(webinarId)
      setWebinarDetails((d) => ({ ...d, [webinarId]: detail }))
    }
  }

  async function handleCreateSlot(e, webinarId) {
    e.preventDefault()
    setError("")
    try {
      await api.createSlot(webinarId, { ...slotForm, capacity: Number(slotForm.capacity) }, token)
      const detail = await api.getWebinar(webinarId)
      setWebinarDetails((d) => ({ ...d, [webinarId]: detail }))
      setSlotForm(emptySlotForm)
    } catch (err) {
      setError(err.message)
    }
  }

  async function toggleWebinarActive(w) {
    setError("")
    try {
      await api.updateWebinar(w.id, { is_active: !w.is_active }, token)
      refreshWebinars()
    } catch (err) {
      setError(err.message)
    }
  }

  async function toggleSlotActive(webinarId, slot) {
    setError("")
    try {
      await api.updateSlot(slot.id, { is_active: !slot.is_active }, token)
      const detail = await api.getWebinar(webinarId)
      setWebinarDetails((d) => ({ ...d, [webinarId]: detail }))
    } catch (err) {
      setError(err.message)
    }
  }

  const departmentName = (id) => departments.find((d) => d.id === id)?.name ?? "—"

  return (
    <div className="space-y-6">
      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}

      <form onSubmit={handleCreateWebinar} className="grid gap-3 rounded-xl border border-black/5 bg-white p-5 shadow-sm md:grid-cols-6">
        <input
          required
          placeholder="Title"
          className="rounded-lg border border-black/10 px-3 py-2 text-sm md:col-span-2"
          value={webinarForm.title}
          onChange={(e) => setWebinarForm({ ...webinarForm, title: e.target.value })}
        />
        <input
          placeholder="Description"
          className="rounded-lg border border-black/10 px-3 py-2 text-sm md:col-span-2"
          value={webinarForm.description}
          onChange={(e) => setWebinarForm({ ...webinarForm, description: e.target.value })}
        />
        <select
          className="rounded-lg border border-black/10 px-3 py-2 text-sm"
          value={webinarForm.department_id}
          onChange={(e) => setWebinarForm({ ...webinarForm, department_id: e.target.value })}
        >
          {departments.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
        <input
          required
          type="number"
          min="0"
          placeholder="Price ₹"
          className="rounded-lg border border-black/10 px-3 py-2 text-sm"
          value={webinarForm.price}
          onChange={(e) => setWebinarForm({ ...webinarForm, price: e.target.value })}
        />
        <input
          required
          type="number"
          min="1"
          placeholder="Duration (min)"
          className="rounded-lg border border-black/10 px-3 py-2 text-sm md:col-span-2"
          value={webinarForm.duration_minutes}
          onChange={(e) => setWebinarForm({ ...webinarForm, duration_minutes: e.target.value })}
        />
        <button
          type="submit"
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-dark md:col-span-4"
        >
          Create webinar
        </button>
      </form>

      <div className="space-y-3">
        {webinars.map((w) => (
          <div key={w.id} className={`rounded-xl border border-black/5 bg-white shadow-sm ${w.is_active ? "" : "opacity-50"}`}>
            <div className="flex w-full items-center justify-between px-5 py-4">
              <button onClick={() => toggleExpand(w.id)} className="flex-1 text-left">
                <p className="font-semibold text-ink">
                  {w.title} {!w.is_active && <span className="text-xs font-normal text-slate-500">(inactive)</span>}
                </p>
                <p className="text-xs text-ink/50">
                  {departmentName(w.department_id)} · ₹{w.price} · {w.duration_minutes} min
                </p>
              </button>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => toggleWebinarActive(w)}
                  className="text-xs font-semibold text-primary hover:underline"
                >
                  {w.is_active ? "Deactivate" : "Activate"}
                </button>
                <button onClick={() => toggleExpand(w.id)} className="text-sm text-primary">
                  {expandedId === w.id ? "Hide slots" : "Manage slots"}
                </button>
              </div>
            </div>

            {expandedId === w.id && (
              <div className="border-t border-black/5 px-5 py-4">
                <ul className="space-y-1.5 text-sm text-ink/70">
                  {(webinarDetails[w.id]?.slots ?? []).map((s) => (
                    <li key={s.id} className="flex items-center justify-between">
                      <span className={s.is_active ? "" : "text-ink/30 line-through"}>
                        {s.date} · {s.start_time}–{s.end_time} · {s.available_seats}/{s.capacity} seats
                      </span>
                      <button
                        onClick={() => toggleSlotActive(w.id, s)}
                        className="text-xs font-semibold text-primary hover:underline"
                      >
                        {s.is_active ? "Cancel" : "Reactivate"}
                      </button>
                    </li>
                  ))}
                  {webinarDetails[w.id]?.slots?.length === 0 && (
                    <li className="text-ink/40">No slots yet.</li>
                  )}
                </ul>

                <form onSubmit={(e) => handleCreateSlot(e, w.id)} className="mt-4 grid gap-2 md:grid-cols-5">
                  <input
                    required
                    type="date"
                    className="rounded-lg border border-black/10 px-2 py-1.5 text-sm"
                    value={slotForm.date}
                    onChange={(e) => setSlotForm({ ...slotForm, date: e.target.value })}
                  />
                  <input
                    required
                    type="time"
                    className="rounded-lg border border-black/10 px-2 py-1.5 text-sm"
                    value={slotForm.start_time}
                    onChange={(e) => setSlotForm({ ...slotForm, start_time: e.target.value })}
                  />
                  <input
                    required
                    type="time"
                    className="rounded-lg border border-black/10 px-2 py-1.5 text-sm"
                    value={slotForm.end_time}
                    onChange={(e) => setSlotForm({ ...slotForm, end_time: e.target.value })}
                  />
                  <input
                    required
                    type="number"
                    min="1"
                    placeholder="Capacity"
                    className="rounded-lg border border-black/10 px-2 py-1.5 text-sm"
                    value={slotForm.capacity}
                    onChange={(e) => setSlotForm({ ...slotForm, capacity: e.target.value })}
                  />
                  <button
                    type="submit"
                    className="rounded-lg bg-ink px-3 py-1.5 text-sm font-semibold text-white hover:bg-ink/80"
                  >
                    Add slot
                  </button>
                </form>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
