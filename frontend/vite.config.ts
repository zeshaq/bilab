import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Phase 2: dev server proxies /api to the bilab backend (127.0.0.1:8001), so
// the frontend calls same-origin /api/* and no CORS is needed. In production
// (Phase 5) a reverse proxy sits in front of both.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8001',
    },
  },
})
