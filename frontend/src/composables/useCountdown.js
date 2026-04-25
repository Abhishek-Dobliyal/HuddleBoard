import { ref, onMounted, onUnmounted, computed } from 'vue'

export function useCountdown(targetDate) {
  const now = ref(Date.now())
  let interval = null

  const remaining = computed(() => {
    if (!targetDate.value) return null
    const diff = new Date(targetDate.value).getTime() - now.value
    return diff > 0 ? diff : 0
  })

  const hours = computed(() => remaining.value !== null ? Math.floor(remaining.value / (1000 * 60 * 60)) : 0)
  const minutes = computed(() => remaining.value !== null ? Math.floor((remaining.value % (1000 * 60 * 60)) / (1000 * 60)) : 0)
  const seconds = computed(() => remaining.value !== null ? Math.floor((remaining.value % (1000 * 60)) / 1000) : 0)
  const isExpired = computed(() => remaining.value === 0)

  const display = computed(() => {
    if (remaining.value === null) return ''
    if (isExpired.value) return 'Expired'
    const parts = []
    if (hours.value > 0) parts.push(`${hours.value}h`)
    if (minutes.value > 0) parts.push(`${minutes.value}m`)
    if (hours.value === 0) parts.push(`${seconds.value}s`)
    return parts.join(' ')
  })

  onMounted(() => {
    interval = setInterval(() => {
      now.value = Date.now()
    }, 1000)
  })

  onUnmounted(() => {
    if (interval) clearInterval(interval)
  })

  return { hours, minutes, seconds, isExpired, display }
}
