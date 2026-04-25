<script setup>
import { useToast } from '../../composables/useToast'

const { toasts, removeToast } = useToast()

const typeClasses = {
  info: 'bg-gray-800 text-white',
  success: 'bg-emerald-600 text-white',
  error: 'bg-red-600 text-white',
  warning: 'bg-amber-500 text-white',
}
</script>

<template>
  <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
    <transition-group
      enter-active-class="animate__animated animate__fadeInRight animate__faster"
      leave-active-class="animate__animated animate__fadeOutRight animate__faster"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'px-4 py-2.5 rounded-lg shadow-lg text-sm font-medium max-w-xs flex items-center gap-2 cursor-pointer',
          typeClasses[toast.type] || typeClasses.info,
        ]"
        @click="removeToast(toast.id)"
      >
        <font-awesome-icon v-if="toast.type === 'success'" icon="check" />
        {{ toast.message }}
      </div>
    </transition-group>
  </div>
</template>
