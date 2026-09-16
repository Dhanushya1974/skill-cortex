import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import Navbar from "../components/Navbar"
import Footer from "../components/Footer"
import { api } from "../services/api"

export default function Landing() {
  const [departments, setDepartments] = useState([])
  const [webinars, setWebinars] = useState([])

  useEffect(() => {
    api.listDepartments().then(setDepartments).catch(() => {})
    api.listWebinars().then(setWebinars).catch(() => {})
  }, [])

  const departmentName = (id) => departments.find((d) => d.id === id)?.name ?? ""

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <Navbar />

      <section className="relative overflow-hidden bg-ink text-white">
        <div className="absolute inset-0 bg-gradient-to-br from-ink via-ink/95 to-primary/30" />
        <div className="relative mx-auto flex max-w-6xl flex-col items-start gap-6 px-6 py-24">
          <span className="rounded-full bg-primary/20 px-4 py-1 text-sm font-semibold text-primary">
            Your journey into tech industry starts here
          </span>
          <h1 className="max-w-2xl text-4xl font-bold leading-tight md:text-5xl">
            Empower your career with <span className="text-primary">industry-aligned tech solutions</span> &
            real-world experience.
          </h1>
          <p className="max-w-xl text-lg text-white/70">
            We deliver IT services, digital product operations, and project-based learning solutions that
            empower individuals to gain real industry exposure and create meaningful impact in the tech
            sector.
          </p>
          <div className="flex gap-4">
            <Link
              to="/dashboard"
              className="rounded-lg bg-primary px-6 py-3 font-semibold text-white shadow-lg transition hover:bg-primary-dark"
            >
              Explore Services & Internships
            </Link>
            <a
              href="#departments"
              className="rounded-lg border border-white/30 px-6 py-3 font-semibold text-white transition hover:bg-white/10"
            >
              Browse Departments
            </a>
          </div>
        </div>
      </section>

      <section id="about" className="mx-auto w-full max-w-6xl px-6 py-20">
        <div className="grid gap-10 md:grid-cols-2 md:items-center">
          <div>
            <span className="text-sm font-semibold uppercase tracking-wide text-primary">About Skill Cortex</span>
            <h2 className="mt-2 text-2xl font-bold text-ink">One platform for every step of your webinar journey</h2>
            <p className="mt-4 text-ink/60">
              Skill Cortex brings together department-wise course discovery, slot booking, secure Razorpay
              payments, and automatic confirmations and reminders — so you never have to chase an admin
              for a booking status again.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[
              ["Verified payments", "Every payment is confirmed on our backend, never just the checkout popup."],
              ["Zero double-booking", "Slot capacity is enforced in real time."],
              ["Automatic reminders", "3 days, 1 day, and day-of — no manual follow-up."],
              ["Admin visibility", "Full tracking of bookings, payments and notifications."],
            ].map(([title, body]) => (
              <div key={title} className="rounded-xl bg-surface p-4">
                <h3 className="text-sm font-semibold text-ink">{title}</h3>
                <p className="mt-1 text-xs text-ink/60">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="departments" className="mx-auto w-full max-w-6xl px-6 py-20">
        <h2 className="text-2xl font-bold text-ink">Select your department</h2>
        <p className="mt-2 text-ink/60">Webinars are organized by department so you see what's relevant to you.</p>
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          {departments.map((d) => (
            <div key={d.id} className="rounded-xl border border-black/5 bg-surface p-6 transition hover:shadow-lg">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 font-bold text-primary">
                {d.name[0]}
              </div>
              <h3 className="mt-4 font-semibold text-ink">{d.name}</h3>
              <p className="mt-1 text-sm text-ink/60">{d.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="webinars" className="bg-surface py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-2xl font-bold text-ink">Upcoming webinars</h2>
          <p className="mt-2 text-ink/60">Choose a slot, pay through Razorpay, get confirmed instantly.</p>
          <div className="mt-8 grid gap-6 md:grid-cols-3">
            {webinars.map((w) => (
              <div key={w.id} className="flex flex-col rounded-xl bg-white p-6 shadow-sm ring-1 ring-black/5">
                <span className="text-xs font-semibold uppercase tracking-wide text-primary">
                  {departmentName(w.department_id)}
                </span>
                <h3 className="mt-2 text-lg font-bold text-ink">{w.title}</h3>
                <p className="mt-2 flex-1 text-sm text-ink/60">{w.description}</p>
                <div className="mt-4 flex items-center justify-between text-sm text-ink/50">
                  <span>{w.duration_minutes} min</span>
                  <span className="font-semibold text-ink">₹{w.price}</span>
                </div>
                <Link
                  to="/dashboard"
                  className="mt-4 rounded-lg bg-primary py-2 text-center text-sm font-semibold text-white transition hover:bg-primary-dark"
                >
                  Book Slot
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-6xl px-6 py-20">
        <h2 className="text-2xl font-bold text-ink">Why book through Skill Cortex</h2>
        <div className="mt-8 grid gap-6 md:grid-cols-4">
          {[
            ["Discover", "Browse webinars by department in one place."],
            ["Book instantly", "Pick a live slot with real-time seat availability."],
            ["Pay securely", "Razorpay checkout, verified server-side before confirming."],
            ["Never miss it", "Automatic reminders leading up to your session."],
          ].map(([title, body]) => (
            <div key={title} className="rounded-xl border border-black/5 p-6">
              <h3 className="font-semibold text-ink">{title}</h3>
              <p className="mt-1 text-sm text-ink/60">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="contact" className="bg-surface py-20">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <h2 className="text-2xl font-bold text-ink">Get in touch</h2>
          <p className="mt-2 text-ink/60">Have a question about a webinar or your booking? We're happy to help.</p>
          <div className="mt-6 flex flex-col items-center gap-2 text-sm text-ink/70 md:flex-row md:justify-center md:gap-8">
            <span>📧 support@skillcortex.com</span>
            <span>📞 +91 90000 00000</span>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
