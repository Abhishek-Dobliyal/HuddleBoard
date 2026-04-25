<script setup>
import { computed } from 'vue'
import BoardCard from './BoardCard.vue'
import AddCardForm from './AddCardForm.vue'

const props = defineProps({
  column: { type: Object, required: true },
  cards: { type: Array, required: true },
  boardId: { type: String, required: true },
  readOnly: { type: Boolean, default: false },
})

const cardCount = computed(() => props.cards.length)

// Column colors
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
    <div class="flex-1 overflow-y-auto px-3 pb-3 space-y-2">
      <transition-group
        enter-active-class="animate__animated animate__fadeInUp animate__faster"
        leave-active-class="animate__animated animate__fadeOutDown animate__faster"
      >
        <BoardCard
          v-for="card in cards"
          :key="card.id"
          :card="card"
          :read-only="readOnly"
        />
      </transition-group>
    </div>

    <!-- Add Card -->
    <AddCardForm
      v-if="!readOnly"
      :board-id="boardId"
      :column-id="column.id"
    />
  </div>
</template>
