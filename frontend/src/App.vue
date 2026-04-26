<script setup>
import ToastNotification from './components/ui/ToastNotification.vue'
</script>

<template>
  <div class="flex md:hidden min-h-screen items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-6">
    <div class="text-center max-w-sm">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">
        Huddle<span class="text-indigo-600">Board</span>
      </h1>
      <div class="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto my-6">
        <font-awesome-icon icon="columns" class="text-indigo-600 text-2xl" />
      </div>
      <h2 class="text-lg font-semibold text-gray-800 mb-2">Larger screen needed</h2>
      <p class="text-sm text-gray-500 leading-relaxed">
        HuddleBoard works best on tablets and desktops. Please switch to a device with a wider screen for the full experience.
      </p>
    </div>
  </div>

  <div class="hidden md:block min-h-screen bg-gray-50">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <ToastNotification />
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
