import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const backendTarget = 'http://localhost:8000'
const backendPaths = [
  '/health',
  '/auth',
  '/departments',
  '/webinars',
  '/slots',
  '/bookings',
  '/payments',
  '/notifications',
  '/reminders',
  '/users',
  '/assistant',
]

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: Object.fromEntries(backendPaths.map((path) => [path, { target: backendTarget, changeOrigin: true }])),
  },
})
