<script setup>
import { computed } from 'vue'
import draggable from 'vuedraggable'
import { useBoardStore } from '../../stores/board'
import { useWsStore } from '../../stores/ws'
import { useToast } from '../../composables/useToast'
import BoardCard from './BoardCard.vue'
import AddCardForm from './AddCardForm.vue'

const props = defineProps({
  column: { type: Object, required: true },
  cards: { type: Array, required: true },
  boardId: { type: String, required: true },
  readOnly: { type: Boolean, default: false },
})

const boardStore = useBoardStore()
const wsStore = useWsStore()
const { showToast } = useToast()

const cardCount = computed(() => props.cards.length)

const localCards = computed({
  get: () => [...props.cards],
  set: () => {},
})

async function onChange(evt) {
  // Only act on the "added" side (card dropped INTO this column)
  if (!evt.added) return

  const card = evt.added.element
  const targetColumnId = props.column.id

  // Skip if card is already in this column
  if (card.column_id === targetColumnId) return

  const oldColumnId = card.column_id

  // Update local state immediately so UI reflects the move
  boardStore.onCardMoved(card.id, targetColumnId)

  try {
    const updated = await boardStore.moveCard(card.id, targetColumnId)
    wsStore.send('card:move', { card_id: updated.id, column_id: updated.column_id })
  } catch {
    // Revert on failure
    boardStore.onCardMoved(card.id, oldColumnId)
    showToast('Failed to move card.', 'error')
  }
}

const colorMap = {
  green: 'border-t-emerald-400 bg-emerald-50/50',
  red: 'border-t-rose-400 bg-rose-50/50',
  blue: 'border-t-blue-400 bg-blue-50/50',
  yellow: 'border-t-amber-400 bg-amber-50/50',
  purple: 'border-t-purple-400 bg-purple-50/50',
  orange: 'border-t-orange-400 bg-orange-50/50',
  default: 'border-t-indigo-400 bg-indigo-50/30',
}

const columnStyle = computed(() => {
  return colorMap[props.column.color] || colorMap.default
})
</script>

<template>
  <div :class="['flex-1 min-w-[280px] max-w-[400px] flex flex-col rounded-xl border border-gray-200 border-t-4', columnStyle]">
    <!-- Column Header -->
    <div class="px-4 py-3 flex items-center justify-between">
      <h3 class="font-semibold text-gray-700 text-sm uppercase tracking-wide">
        {{ column.title }}
      </h3>
      <span class="text-xs text-gray-400 bg-white/70 px-2 py-0.5 rounded-full">
        {{ cardCount }}
      </span>
    </div>

    <!-- Cards List -->
    <draggable
      :list="localCards"
      group="cards"
      item-key="id"
      :disabled="readOnly"
      class="flex-1 overflow-y-auto px-3 pb-3 space-y-2 min-h-[40px]"
      ghost-class="drag-ghost"
      drag-class="drag-active"
      :animation="150"
      @change="onChange"
    >
      <template #item="{ element }">
        <BoardCard
          :card="element"
          :read-only="readOnly"
        />
      </template>
    </draggable>

    <!-- Add Card -->
    <AddCardForm
      v-if="!readOnly"
      :board-id="boardId"
      :column-id="column.id"
    />
  </div>
</template>

<style scoped>
.drag-ghost {
  opacity: 0.4;
}

.drag-active {
  opacity: 0.9;
  transform: rotate(2deg);
  cursor: grabbing;
}
</style>
