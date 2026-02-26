<template>
  <div class="flex items-center justify-center p-8">
    <div class="flex flex-col items-center gap-3">
      <div class="loader"></div>
      <p v-if="message" class="text-sm text-gray-600 dark:text-gray-400">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
	message?: string
}

withDefaults(defineProps<Props>(), {
	message: 'Loading...',
})
</script>

<style scoped>
.loader {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(59, 130, 246, 0.1);
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
