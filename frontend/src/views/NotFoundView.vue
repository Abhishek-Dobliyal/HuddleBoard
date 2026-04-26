<script setup>
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
    <div class="text-center p-8">
      <div class="text-7xl mb-6"><font-awesome-icon icon="magnifying-glass" class="text-indigo-400" /></div>
      <h1 class="text-3xl font-bold text-gray-800 mb-2">Board Not Found</h1>
      <p class="text-gray-500 mb-8 max-w-md mx-auto">
        This board may have expired or doesn't exist. Boards auto-delete after their set duration.
      </p>
      <router-link
        to="/"
        class="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium shadow-md cursor-pointer active:scale-95"
      >
        Create a New Board
        <font-awesome-icon icon="arrow-right" />
      </router-link>
    </div>
  </div>
</template>
