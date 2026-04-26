<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBoardStore } from '../stores/board'
import { useTypewriter } from '../composables/useTypewriter'

const router = useRouter()
const boardStore = useBoardStore()

const { displayText } = useTypewriter([
  'Brainstorm ideas together.',
  'Run better retrospectives.',
  'Gather feedback in real time.',
  'No login. No friction.',
  'Collaborate across oceans.',
  'Ship better as a team.',
], { typeSpeed: 55, deleteSpeed: 30, pauseAfterType: 2200 })

const title = ref('')
const description = ref('')
const template = ref('retrospective')
const ttlHours = ref(24)
const password = ref('')
const isReadOnly = ref(false)
const isCreating = ref(false)
const showAdvanced = ref(false)

const templates = [
  { id: 'retrospective', name: 'Retrospective', columns: ['What went well', 'What to improve', 'Action items'], icon: 'rotate' },
  { id: '4ls', name: '4Ls', columns: ['Liked', 'Learned', 'Lacked', 'Longed For'], icon: 'lightbulb' },
  { id: 'custom', name: 'Custom', columns: [], icon: 'pencil' },
]

const customColumns = ref(['', '', ''])

const selectedTemplate = computed(() => templates.find((t) => t.id === template.value))

function addCustomColumn() {
  if (customColumns.value.length < 4) {
    customColumns.value.push('')
  }
}

function removeCustomColumn(idx) {
  if (customColumns.value.length > 1) {
    customColumns.value.splice(idx, 1)
  }
}

const canSubmit = computed(() => {
  if (!title.value.trim()) return false
  if (template.value === 'custom') {
    return customColumns.value.filter((c) => c.trim()).length >= 1
  }
  return true
})

async function handleCreate() {
  if (!canSubmit.value || isCreating.value) return
  isCreating.value = true

  try {
    const payload = {
      title: title.value.trim(),
      description: description.value.trim(),
      template: template.value,
      ttl_hours: ttlHours.value,
      password: password.value || null,
      is_readonly_default: isReadOnly.value,
    }

    if (template.value === 'custom') {
      payload.custom_columns = customColumns.value.filter((c) => c.trim())
    }

    const data = await boardStore.createBoard(payload)

    router.push({
      name: 'board',
      params: { id: data.board_id },
      query: { admin: data.admin_token },
    })
  } catch {
    // error already set in store
  } finally {
    isCreating.value = false
  }
}

