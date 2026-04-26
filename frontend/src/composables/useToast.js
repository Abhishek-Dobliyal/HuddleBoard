import { ref } from 'vue'
import { TOAST_DURATION_MS } from '../constants/board'

const toasts = ref([])
let toastId = 0

export function useToast() {
  function showToast(message, type = 'info', duration = TOAST_DURATION_MS) {
    const id = ++toastId
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  function removeToast(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return {
    toasts,
    showToast,
    removeToast,
  }
}
