<script setup>
import { ref, nextTick } from 'vue'
import { useBoardStore } from '../../stores/board'
import { useWsStore } from '../../stores/ws'
import { useToast } from '../../composables/useToast'

const props = defineProps({
  card: { type: Object, required: true },
  readOnly: { type: Boolean, default: false },
})

const boardStore = useBoardStore()
const wsStore = useWsStore()
const { showToast } = useToast()

const isEditing = ref(false)
const editText = ref('')
const editInput = ref(null)
const isVoting = ref(false)
const isDeleting = ref(false)
const showConfirmDelete = ref(false)

const stickyColors = {
  yellow: 'bg-yellow-100 border-yellow-200',
  pink: 'bg-pink-100 border-pink-200',
  blue: 'bg-blue-100 border-blue-200',
  green: 'bg-green-100 border-green-200',
  purple: 'bg-purple-100 border-purple-200',
  default: 'bg-yellow-100 border-yellow-200',
}

const cardColor = stickyColors[props.card.color] || stickyColors.default

function startEdit() {
  if (props.readOnly) return
  editText.value = props.card.text
  isEditing.value = true
  nextTick(() => editInput.value?.focus())
}

async function saveEdit() {
  const trimmed = editText.value.trim()
  if (!trimmed || trimmed === props.card.text) {
    isEditing.value = false
    return
  }
  try {
    const updated = await boardStore.updateCard(props.card.id, trimmed)
    wsStore.send('card:update', { card_id: updated.id, text: updated.text })
    isEditing.value = false
  } catch {
    showToast('Failed to update card. Please try again.', 'error')
  }
}

function cancelEdit() {
  isEditing.value = false
}

async function handleVote() {
  if (isVoting.value) return
  isVoting.value = true
  try {
    const updated = await boardStore.voteCard(props.card.id)
    wsStore.send('card:vote', { card_id: updated.id, votes: updated.votes })
  } catch {
    showToast('Failed to register vote.', 'error')
  } finally {
    isVoting.value = false
  }
}

async function handleDelete() {
  if (isDeleting.value) return
  isDeleting.value = true
  try {
    await boardStore.deleteCard(props.card.id)
    wsStore.send('card:delete', { card_id: props.card.id })
    showConfirmDelete.value = false
  } catch {
    showToast('Failed to delete card.', 'error')
    showConfirmDelete.value = false
  } finally {
    isDeleting.value = false
  }
}
</script>

<template>
  <div :class="['p-3 rounded-lg border card-shadow hover:card-shadow-hover transition-all duration-200 relative group hover:-translate-y-0.5', cardColor]">
    <div v-if="isEditing" class="animate__animated animate__fadeIn animate__faster">
      <textarea
        ref="editInput"
        v-model="editText"
        rows="3"
        maxlength="500"
        class="w-full px-2 py-1 border border-gray-200 rounded text-sm resize-none focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 bg-white"
        @keydown.enter.ctrl="saveEdit"
        @keydown.escape="cancelEdit"
      ></textarea>
      <div class="flex justify-end gap-2 mt-1">
        <button @click="cancelEdit" class="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 cursor-pointer">Cancel</button>
        <button @click="saveEdit" class="text-xs bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700 cursor-pointer active:scale-95">Save</button>
      </div>
    </div>

    <div v-else>
      <p
        class="text-sm text-gray-700 whitespace-pre-wrap break-words"
        :class="{ 'cursor-pointer': !readOnly }"
        @dblclick="startEdit"
      >{{ card.text }}</p>

      <p v-if="card.author_name" class="text-xs text-gray-400 mt-2">
        &mdash; {{ card.author_name }}
      </p>

      <div class="flex items-center justify-between mt-2 pt-2 border-t border-black/5">
        <button
          @click="handleVote"
          :disabled="isVoting"
          class="flex items-center gap-1 text-xs text-gray-500 hover:text-indigo-600 transition-colors cursor-pointer active:scale-110"
        >
          <font-awesome-icon icon="thumbs-up" />
          <span :class="[card.votes > 0 ? 'font-semibold text-indigo-600' : '']">{{ card.votes }}</span>
        </button>

        <div v-if="!readOnly" class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button @click="startEdit" class="text-xs text-gray-400 hover:text-indigo-600 transition-colors cursor-pointer" title="Edit">
            <font-awesome-icon icon="pen" />
          </button>
          <button
            v-if="!showConfirmDelete"
            @click="showConfirmDelete = true"
            class="text-xs text-gray-400 hover:text-red-500 transition-colors cursor-pointer"
            title="Delete"
          >
            <font-awesome-icon icon="trash" />
          </button>
          <div v-else class="flex items-center gap-1 animate__animated animate__fadeIn animate__faster">
            <button @click="handleDelete" class="text-xs text-red-600 hover:text-red-700 font-medium cursor-pointer">Delete?</button>
            <button @click="showConfirmDelete = false" class="text-xs text-gray-400 hover:text-gray-600 cursor-pointer">No</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
