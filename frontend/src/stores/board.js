import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../lib/api'

export const useBoardStore = defineStore('board', () => {
  const board = ref(null)
  const columns = ref([])
  const cards = ref([])
  const loading = ref(false)
  const error = ref(null)
  const adminToken = ref(null)
  const onlineUsers = ref(0)

  const isAdmin = computed(() => !!adminToken.value)
  const isReadOnly = computed(() => board.value?.is_readonly_default && !isAdmin.value)
  const boardTitle = computed(() => board.value?.title || '')
  const expiresAt = computed(() => board.value?.expires_at ? new Date(board.value.expires_at) : null)

  const columnsSorted = computed(() => {
    return [...columns.value].sort((a, b) => a.position - b.position)
  })

  function cardsByColumn(columnId) {
    return cards.value.filter((c) => c.column_id === columnId)
  }

  async function apiCall(fn) {
    error.value = null
    try {
      return await fn()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Something went wrong'
      throw err
    }
  }

  async function createBoard(payload) {
    loading.value = true
    try {
      const { data } = await apiCall(() => api.post('/api/boards', payload))
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchBoard(boardId, password = null) {
    loading.value = true
    try {
      const headers = {}
      if (password) headers['X-Board-Password'] = password
      if (adminToken.value) headers['X-Admin-Token'] = adminToken.value

      const { data } = await apiCall(() => api.get(`/api/boards/${boardId}`, { headers }))
      board.value = data.board
      columns.value = data.columns
      cards.value = data.cards
      return data
    } finally {
      loading.value = false
    }
  }

  function adminHeaders() {
    return adminToken.value ? { 'X-Admin-Token': adminToken.value } : {}
  }

  async function updateBoard(boardId, payload) {
    const { data } = await apiCall(() =>
      api.patch(`/api/boards/${boardId}`, payload, { headers: adminHeaders() })
    )
    board.value = data
  }

  async function deleteBoard(boardId) {
    await apiCall(() =>
      api.delete(`/api/boards/${boardId}`, { headers: adminHeaders() })
    )
    resetState()
  }

  async function addCard(boardId, columnId, text, authorName, color) {
    const { data } = await apiCall(() =>
      api.post(`/api/boards/${boardId}/cards`, {
        column_id: columnId, text, author_name: authorName, color,
      }, { headers: adminHeaders() })
    )
    onCardAdded(data)
    return data
  }

  async function updateCard(cardId, text) {
    const { data } = await apiCall(() =>
      api.patch(`/api/cards/${cardId}`, { text }, { headers: adminHeaders() })
    )
    onCardUpdated(data)
    return data
  }

  async function deleteCard(cardId) {
    await apiCall(() => api.delete(`/api/cards/${cardId}`, { headers: adminHeaders() }))
    onCardDeleted(cardId)
  }

  async function voteCard(cardId) {
    const { data } = await apiCall(() => api.post(`/api/cards/${cardId}/vote`))
    onCardVoted(data.id, data.votes)
    return data
  }

  function onCardAdded(card) {
    if (!cards.value.find((c) => c.id === card.id)) {
      cards.value.push(card)
    }
  }

  function onCardUpdated(card) {
    const idx = cards.value.findIndex((c) => c.id === card.id)
    if (idx !== -1) cards.value[idx] = { ...cards.value[idx], ...card }
  }

  function onCardDeleted(cardId) {
    cards.value = cards.value.filter((c) => c.id !== cardId)
  }

  function onCardVoted(cardId, votes) {
    const card = cards.value.find((c) => c.id === cardId)
    if (card) card.votes = votes
  }

  async function moveCard(cardId, columnId) {
    const { data } = await apiCall(() =>
      api.patch(`/api/cards/${cardId}/move`, { column_id: columnId }, { headers: adminHeaders() })
    )
    onCardMoved(data.id, data.column_id)
    return data
  }

  function onCardMoved(cardId, columnId) {
    const card = cards.value.find((c) => c.id === cardId)
    if (card) card.column_id = columnId
  }

  function setOnlineUsers(count) {
    onlineUsers.value = count
  }

  function setAdminToken(token) {
    adminToken.value = token
  }

  function resetState() {
    board.value = null
    columns.value = []
    cards.value = []
    loading.value = false
    error.value = null
    adminToken.value = null
    onlineUsers.value = 0
  }

  return {
    board, columns, cards, loading, error, adminToken, onlineUsers,
    isAdmin, isReadOnly, boardTitle, expiresAt, columnsSorted,
    cardsByColumn, createBoard, fetchBoard, updateBoard, deleteBoard,
    addCard, updateCard, deleteCard, voteCard, moveCard,
    onCardAdded, onCardUpdated, onCardDeleted, onCardVoted, onCardMoved,
    setOnlineUsers, setAdminToken, resetState,
  }
})
