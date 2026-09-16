import Logo from "./Logo"

export default function Footer() {
  return (
    <footer className="border-t border-black/5 bg-ink text-white/70">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10 md:flex-row md:items-center md:justify-between">
        <Logo dark />
        <p className="text-sm">© 2026 Skill Cortex. All rights reserved.</p>
      </div>
    </footer>
  )
}