const features = [
  { icon: 'clock', title: 'Ephemeral boards', desc: 'Auto-expire in 1h to 3 days. No clutter.' },
  { icon: 'users', title: 'Real-time sync', desc: 'See changes as your team types. Powered by WebSockets.' },
  { icon: 'lock', title: 'Access control', desc: 'Password-protect boards. Set read-only mode.' },
  { icon: 'columns', title: 'Flexible templates', desc: 'Retro, 4Ls, or fully custom columns.' },
]
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
    <div class="min-h-screen flex flex-col lg:flex-row">

      <!-- LEFT HALF: Hero / Marketing -->
      <div class="lg:w-1/2 flex flex-col justify-center px-8 md:px-16 py-12 lg:py-0 lg:sticky lg:top-0 lg:h-screen">
        <div class="max-w-lg mx-auto lg:mx-0">
          <!-- Logo -->
          <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 tracking-tight leading-tight">
            Huddle<span class="text-indigo-600">Board</span>
          </h1>

          <!-- Typewriter -->
          <div class="mt-6 h-16">
            <p class="text-2xl md:text-3xl font-light text-gray-600">
              <span>{{ displayText }}</span><span class="typewriter-cursor text-indigo-500">|</span>
            </p>
          </div>

          <!-- Tagline -->
          <p class="mt-6 text-lg text-gray-400 leading-relaxed max-w-md">
            The simplest way to run retrospectives, brainstorm ideas, and collect feedback.
            Create a board in seconds — share the link — collaborate live.
          </p>

          <!-- Feature pills -->
          <div class="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              v-for="feature in features"
              :key="feature.title"
              class="flex items-start gap-3"
            >
              <div class="w-9 h-9 rounded-lg bg-indigo-100 flex items-center justify-center shrink-0 mt-0.5">
                <font-awesome-icon :icon="feature.icon" class="text-indigo-600 text-sm" />
              </div>
              <div>
                <h3 class="text-sm font-semibold text-gray-800">{{ feature.title }}</h3>
                <p class="text-xs text-gray-400 mt-0.5 leading-relaxed">{{ feature.desc }}</p>
              </div>
            </div>
          </div>

          <!-- Social proof / stat -->
          <div class="mt-12 flex items-center gap-4 text-sm text-gray-400">
            <div class="flex -space-x-2">
              <div class="w-8 h-8 rounded-full bg-indigo-200 border-2 border-white flex items-center justify-center text-xs font-bold text-indigo-700">A</div>
              <div class="w-8 h-8 rounded-full bg-emerald-200 border-2 border-white flex items-center justify-center text-xs font-bold text-emerald-700">K</div>
              <div class="w-8 h-8 rounded-full bg-amber-200 border-2 border-white flex items-center justify-center text-xs font-bold text-amber-700">R</div>
            </div>
            <span>No signup required. Just create and share.</span>
          </div>
        </div>
      </div>

      <!-- RIGHT HALF: Create Board Form -->
      <div class="lg:w-1/2 flex items-center justify-center px-4 md:px-8 py-12 lg:py-0 lg:min-h-screen">
        <div class="w-full max-w-lg">
          <form @submit.prevent="handleCreate" class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 md:p-8">
            <h2 class="text-xl font-semibold text-gray-800 mb-6">
              <font-awesome-icon icon="plus" class="text-indigo-500 mr-2" />
              Create a new board
            </h2>

            <!-- Title -->
            <div class="mb-4">
              <label for="title" class="block text-sm font-medium text-gray-700 mb-1">Board title *</label>
              <input
                id="title"
                v-model="title"
                type="text"
                placeholder="e.g. Sprint 42 Retrospective"
                maxlength="100"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 transition-colors"
              />
            </div>

            <!-- Description -->
            <div class="mb-4">
              <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description <span class="text-gray-400">(optional)</span></label>
              <textarea
                id="description"
                v-model="description"
                rows="2"
                placeholder="What's this board about?"
                maxlength="500"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 transition-colors resize-none"
              ></textarea>
            </div>

            <!-- Template Picker -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Template</label>
              <div class="grid grid-cols-3 gap-2">
                <button
                  v-for="t in templates"
                  :key="t.id"
                  type="button"
                  @click="template = t.id"
                  :class="[
                    'p-3 rounded-lg border-2 text-left transition-all text-sm cursor-pointer hover:scale-[1.02] active:scale-[0.98]',
                    template === t.id
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-600',
                  ]"
                >
                  <font-awesome-icon :icon="t.icon" class="text-base" />
                  <span class="block font-medium mt-1 text-xs">{{ t.name }}</span>
                </button>
              </div>
            </div>

            <!-- Template Preview -->
            <transition
              enter-active-class="animate__animated animate__fadeIn animate__faster"
              leave-active-class="animate__animated animate__fadeOut animate__faster"
            >
              <div v-if="selectedTemplate && selectedTemplate.columns.length > 0" class="mb-4">
                <label class="block text-sm font-medium text-gray-500 mb-2">Columns</label>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="col in selectedTemplate.columns"
                    :key="col"
                    class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs"
                  >{{ col }}</span>
                </div>
              </div>
            </transition>

            <!-- Custom Columns -->
            <transition
              enter-active-class="animate__animated animate__fadeIn animate__faster"
              leave-active-class="animate__animated animate__fadeOut animate__faster"
            >
              <div v-if="template === 'custom'" class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">Custom columns <span class="text-gray-400 text-xs">(up to 4)</span></label>
                <div class="space-y-2">
                  <div v-for="(col, idx) in customColumns" :key="idx" class="flex gap-2">
                    <input
                      v-model="customColumns[idx]"
                      type="text"
                      :placeholder="`Column ${idx + 1}`"
                      maxlength="50"
                      class="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 text-sm"
                    />
                    <button
                      v-if="customColumns.length > 1"
                      type="button"
                      @click="removeCustomColumn(idx)"
                      class="px-3 text-gray-400 hover:text-red-500 transition-colors cursor-pointer"
                    >
                      <font-awesome-icon icon="xmark" />
                    </button>
                  </div>
                </div>
                <button
                  v-if="customColumns.length < 4"
                  type="button"
                  @click="addCustomColumn"
                  class="mt-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium cursor-pointer"
                >
                  <font-awesome-icon icon="plus" class="mr-1" /> Add column
                </button>
              </div>
            </transition>

            <!-- TTL Slider -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Board expires in: <span class="text-indigo-600 font-semibold">{{ ttlHours }}h</span>
              </label>
              <input
                v-model.number="ttlHours"
                type="range"
                min="1"
                max="72"
                step="1"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <div class="flex justify-between text-xs text-gray-400 mt-1">
                <span>1 hour</span>
                <span>3 days</span>
              </div>
            </div>

            <!-- Advanced Options Toggle -->
            <button
              type="button"
              @click="showAdvanced = !showAdvanced"
              class="mb-4 text-sm text-gray-500 hover:text-gray-700 font-medium flex items-center gap-1 cursor-pointer"
            >
              <font-awesome-icon icon="gear" class="text-xs" />
              Advanced options
              <font-awesome-icon
                icon="chevron-down"
                :class="['text-xs transition-transform duration-300', showAdvanced ? 'rotate-180' : '']"
              />
            </button>

            <!-- Advanced Options -->
            <transition
              enter-active-class="animate__animated animate__fadeIn animate__faster"
              leave-active-class="animate__animated animate__fadeOut animate__faster"
            >
              <div v-if="showAdvanced" class="mb-4 space-y-4 p-4 bg-gray-50 rounded-lg">
                <!-- Password -->
                <div>
                  <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                    <font-awesome-icon icon="lock" class="mr-1 text-gray-400" />
                    Board password <span class="text-gray-400">(optional)</span>
                  </label>
                  <input
                    id="password"
                    v-model="password"
                    type="password"
                    placeholder="Leave empty for open access"
                    class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 transition-colors text-sm"
                  />
                </div>

                <!-- Read Only -->
                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    v-model="isReadOnly"
                    type="checkbox"
                    class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 cursor-pointer"
                  />
                  <div>
                    <span class="text-sm font-medium text-gray-700">Read-only for participants</span>
                    <p class="text-xs text-gray-400">Only admin can add/edit cards. Participants can view and vote.</p>
                  </div>
                </label>
              </div>
            </transition>

            <!-- Error -->
            <transition
              enter-active-class="animate__animated animate__shakeX animate__faster"
              leave-active-class="animate__animated animate__fadeOut animate__faster"
            >
              <div v-if="boardStore.error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                {{ boardStore.error }}
              </div>
            </transition>

            <!-- Submit -->
            <button
              type="submit"
              :disabled="!canSubmit || isCreating"
              :class="[
                'w-full py-3 px-6 rounded-lg font-semibold text-white transition-all',
                canSubmit && !isCreating
                  ? 'bg-indigo-600 hover:bg-indigo-700 shadow-md hover:shadow-lg cursor-pointer active:scale-[0.98]'
                  : 'bg-gray-300 cursor-not-allowed',
              ]"
            >
              <span v-if="isCreating">Creating...</span>
              <span v-else>
                Create Board
                <font-awesome-icon icon="arrow-right" class="ml-2" />
              </span>
            </button>

            <p class="text-center text-xs text-gray-400 mt-4">
              No login required. Boards auto-expire after the set duration.
            </p>
          </form>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.typewriter-cursor {
  animation: blink 1s step-end infinite;
  font-weight: 300;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
