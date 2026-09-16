const API_URL = import.meta.env.VITE_API_URL ?? ""

async function request(path, { method = "GET", body, token } = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    throw new Error(data?.detail ?? "Request failed")
  }
  return data
}

export const api = {
  listDepartments: () => request("/departments"),
  listAllDepartments: (token) => request("/departments/admin/all", { token }),
  createDepartment: (payload, token) => request("/departments", { method: "POST", body: payload, token }),
  updateDepartment: (id, payload, token) => request(`/departments/${id}`, { method: "PATCH", body: payload, token }),
  register: (payload) => request("/auth/register", { method: "POST", body: payload }),
  login: (payload) => request("/auth/login", { method: "POST", body: payload }),
  forgotPassword: (email) => request("/auth/forgot-password", { method: "POST", body: { email } }),
  resetPassword: (payload) => request("/auth/reset-password", { method: "POST", body: payload }),
  me: (token) => request("/auth/me", { token }),
  listWebinars: (departmentId) =>
    request(`/webinars${departmentId ? `?department_id=${departmentId}` : ""}`),
  listAllWebinars: (token) => request("/webinars/admin/all", { token }),
  getWebinar: (id) => request(`/webinars/${id}`),
  createWebinar: (payload, token) => request("/webinars", { method: "POST", body: payload, token }),
  updateWebinar: (id, payload, token) => request(`/webinars/${id}`, { method: "PATCH", body: payload, token }),
  createSlot: (webinarId, payload, token) =>
    request(`/webinars/${webinarId}/slots`, { method: "POST", body: payload, token }),
  updateSlot: (slotId, payload, token) => request(`/slots/${slotId}`, { method: "PATCH", body: payload, token }),
  createBooking: (payload, token) => request("/bookings", { method: "POST", body: payload, token }),
  myBookings: (token) => request("/bookings/me", { token }),
  listAllBookings: (token) => request("/bookings", { token }),
  createOrder: (bookingId, token) =>
    request("/payments/create-order", { method: "POST", body: { booking_id: bookingId }, token }),
  verifyPayment: (payload, token) => request("/payments/verify", { method: "POST", body: payload, token }),
  listPayments: (token) => request("/payments", { token }),
  myNotifications: (token) => request("/notifications/me", { token }),
  listNotifications: (token) => request("/notifications", { token }),
  runReminders: (token) => request("/reminders/run", { method: "POST", token }),
  listUsers: (token) => request("/users", { token }),
  chatWithAssistant: (message, history, token) =>
    request("/assistant/chat", { method: "POST", body: { message, history }, token }),
}
