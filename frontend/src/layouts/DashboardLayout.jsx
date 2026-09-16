import { Link, useLocation, useNavigate } from "react-router-dom"
import Logo from "../components/Logo"
import { useAuth } from "../context/AuthContext"

export default function DashboardLayout({ title, navItems, children }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  function handleLogout() {
    logout()
    navigate("/")
  }

  return (
    <div className="flex min-h-screen bg-surface">
      <aside className="hidden w-64 flex-col border-r border-black/5 bg-white md:flex">
        <div className="border-b border-black/5 px-6 py-5">
          <Link to="/">
            <Logo />
          </Link>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const active = location.hash === item.href || (item.href === "#" && !location.hash)
            return (
              <a
                key={item.label}
                href={item.href}
                className={`block rounded-lg px-3 py-2 text-sm font-medium transition ${
                  active ? "bg-primary/10 text-primary" : "text-ink/70 hover:bg-black/5"
                }`}
              >
                {item.label}
              </a>
            )
          })}
        </nav>
        <div className="space-y-2 border-t border-black/5 px-6 py-4">
          <Link to="/" className="block text-sm font-medium text-ink/50 hover:text-primary">
            ← Back to site
          </Link>
          <button onClick={handleLogout} className="block text-sm font-medium text-ink/50 hover:text-primary">
            Log out
          </button>
        </div>
      </aside>

      <div className="flex-1">
        <header className="flex items-center justify-between border-b border-black/5 bg-white px-6 py-4">
          <h1 className="text-lg font-bold text-ink">{title}</h1>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-ink/60 sm:inline">{user?.name}</span>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
              {user?.name?.[0]?.toUpperCase() ?? "SC"}
            </div>
          </div>
        </header>
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
