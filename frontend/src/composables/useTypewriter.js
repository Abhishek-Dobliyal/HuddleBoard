import { ref, onMounted, onUnmounted } from 'vue'

export function useTypewriter(phrases, { typeSpeed = 60, deleteSpeed = 35, pauseAfterType = 2000, pauseAfterDelete = 500 } = {}) {
  const displayText = ref('')
  const currentPhraseIndex = ref(0)
  const isDeleting = ref(false)
  let timeout = null

  function tick() {
    const currentPhrase = phrases[currentPhraseIndex.value]

    if (!isDeleting.value) {
      // Typing
      displayText.value = currentPhrase.substring(0, displayText.value.length + 1)

      if (displayText.value === currentPhrase) {
        // Finished typing — pause then start deleting
        timeout = setTimeout(() => {
          isDeleting.value = true
          tick()
        }, pauseAfterType)
        return
      }

      timeout = setTimeout(tick, typeSpeed)
    } else {
      // Deleting
      displayText.value = currentPhrase.substring(0, displayText.value.length - 1)

      if (displayText.value === '') {
        isDeleting.value = false
        currentPhraseIndex.value = (currentPhraseIndex.value + 1) % phrases.length

        timeout = setTimeout(tick, pauseAfterDelete)
        return
      }

      timeout = setTimeout(tick, deleteSpeed)
    }
  }

  onMounted(() => {
    tick()
  })

  onUnmounted(() => {
    if (timeout) clearTimeout(timeout)
  })

  return { displayText, currentPhraseIndex, isDeleting }
}
