import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

export const api = axios.create({
  baseURL: API_URL,
})

/**
 * Build the WebSocket URL for a given board.
 * Local dev (VITE_API_URL empty): uses current host via Vite proxy.
 * Production (VITE_API_URL set): derives WS URL from the API URL.
 */
export function buildWsUrl(boardId, { adminToken = null, password = null } = {}) {
  let base
  if (API_URL) {
    base = API_URL.replace(/^http/, 'ws')
  } else {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    base = `${protocol}://${window.location.host}`
  }

  const params = new URLSearchParams()
  if (adminToken) params.set('admin', adminToken)
  if (password) params.set('password', password)

  const qs = params.toString()
  return `${base}/ws/${boardId}${qs ? '?' + qs : ''}`
}
