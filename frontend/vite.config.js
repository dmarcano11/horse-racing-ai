import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    proxy: {
      // Proxy API calls to Spring Boot - no CORS issues!
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      }
    }
  }
})