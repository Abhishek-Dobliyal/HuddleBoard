import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useBoardStore } from './board'
import { useToast } from '../composables/useToast'

export const useWsStore = defineStore('ws', () => {
  const socket = ref(null)
  const connected = ref(false)
  const reconnectTimer = ref(null)

  function connect(id, adminToken = null) {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    let url = `${protocol}://${window.location.host}/ws/${id}`
    if (adminToken) url += `?admin=${adminToken}`

    disconnect()

    const ws = new WebSocket(url)
    socket.value = ws

    ws.onopen = () => {
      connected.value = true
      clearReconnectTimer()
    }

    ws.onmessage = (event) => {
      try {
        handleMessage(JSON.parse(event.data))
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
      }
    }

    ws.onclose = () => {
      connected.value = false
      const { showToast } = useToast()
      showToast('Connection lost. Reconnecting...', 'warning')
      scheduleReconnect(id, adminToken)
    }

    ws.onerror = () => {
      ws.close()
    }
  }

  function handleMessage(msg) {
    const boardStore = useBoardStore()
    const { showToast } = useToast()

    switch (msg.type) {
      case 'board:state':
        boardStore.board = msg.data.board
        boardStore.columns = msg.data.columns
        boardStore.cards = msg.data.cards
        break
      case 'card:added':
        boardStore.onCardAdded(msg.data)
        showToast(`${msg.data.author_name || 'Someone'} added a card`, 'info')
        break
      case 'card:updated':
        boardStore.onCardUpdated(msg.data)
        break
      case 'card:deleted':
        boardStore.onCardDeleted(msg.data.card_id)
        break
      case 'card:voted':
        boardStore.onCardVoted(msg.data.card_id, msg.data.votes)
        break
      case 'user:joined':
      case 'user:left':
        boardStore.setOnlineUsers(msg.data.count)
        break
    }
  }

  function send(type, data) {
    if (socket.value?.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify({ type, data }))
    }
  }

  function disconnect() {
    clearReconnectTimer()
    if (socket.value) {
      socket.value.onclose = null
      socket.value.close()
      socket.value = null
    }
    connected.value = false
  }

  function scheduleReconnect(id, adminToken) {
    clearReconnectTimer()
    reconnectTimer.value = setTimeout(() => connect(id, adminToken), 3000)
  }

  function clearReconnectTimer() {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
  }

  return { socket, connected, connect, disconnect, send }
})
