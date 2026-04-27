<script setup>
import { ref } from 'vue'
import { useClipboard } from '../../composables/useClipboard'

const props = defineProps({
  mode: { type: String, required: true }, // 'display' or 'login'
  token: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit'])
const { copy } = useClipboard()

const inputToken = ref('')
const localError = ref('')

function handleCopy() {
  copy(props.token, 'Admin token copied!')
}

function handleSubmit() {
  if (props.loading) return
  if (!inputToken.value.trim()) {
    localError.value = 'Token is required'
    return
  }
  localError.value = ''
  emit('submit', inputToken.value.trim())
}

function setError(msg) {
  localError.value = msg
}

defineExpose({ setError })
</script>

<template>
  <div class="fixed inset-0 bg-black/30 z-50 flex items-center justify-center px-4" @click.self="emit('close')">
    <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 w-full max-w-sm">

      <!-- Display mode: show token after board creation -->
      <template v-if="mode === 'display'">
        <div class="text-center mb-4">
          <div class="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <font-awesome-icon icon="key" class="text-emerald-600 text-xl" />
          </div>
          <h2 class="text-lg font-semibold text-gray-800">Save Your Admin Token</h2>
          <p class="text-sm text-gray-500 mt-1">You'll need this to manage your board later.</p>
        </div>

        <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-2 mb-3">
          <code class="flex-1 text-sm text-gray-700 font-mono break-all select-all">{{ token }}</code>
          <button
            @click="handleCopy"
            class="shrink-0 px-3 py-1.5 bg-indigo-600 text-white text-xs rounded-lg hover:bg-indigo-700 cursor-pointer active:scale-95"
          >
            <font-awesome-icon icon="copy" class="mr-1" />
            Copy
          </button>
        </div>

        <p class="text-xs text-amber-600 mb-4">
          <font-awesome-icon icon="triangle-exclamation" class="mr-1" />
          This token won't be shown again. Save it somewhere safe.
        </p>

        <button
          @click="emit('close')"
          class="w-full py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium cursor-pointer active:scale-[0.98]"
        >
          I've saved it — continue
        </button>
      </template>

      <!-- Login mode: enter token to gain admin access -->
      <template v-else>
        <div class="text-center mb-4">
          <div class="w-14 h-14 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <font-awesome-icon icon="key" class="text-indigo-600 text-xl" />
          </div>
          <h2 class="text-lg font-semibold text-gray-800">Admin Login</h2>
          <p class="text-sm text-gray-500 mt-1">Enter your admin token to manage this board.</p>
        </div>

        <form @submit.prevent="handleSubmit">
          <input
            v-model="inputToken"
            type="text"
            placeholder="Paste your admin token"
            autofocus
            :disabled="loading"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 transition-colors mb-3 font-mono text-sm disabled:opacity-50"
          />

          <p v-if="localError" class="text-sm text-red-500 mb-3">{{ localError }}</p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium cursor-pointer active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            {{ loading ? 'Verifying...' : 'Login as Admin' }}
          </button>
        </form>

        <button @click="emit('close')" class="block w-full text-center text-sm text-gray-400 hover:text-gray-600 mt-3 cursor-pointer transition-colors">
          Cancel
        </button>
      </template>
    </div>
  </div>
</template>
