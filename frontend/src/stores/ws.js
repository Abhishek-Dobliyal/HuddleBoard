import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useBoardStore } from './board'
import { useToast } from '../composables/useToast'
import { buildWsUrl } from '../lib/api'
import {
  WS_RECONNECT_BASE_MS, WS_RECONNECT_MAX_MS, WS_RECONNECT_MAX_RETRIES,
  WS_CLOSE_MIN, WS_CLOSE_MAX,
} from '../constants/board'

export const useWsStore = defineStore('ws', () => {
  const socket = ref(null)
  const connected = ref(false)
  const reconnectTimer = ref(null)
  let connectOpts = {}
  let retryCount = 0

  function connect(boardId, opts = {}) {
    connectOpts = { boardId, ...opts }
    disconnect()

    const ws = new WebSocket(buildWsUrl(boardId))
    socket.value = ws

    ws.onopen = () => {
      connected.value = true
      const wasReconnect = retryCount > 0
      retryCount = 0
      clearReconnectTimer()

      // Send auth credentials as first message (not in URL)
      if (connectOpts.adminToken || connectOpts.password) {
        ws.send(JSON.stringify({
          type: 'auth',
          data: {
            adminToken: connectOpts.adminToken || null,
            password: connectOpts.password || null,
          },
        }))
      }

      if (wasReconnect) {
        const boardStore = useBoardStore()
        const password = connectOpts.password || null
        boardStore.fetchBoard(connectOpts.boardId, password).catch(() => {})
      }
    }

    ws.onmessage = (event) => {
      try {
        handleMessage(JSON.parse(event.data))
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
      }
    }

    ws.onclose = (event) => {
      connected.value = false
      if (event.code >= WS_CLOSE_MIN && event.code < WS_CLOSE_MAX) {
        return
      }
      scheduleReconnect()
    }

    ws.onerror = () => {
      ws.close()
    }
  }

  function handleMessage(msg) {
    const boardStore = useBoardStore()
    const { showToast } = useToast()

    switch (msg.type) {
      case 'ping':
        send('pong', {})
        return
      case 'board:state':
        boardStore.board = msg.data.board
        boardStore.columns = msg.data.columns
        boardStore.cards = msg.data.cards
        break
      case 'board:updated':
        if (boardStore.board) Object.assign(boardStore.board, msg.data)
        if (msg.data.is_readonly_default !== undefined) {
          showToast(
            msg.data.is_readonly_default ? 'Board is now read-only' : 'Board is now editable',
            'info',
          )
        }
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
      case 'card:moved':
        boardStore.onCardMoved(msg.data.card_id, msg.data.column_id)
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
    retryCount = 0
    if (socket.value) {
      socket.value.onclose = null
      socket.value.close()
      socket.value = null
    }
    connected.value = false
  }

  function scheduleReconnect() {
    clearReconnectTimer()
    const { showToast } = useToast()

    if (retryCount >= WS_RECONNECT_MAX_RETRIES) {
      showToast('Could not reconnect. Please refresh the page.', 'error')
      return
    }

    const delay = Math.min(WS_RECONNECT_BASE_MS * 2 ** retryCount, WS_RECONNECT_MAX_MS)
    retryCount++

    showToast(`Connection lost. Retrying in ${Math.round(delay / 1000)}s...`, 'warning')
    reconnectTimer.value = setTimeout(
      () => connect(connectOpts.boardId, connectOpts),
      delay,
    )
  }

  function clearReconnectTimer() {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
  }

  return { connected, connect, disconnect, send }
})
