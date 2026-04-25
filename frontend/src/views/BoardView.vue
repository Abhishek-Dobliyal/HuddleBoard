<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBoardStore } from '../stores/board'
import { useWsStore } from '../stores/ws'
import { useCountdown } from '../composables/useCountdown'
import { useToast } from '../composables/useToast'
import BoardColumn from '../components/board/BoardColumn.vue'
import AdminPanel from '../components/ui/AdminPanel.vue'
import PasswordModal from '../components/ui/PasswordModal.vue'

const route = useRoute()
const router = useRouter()
const boardStore = useBoardStore()
const wsStore = useWsStore()
const { showToast } = useToast()

const boardId = route.params.id
const adminToken = route.query.admin || null
const needsPassword = ref(false)
const showAdmin = ref(false)

if (adminToken) {
  boardStore.setAdminToken(adminToken)
}

const { display: countdownDisplay, isExpired } = useCountdown(
  computed(() => boardStore.expiresAt)
)

const shareUrl = computed(() => `${window.location.origin}/board/${boardId}`)

function copyShareUrl() {
  navigator.clipboard.writeText(shareUrl.value)
  showToast('Share link copied!', 'success')
}

async function loadBoard(password = null) {
  try {
    await boardStore.fetchBoard(boardId, password)
    needsPassword.value = false
    wsStore.connect(boardId, adminToken)
  } catch (err) {
    if (err.response?.status === 401) {
      needsPassword.value = true
    } else if (err.response?.status === 404 || err.response?.status === 410) {
      router.push({ name: 'not-found' })
    }
  }
}

onMounted(() => loadBoard())

onUnmounted(() => {
  wsStore.disconnect()
  boardStore.resetState()
})
</script>

<template>
  <PasswordModal v-if="needsPassword" @submit="loadBoard" />

  <div v-else-if="boardStore.loading" class="min-h-screen flex items-center justify-center">
    <div class="text-center animate__animated animate__fadeIn">
      <div class="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto"></div>
      <p class="mt-4 text-gray-500">Loading board...</p>
    </div>
  </div>

  <div v-else-if="isExpired" class="min-h-screen flex items-center justify-center">
    <div class="text-center p-8 animate__animated animate__fadeIn">
      <div class="text-6xl mb-4 animate__animated animate__pulse animate__infinite animate__slower">
        <font-awesome-icon icon="clock" class="text-amber-500" />
      </div>
      <h2 class="text-2xl font-bold text-gray-800">Board Expired</h2>
      <p class="text-gray-500 mt-2">This board has reached its time limit.</p>
      <router-link to="/" class="mt-6 inline-block px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors cursor-pointer">
        Create a New Board
      </router-link>
    </div>
  </div>

  <div v-else-if="boardStore.board" class="min-h-screen flex flex-col">
    <header class="bg-white border-b border-gray-200 px-4 py-3 sticky top-0 z-30 animate__animated animate__fadeInDown animate__faster">
      <div class="flex items-center justify-between max-w-screen-2xl mx-auto">
        <div class="flex items-center gap-3 min-w-0">
          <router-link to="/" class="text-xl font-bold text-gray-900 shrink-0 cursor-pointer hover:opacity-75 transition-opacity">
            H<span class="text-indigo-600">B</span>
          </router-link>
          <div class="h-6 w-px bg-gray-200"></div>
          <h1 class="text-lg font-semibold text-gray-800 truncate min-w-0">{{ boardStore.boardTitle }}</h1>
        </div>

        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-400 flex items-center gap-1" v-if="boardStore.onlineUsers > 0">
            <font-awesome-icon icon="users" />
            {{ boardStore.onlineUsers }}
          </span>

          <span v-if="countdownDisplay" class="text-sm text-amber-600 flex items-center gap-1">
            <font-awesome-icon icon="clock" />
            {{ countdownDisplay }}
          </span>

          <span
            :class="['w-2 h-2 rounded-full transition-colors', wsStore.connected ? 'bg-green-400' : 'bg-red-400 animate__animated animate__flash animate__infinite animate__slower']"
            :title="wsStore.connected ? 'Connected' : 'Disconnected'"
          ></span>

          <button
            @click="copyShareUrl"
            class="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer active:scale-95"
          >
            <font-awesome-icon icon="link" />
            Share
          </button>

          <button
            v-if="boardStore.isAdmin"
            @click="showAdmin = !showAdmin"
            class="px-3 py-1.5 text-sm bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer active:scale-95"
          >
            <font-awesome-icon icon="gear" />
            Admin
          </button>

          <span v-if="boardStore.isReadOnly" class="px-2 py-1 text-xs bg-amber-100 text-amber-700 rounded-full">
            <font-awesome-icon icon="eye" class="mr-1" />Read-only
          </span>
        </div>
      </div>

      <p v-if="boardStore.board.description" class="text-sm text-gray-400 max-w-screen-2xl mx-auto mt-1 truncate">
        {{ boardStore.board.description }}
      </p>
    </header>

    <main class="flex-1 overflow-x-auto p-4">
      <div class="flex gap-4 min-h-[calc(100vh-120px)] max-w-screen-2xl mx-auto">
        <BoardColumn
          v-for="(column, idx) in boardStore.columnsSorted"
          :key="column.id"
          :column="column"
          :cards="boardStore.cardsByColumn(column.id)"
          :board-id="boardId"
          :read-only="boardStore.isReadOnly"
          class="animate__animated animate__fadeInUp"
          :style="{ animationDelay: `${idx * 100}ms` }"
        />
      </div>
    </main>

    <AdminPanel
      v-if="boardStore.isAdmin"
      :show="showAdmin"
      :board-id="boardId"
      :share-url="shareUrl"
      @close="showAdmin = false"
    />
  </div>
</template>
