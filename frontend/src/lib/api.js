import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

export const api = axios.create({
  baseURL: API_URL,
})

/**
 * Build the WebSocket URL for a given board.
 * - Local dev (VITE_API_URL empty): uses current host via Vite proxy
 * - Production (VITE_API_URL set): derives WS URL from the API URL
 */
export function buildWsUrl(boardId, adminToken = null) {
  let url

  if (API_URL) {
    // Production: convert https://api.example.com → wss://api.example.com/ws/{id}
    const wsBase = API_URL.replace(/^http/, 'ws')
    url = `${wsBase}/ws/${boardId}`
  } else {
    // Local dev: use current host (Vite proxy handles it)
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    url = `${protocol}://${window.location.host}/ws/${boardId}`
  }

  if (adminToken) url += `?admin=${adminToken}`
  return url
}
