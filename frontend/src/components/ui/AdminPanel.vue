<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBoardStore } from '../../stores/board'
import { useWsStore } from '../../stores/ws'
import { useToast } from '../../composables/useToast'
import { useClipboard } from '../../composables/useClipboard'
import { getErrorMessage } from '../../lib/errors'

const props = defineProps({
  show: { type: Boolean, default: false },
  boardId: { type: String, required: true },
  shareUrl: { type: String, required: true },
})

const emit = defineEmits(['close'])

const router = useRouter()
const boardStore = useBoardStore()
const wsStore = useWsStore()
const { showToast } = useToast()
const { copy } = useClipboard()

const confirmDelete = ref(false)

function copyShareUrl() {
  copy(props.shareUrl, 'Share link copied!')
}

function copyBoardId() {
  copy(props.boardId, 'Board ID copied!')
}

function copyAdminUrl() {
  copy(`${props.shareUrl}?admin=${boardStore.adminToken}`, 'Admin link copied! Keep this private.')
}

async function toggleReadOnly() {
  try {
    await boardStore.updateBoard(props.boardId, {
      is_readonly_default: !boardStore.board.is_readonly_default,
    })
    wsStore.send('board:update', { is_readonly_default: boardStore.board.is_readonly_default })
    showToast(
      boardStore.board.is_readonly_default ? 'Board is now read-only' : 'Board is now editable',
      'info',
    )
  } catch (err) {
    showToast(getErrorMessage(err, 'Failed to update board settings'), 'error')
  }
}

async function handleDelete() {
  try {
    await boardStore.deleteBoard(props.boardId)
    showToast('Board deleted', 'info')
    router.push('/')
  } catch (err) {
    showToast(getErrorMessage(err, 'Failed to delete board'), 'error')
    confirmDelete.value = false
  }
}
</script>

<template>
  <!-- Overlay -->
  <transition
    enter-active-class="transition-opacity duration-200"
    leave-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    leave-to-class="opacity-0"
  >
    <div v-if="show" class="fixed inset-0 bg-black/20 z-40 cursor-pointer" @click="emit('close')"></div>
  </transition>

  <!-- Panel -->
  <transition
    enter-active-class="animate__animated animate__slideInRight animate__faster"
    leave-active-class="animate__animated animate__slideOutRight animate__faster"
  >
    <div v-if="show" class="fixed right-0 top-0 h-full w-80 bg-white shadow-2xl z-50 flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 class="font-semibold text-gray-800">
          <font-awesome-icon icon="gear" class="mr-2 text-gray-400" />
          Admin Panel
        </h3>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 cursor-pointer transition-colors">
          <font-awesome-icon icon="xmark" size="lg" />
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4 space-y-5">
        <!-- Share Links -->
        <div>
          <h4 class="text-sm font-medium text-gray-700 mb-2">Share Links</h4>
          <div class="space-y-2">
            <button
              @click="copyShareUrl"
              class="w-full text-left px-3 py-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-sm flex items-center gap-2 cursor-pointer active:scale-[0.98]"
            >
              <font-awesome-icon icon="link" class="text-gray-400" />
              <span class="truncate">Copy participant link</span>
              <font-awesome-icon icon="copy" class="text-gray-300 ml-auto" />
            </button>
            <button
              @click="copyAdminUrl"
              class="w-full text-left px-3 py-2 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors text-sm flex items-center gap-2 cursor-pointer active:scale-[0.98]"
            >
              <font-awesome-icon icon="lock" class="text-indigo-400" />
              <span class="truncate">Copy admin link</span>
              <font-awesome-icon icon="copy" class="text-indigo-300 ml-auto" />
            </button>
          </div>
        </div>

        <!-- Settings -->
        <div>
          <h4 class="text-sm font-medium text-gray-700 mb-2">Settings</h4>
          <div class="space-y-3">
            <!-- Read-only toggle -->
            <label class="flex items-center justify-between cursor-pointer p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div>
                <span class="text-sm text-gray-700">Read-only mode</span>
                <p class="text-xs text-gray-400">Participants can only view & vote</p>
              </div>
              <input
                type="checkbox"
                :checked="boardStore.board?.is_readonly_default"
                @change="toggleReadOnly"
                class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 cursor-pointer"
              />
            </label>
          </div>
        </div>

        <!-- Board Info -->
        <div>
          <h4 class="text-sm font-medium text-gray-700 mb-2">Board Info</h4>
          <div class="bg-gray-50 rounded-lg p-3 space-y-1 text-sm">
            <div class="flex justify-between items-center">
              <span class="text-gray-500">Board ID</span>
              <button
                @click="copyBoardId"
                class="text-gray-400 hover:text-indigo-600 transition-colors cursor-pointer flex items-center gap-1 text-xs"
                title="Copy Board ID"
              >
                <span class="text-gray-700 font-mono">{{ boardId.slice(0, 8) }}...</span>
                <font-awesome-icon icon="copy" />
              </button>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Template</span>
              <span class="text-gray-700">{{ boardStore.board?.template }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Password</span>
              <span class="text-gray-700">{{ boardStore.board?.has_password ? 'Yes' : 'No' }}</span>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div>
          <h4 class="text-sm font-medium text-red-600 mb-2">Danger Zone</h4>
          <div v-if="!confirmDelete">
            <button
              @click="confirmDelete = true"
              class="w-full px-4 py-2 border-2 border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium cursor-pointer active:scale-[0.98]"
            >
              <font-awesome-icon icon="trash" class="mr-1" />
              Delete Board
            </button>
          </div>
          <div v-else class="bg-red-50 p-3 rounded-lg animate__animated animate__fadeIn animate__faster">
            <p class="text-sm text-red-700 mb-2">Are you sure? This cannot be undone.</p>
            <div class="flex gap-2">
              <button
                @click="handleDelete"
                class="flex-1 px-3 py-1.5 bg-red-600 text-white rounded text-sm hover:bg-red-700 cursor-pointer active:scale-95"
              >
                Yes, delete
              </button>
              <button
                @click="confirmDelete = false"
                class="flex-1 px-3 py-1.5 bg-white border border-gray-300 text-gray-600 rounded text-sm hover:bg-gray-50 cursor-pointer active:scale-95"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>
