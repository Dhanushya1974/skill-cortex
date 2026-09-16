import { useState } from "react"
import { Link } from "react-router-dom"
import Logo from "./Logo"

const links = [
  { href: "#webinars", label: "Webinars" },
  { href: "#departments", label: "Departments" },
  { href: "#about", label: "About" },
  { href: "#contact", label: "Contact" },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-10 border-b border-black/5 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" onClick={() => setOpen(false)}>
          <Logo />
        </Link>
        <nav className="hidden items-center gap-8 text-sm font-medium text-ink/70 md:flex">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="hover:text-primary">
              {l.label}
            </a>
          ))}
        </nav>
        <div className="hidden items-center gap-3 md:flex">
          <Link to="/login" className="rounded-lg px-4 py-2 text-sm font-semibold text-ink/80 hover:text-primary">
            Log In
          </Link>
          <Link
            to="/register"
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-dark"
          >
            Get Started
          </Link>
        </div>

        <button
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-ink md:hidden"
        >
          {open ? (
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          )}
        </button>
      </div>

      {open && (
        <div className="border-t border-black/5 px-6 py-4 md:hidden">
          <nav className="flex flex-col gap-3 text-sm font-medium text-ink/70">
            {links.map((l) => (
              <a key={l.href} href={l.href} onClick={() => setOpen(false)} className="hover:text-primary">
                {l.label}
              </a>
            ))}
          </nav>
          <div className="mt-4 flex flex-col gap-2">
            <Link
              to="/login"
              onClick={() => setOpen(false)}
              className="rounded-lg px-4 py-2 text-center text-sm font-semibold text-ink/80 hover:text-primary"
            >
              Log In
            </Link>
            <Link
              to="/register"
              onClick={() => setOpen(false)}
              className="rounded-lg bg-primary px-4 py-2 text-center text-sm font-semibold text-white hover:bg-primary-dark"
            >
              Get Started
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}
