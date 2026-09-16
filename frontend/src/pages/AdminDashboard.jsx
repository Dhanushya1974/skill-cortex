import { useEffect, useState } from "react"
import DashboardLayout from "../layouts/DashboardLayout"
import StatCard from "../components/StatCard"
import StatusBadge from "../components/StatusBadge"
import DepartmentManager from "../components/admin/DepartmentManager"
import WebinarManager from "../components/admin/WebinarManager"
import { useAuth } from "../context/AuthContext"
import { api } from "../services/api"

const navItems = [
  { label: "Overview", href: "#" },
  { label: "Departments", href: "#departments" },
  { label: "Webinars & Slots", href: "#webinars" },
  { label: "Users", href: "#users" },
  { label: "Bookings", href: "#bookings" },
  { label: "Payments", href: "#payments" },
  { label: "Notifications", href: "#notifications" },
]

export default function AdminDashboard() {
  const { token } = useAuth()
  const [webinars, setWebinars] = useState([])
  const [bookings, setBookings] = useState([])
  const [payments, setPayments] = useState([])
  const [notifications, setNotifications] = useState([])
  const [users, setUsers] = useState([])
  const [departments, setDepartments] = useState([])
  const [reminderMessage, setReminderMessage] = useState("")
  const [loading, setLoading] = useState(true)

  function refreshNotifications() {
    api.listNotifications(token).then(setNotifications).catch(() => {})
  }

  useEffect(() => {
    Promise.allSettled([
      api.listWebinars().then(setWebinars),
      api.listAllBookings(token).then(setBookings),
      api.listPayments(token).then(setPayments),
      api.listUsers(token).then(setUsers),
      api.listAllDepartments(token).then(setDepartments),
      api.listNotifications(token).then(setNotifications),
    ]).finally(() => setLoading(false))
  }, [token])

  const departmentName = (id) => departments.find((d) => d.id === id)?.name ?? "—"

  async function handleRunReminders() {
    setReminderMessage("Checking...")
    try {
      const { sent } = await api.runReminders(token)
      setReminderMessage(`Sent ${sent} reminder${sent === 1 ? "" : "s"}.`)
      refreshNotifications()
    } catch (err) {
      setReminderMessage(err.message)
    }
  }

  const stats = [
    { label: "Total Users", value: users.length },
    { label: "Active Webinars", value: webinars.length },
    { label: "Total Bookings", value: bookings.length },
    { label: "Pending Bookings", value: bookings.filter((b) => b.status === "PENDING").length },
    { label: "Confirmed Bookings", value: bookings.filter((b) => b.status === "CONFIRMED").length },
  ]

  if (loading) {
    return (
      <DashboardLayout title="Admin Overview" navItems={navItems}>
        <div className="flex items-center justify-center py-24 text-sm text-ink/40">Loading admin overview...</div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title="Admin Overview" navItems={navItems}>
      <div className="space-y-10">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {stats.map((s) => (
            <StatCard key={s.label} label={s.label} value={s.value} />
          ))}
        </div>

        <section id="departments">
          <h2 className="text-base font-bold text-ink">Departments</h2>
          <div className="mt-4">
            <DepartmentManager />
          </div>
        </section>

        <section id="webinars">
          <h2 className="text-base font-bold text-ink">Webinars & Slots</h2>
          <div className="mt-4">
            <WebinarManager />
          </div>
        </section>

        <section id="users">
          <h2 className="text-base font-bold text-ink">Users</h2>
          <div className="mt-4 overflow-hidden rounded-xl border border-black/5 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface text-ink/50">
                <tr>
                  <th className="px-5 py-3 font-medium">Name</th>
                  <th className="px-5 py-3 font-medium">Email</th>
                  <th className="px-5 py-3 font-medium">Phone</th>
                  <th className="px-5 py-3 font-medium">Department</th>
                  <th className="px-5 py-3 font-medium">Role</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-t border-black/5">
                    <td className="px-5 py-4 font-medium text-ink">{u.name}</td>
                    <td className="px-5 py-4 text-ink/70">{u.email}</td>
                    <td className="px-5 py-4 text-ink/50">{u.phone}</td>
                    <td className="px-5 py-4 text-ink/70">{departmentName(u.department_id)}</td>
                    <td className="px-5 py-4 text-ink/70">{u.role}</td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-5 py-6 text-center text-ink/40">
                      No users yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section id="bookings">
          <h2 className="text-base font-bold text-ink">Recent bookings</h2>
          <div className="mt-4 overflow-hidden rounded-xl border border-black/5 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface text-ink/50">
                <tr>
                  <th className="px-5 py-3 font-medium">User</th>
                  <th className="px-5 py-3 font-medium">Webinar</th>
                  <th className="px-5 py-3 font-medium">Slot</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((b) => (
                  <tr key={b.id} className="border-t border-black/5">
                    <td className="px-5 py-4 font-medium text-ink">{b.user.name}</td>
                    <td className="px-5 py-4 text-ink/70">{b.webinar.title}</td>
                    <td className="px-5 py-4 text-ink/50">
                      {b.slot.date} · {b.slot.start_time}–{b.slot.end_time}
                    </td>
                    <td className="px-5 py-4"><StatusBadge status={b.status} /></td>
                  </tr>
                ))}
                {bookings.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-5 py-6 text-center text-ink/40">
                      No bookings yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section id="payments">
          <h2 className="text-base font-bold text-ink">Recent payments</h2>
          <div className="mt-4 overflow-hidden rounded-xl border border-black/5 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface text-ink/50">
                <tr>
                  <th className="px-5 py-3 font-medium">User</th>
                  <th className="px-5 py-3 font-medium">Razorpay ID</th>
                  <th className="px-5 py-3 font-medium">Amount</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.id} className="border-t border-black/5">
                    <td className="px-5 py-4 font-medium text-ink">{p.booking.user.name}</td>
                    <td className="px-5 py-4 font-mono text-xs text-ink/50">{p.razorpay_payment_id ?? p.razorpay_order_id}</td>
                    <td className="px-5 py-4 text-ink/70">₹{p.amount}</td>
                    <td className="px-5 py-4"><StatusBadge status={p.status} /></td>
                  </tr>
                ))}
                {payments.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-5 py-6 text-center text-ink/40">
                      No payments yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section id="notifications">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-ink">Notification history</h2>
            <div className="flex items-center gap-3">
              {reminderMessage && <span className="text-xs text-ink/50">{reminderMessage}</span>}
              <button
                onClick={handleRunReminders}
                className="rounded-lg bg-ink px-3 py-1.5 text-xs font-semibold text-white hover:bg-ink/80"
              >
                Run reminders now
              </button>
            </div>
          </div>
          <p className="mt-1 text-xs text-ink/40">
            Reminders also run automatically once a day (3 days, 1 day, and day-of before each confirmed webinar).
          </p>
          <div className="mt-4 overflow-hidden rounded-xl border border-black/5 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface text-ink/50">
                <tr>
                  <th className="px-5 py-3 font-medium">Recipient</th>
                  <th className="px-5 py-3 font-medium">Type</th>
                  <th className="px-5 py-3 font-medium">Channel</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {notifications.map((n) => (
                  <tr key={n.id} className="border-t border-black/5">
                    <td className="px-5 py-4 font-medium text-ink">{n.user.name}</td>
                    <td className="px-5 py-4 text-ink/70">{n.type.replaceAll("_", " ")}</td>
                    <td className="px-5 py-4 text-ink/50">{n.channel}</td>
                    <td className="px-5 py-4"><StatusBadge status={n.status} /></td>
                  </tr>
                ))}
                {notifications.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-5 py-6 text-center text-ink/40">
                      No notifications yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </DashboardLayout>
  )
}
