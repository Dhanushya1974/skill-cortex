const styles = {
  CONFIRMED: "bg-green-100 text-green-700",
  PAID: "bg-green-100 text-green-700",
  SENT: "bg-green-100 text-green-700",
  PENDING: "bg-amber-100 text-amber-700",
  FAILED: "bg-red-100 text-red-700",
  REFUNDED: "bg-slate-100 text-slate-700",
}

export default function StatusBadge({ status }) {
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${styles[status] ?? "bg-slate-100 text-slate-700"}`}>
      {status}
    </span>
  )
}
