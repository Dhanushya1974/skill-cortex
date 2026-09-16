export default function Logo({ dark = false }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-bold text-white">
        SC
      </div>
      <span className={`text-lg font-bold ${dark ? "text-white" : "text-ink"}`}>
        <span className="text-primary">Skill</span>Cortex
      </span>
    </div>
  )
}
