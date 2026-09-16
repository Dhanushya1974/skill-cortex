import { useEffect, useState } from "react"
import DashboardLayout from "../layouts/DashboardLayout"
import StatusBadge from "../components/StatusBadge"
import { useAuth } from "../context/AuthContext"
import { api } from "../services/api"

const navItems = [
  { label: "My Bookings", href: "#" },
  { label: "Browse Webinars", href: "#browse" },
  { label: "Notifications", href: "#notifications" },
  { label: "Profile", href: "#profile" },
]

export default function UserDashboard() {
  const { token, user } = useAuth()
  const [bookings, setBookings] = useState([])
  const [webinars, setWebinars] = useState([])
  const [notifications, setNotifications] = useState([])
  const [departments, setDepartments] = useState([])
  const [expandedId, setExpandedId] = useState(null)
  const [webinarDetails, setWebinarDetails] = useState({})
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)

  function refreshBookings() {
    api.myBookings(token).then(setBookings).catch(() => {})
  }

  function refreshNotifications() {
    api.myNotifications(token).then(setNotifications).catch(() => {})
  }

  useEffect(() => {
    Promise.allSettled([
      api.listWebinars().then(setWebinars),
      api.listDepartments().then(setDepartments),
      api.myBookings(token).then(setBookings),
      api.myNotifications(token).then(setNotifications),
    ]).finally(() => setLoading(false))
  }, [])

  const departmentName = (id) => departments.find((d) => d.id === id)?.name ?? "—"

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

  async function handleBook(webinarId, slotId) {
    setMessage("")
    try {
      await api.createBooking({ webinar_id: webinarId, slot_id: slotId }, token)
      const detail = await api.getWebinar(webinarId)
      setWebinarDetails((d) => ({ ...d, [webinarId]: detail }))
      refreshBookings()
      setMessage("Slot booked! Pay now to confirm it.")
    } catch (err) {
      setMessage(err.message)
    }
  }

  async function handlePay(booking) {
    setMessage("")
    if (!window.Razorpay) {
      setMessage("Payment gateway failed to load. Check your connection and try again.")
      return
    }
    try {
      const order = await api.createOrder(booking.id, token)
      const checkout = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        order_id: order.order_id,
        name: "Skill Cortex",
        description: booking.webinar.title,
        prefill: { name: user?.name, email: user?.email },
        theme: { color: "#F5821F" },
        handler: async (response) => {
          try {
            await api.verifyPayment(
              {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              },
              token,
            )
            refreshBookings()
            refreshNotifications()
            setMessage("Payment verified — booking confirmed!")
          } catch (err) {
            setMessage(err.message)
          }
        },
        modal: {
          ondismiss: () => setMessage("Payment cancelled."),
        },
      })
      checkout.on("payment.failed", () => setMessage("Payment failed. Please try again."))
      checkout.open()
    } catch (err) {
      setMessage(err.message)
    }
  }

  if (loading) {
    return (
      <DashboardLayout title="My Bookings" navItems={navItems}>
        <div className="flex items-center justify-center py-24 text-sm text-ink/40">Loading your dashboard...</div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title="My Bookings" navItems={navItems}>
      <div className="space-y-8">
        {message && <p className="rounded-lg bg-primary/10 px-3 py-2 text-sm text-primary">{message}</p>}

        <div className="overflow-hidden rounded-xl border border-black/5 bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-ink/50">
              <tr>
                <th className="px-5 py-3 font-medium">Webinar</th>
                <th className="px-5 py-3 font-medium">Slot</th>
                <th className="px-5 py-3 font-medium">Booking</th>
                <th className="px-5 py-3 font-medium">Amount</th>
                <th className="px-5 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => (
                <tr key={b.id} className="border-t border-black/5">
                  <td className="px-5 py-4 font-medium text-ink">{b.webinar.title}</td>
                  <td className="px-5 py-4 text-ink/60">
                    {b.slot.date} · {b.slot.start_time}–{b.slot.end_time}
                  </td>
                  <td className="px-5 py-4"><StatusBadge status={b.status} /></td>
                  <td className="px-5 py-4 text-ink/80">₹{b.webinar.price}</td>
                  <td className="px-5 py-4">
                    {b.status === "PENDING" && (
                      <button
                        onClick={() => handlePay(b)}
                        className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-primary-dark"
                      >
                        Pay Now
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {bookings.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-5 py-6 text-center text-ink/40">
                    No bookings yet — browse webinars below.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div id="browse">
          <h2 className="text-base font-bold text-ink">Browse more webinars</h2>
          <div className="mt-4 space-y-3">
            {webinars.map((w) => (
              <div key={w.id} className="rounded-xl border border-black/5 bg-white shadow-sm">
                <button
                  onClick={() => toggleExpand(w.id)}
                  className="flex w-full items-center justify-between px-5 py-4 text-left"
                >
                  <div>
                    <p className="font-semibold text-ink">{w.title}</p>
                    <p className="text-xs text-ink/50">
                      ₹{w.price} · {w.duration_minutes} min
                    </p>
                  </div>
                  <span className="text-sm text-primary">{expandedId === w.id ? "Hide slots" : "View slots"}</span>
                </button>

                {expandedId === w.id && (
                  <div className="border-t border-black/5 px-5 py-4">
                    <p className="mb-3 text-sm text-ink/60">{w.description}</p>
                    <ul className="space-y-2">
                      {(webinarDetails[w.id]?.slots ?? [])
                        .filter((s) => s.is_active)
                        .map((s) => (
                          <li key={s.id} className="flex items-center justify-between text-sm">
                            <span className="text-ink/70">
                              {s.date} · {s.start_time}–{s.end_time} ({s.available_seats}/{s.capacity} seats)
                            </span>
                            <button
                              disabled={s.available_seats === 0}
                              onClick={() => handleBook(w.id, s.id)}
                              className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-40"
                            >
                              {s.available_seats === 0 ? "Full" : "Book Slot"}
                            </button>
                          </li>
                        ))}
                      {(webinarDetails[w.id]?.slots ?? []).filter((s) => s.is_active).length === 0 && (
                        <li className="text-sm text-ink/40">No slots scheduled yet.</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div id="notifications">
          <h2 className="text-base font-bold text-ink">Notifications</h2>
          <div className="mt-4 overflow-hidden rounded-xl border border-black/5 bg-white shadow-sm">
            <ul className="divide-y divide-black/5">
              {notifications.map((n) => (
                <li key={n.id} className="flex items-start justify-between gap-4 px-5 py-4 text-sm">
                  <div>
                    <p className="font-medium text-ink">{n.type.replaceAll("_", " ")}</p>
                    <p className="mt-0.5 text-ink/60">{n.message}</p>
                  </div>
                  <StatusBadge status={n.status} />
                </li>
              ))}
              {notifications.length === 0 && (
                <li className="px-5 py-6 text-center text-ink/40">No notifications yet.</li>
              )}
            </ul>
          </div>
        </div>

        <div id="profile">
          <h2 className="text-base font-bold text-ink">Profile</h2>
          <div className="mt-4 grid gap-4 rounded-xl border border-black/5 bg-white p-5 shadow-sm sm:grid-cols-2">
            <div>
              <p className="text-xs text-ink/50">Name</p>
              <p className="mt-0.5 text-sm font-medium text-ink">{user?.name}</p>
            </div>
            <div>
              <p className="text-xs text-ink/50">Email</p>
              <p className="mt-0.5 text-sm font-medium text-ink">{user?.email}</p>
            </div>
            <div>
              <p className="text-xs text-ink/50">Phone</p>
              <p className="mt-0.5 text-sm font-medium text-ink">{user?.phone}</p>
            </div>
            <div>
              <p className="text-xs text-ink/50">Department</p>
              <p className="mt-0.5 text-sm font-medium text-ink">{departmentName(user?.department_id)}</p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
