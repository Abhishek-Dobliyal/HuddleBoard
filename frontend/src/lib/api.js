import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

export const api = axios.create({
  baseURL: API_URL,
})

/** Build WS URL — credentials are sent via first message, not the URL. */
export function buildWsUrl(boardId) {
  let base
  if (API_URL) {
    base = API_URL.replace(/^http/, 'ws')
  } else {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    base = `${protocol}://${window.location.host}`
  }

  return `${base}/ws/${boardId}`
}
