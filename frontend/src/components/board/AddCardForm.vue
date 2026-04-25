<script setup>
import { ref } from 'vue'
import { useBoardStore } from '../../stores/board'
import { useWsStore } from '../../stores/ws'
import { useToast } from '../../composables/useToast'

const props = defineProps({
  boardId: { type: String, required: true },
  columnId: { type: String, required: true },
})

const boardStore = useBoardStore()
const wsStore = useWsStore()
const { showToast } = useToast()

const text = ref('')
const authorName = ref(localStorage.getItem('hb_author') || '')
const isExpanded = ref(false)
const isSubmitting = ref(false)

const stickyColors = ['yellow', 'pink', 'blue', 'green', 'purple']
const selectedColor = ref(stickyColors[Math.floor(Math.random() * stickyColors.length)])

function expand() {
  isExpanded.value = true
}

function collapse() {
  if (!text.value.trim()) {
    isExpanded.value = false
  }
}

async function handleSubmit() {
  const trimmed = text.value.trim()
  if (!trimmed || isSubmitting.value) return

  isSubmitting.value = true
  const author = authorName.value.trim() || 'Anonymous'

  if (authorName.value.trim()) {
    localStorage.setItem('hb_author', authorName.value.trim())
  }

  try {
    const card = await boardStore.addCard(
      props.boardId, props.columnId, trimmed, author, selectedColor.value,
    )

    // Notify other clients via WS (local state already updated by store)
    wsStore.send('card:add', card)

    text.value = ''
    selectedColor.value = stickyColors[Math.floor(Math.random() * stickyColors.length)]
  } catch {
    showToast('Failed to add card. Please try again.', 'error')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="px-3 pb-3">
    <button
      v-if="!isExpanded"
      @click="expand"
      class="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-400 hover:text-indigo-600 hover:border-indigo-300 transition-all text-sm flex items-center justify-center gap-1 cursor-pointer hover:scale-[1.01] active:scale-[0.99]"
    >
      <font-awesome-icon icon="plus" />
      Add a card
    </button>

    <transition
      enter-active-class="animate__animated animate__fadeInUp animate__faster"
      leave-active-class="animate__animated animate__fadeOut animate__faster"
    >
      <div v-if="isExpanded" class="bg-white rounded-lg border border-gray-200 p-3 card-shadow">
        <textarea
          v-model="text"
          rows="3"
          maxlength="500"
          placeholder="Type your idea..."
          class="w-full px-2 py-1.5 border border-gray-200 rounded text-sm resize-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          @keydown.enter.ctrl="handleSubmit"
          @blur="collapse"
        ></textarea>

        <input
          v-model="authorName"
          type="text"
          placeholder="Your name (optional)"
          maxlength="30"
          class="w-full mt-2 px-2 py-1.5 border border-gray-200 rounded text-xs text-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        />

        <div class="flex items-center gap-2 mt-2">
          <span class="text-xs text-gray-400">Color:</span>
          <button
            v-for="color in stickyColors"
            :key="color"
            type="button"
            @click="selectedColor = color"
            :class="[
              'w-5 h-5 rounded-full border-2 transition-all cursor-pointer hover:scale-125',
              {
                yellow: 'bg-yellow-200',
                pink: 'bg-pink-200',
                blue: 'bg-blue-200',
                green: 'bg-green-200',
                purple: 'bg-purple-200',
              }[color],
              selectedColor === color ? 'border-indigo-600 scale-110' : 'border-transparent',
            ]"
          ></button>
        </div>

        <div class="flex justify-between items-center mt-3">
          <button @click="isExpanded = false" class="text-xs text-gray-400 hover:text-gray-600 cursor-pointer">Cancel</button>
          <button
            @click="handleSubmit"
            :disabled="!text.trim() || isSubmitting"
            :class="[
              'text-xs px-4 py-1.5 rounded font-medium transition-all',
              text.trim() && !isSubmitting
                ? 'bg-indigo-600 text-white hover:bg-indigo-700 cursor-pointer active:scale-95'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed',
            ]"
          >
            {{ isSubmitting ? 'Adding...' : 'Add' }}
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>
