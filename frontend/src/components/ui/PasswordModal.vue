<script setup>
import { ref } from 'vue'

const props = defineProps({
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit'])

const password = ref('')
const localError = ref('')
const errorKey = ref(0)

function setError(msg) {
  localError.value = msg
  errorKey.value++
}

function handleSubmit() {
  if (!password.value.trim()) {
    setError('Password is required')
    return
  }
  localError.value = ''
  emit('submit', password.value)
}

defineExpose({ setError })
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
    <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 w-full max-w-sm mx-4">
      <div class="text-center mb-6">
        <div class="w-14 h-14 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <font-awesome-icon icon="lock" class="text-indigo-600 text-xl" />
        </div>
        <h2 class="text-xl font-semibold text-gray-800">Protected Board</h2>
        <p class="text-sm text-gray-500 mt-1">Enter the password to access this board</p>
      </div>

      <form @submit.prevent="handleSubmit">
        <input
          v-model="password"
          type="password"
          placeholder="Board password"
          autofocus
          class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 transition-colors mb-3"
        />

        <transition
          enter-active-class="animate__animated animate__shakeX animate__faster"
          leave-active-class="animate__animated animate__fadeOut animate__faster"
        >
          <p v-if="localError" :key="errorKey" class="text-sm text-red-500 mb-3">{{ localError }}</p>
        </transition>

        <button
          type="submit"
          class="w-full py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium cursor-pointer active:scale-[0.98]"
        >
          Enter Board
        </button>
      </form>

      <router-link to="/" class="block text-center text-sm text-gray-400 hover:text-gray-600 mt-4 cursor-pointer transition-colors">
        &larr; Back to home
      </router-link>
    </div>
  </div>
</template>
