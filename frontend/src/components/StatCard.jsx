export default function StatCard({ label, value }) {
  return (
    <div className="rounded-xl border border-black/5 bg-white p-5 shadow-sm">
      <p className="text-sm text-ink/50">{label}</p>
      <p className="mt-1 text-2xl font-bold text-ink">{value}</p>
    </div>
  )
}
