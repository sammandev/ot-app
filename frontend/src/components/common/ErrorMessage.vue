<template>
  <div class="flex items-center justify-center p-8">
    <div class="flex flex-col items-center gap-3 max-w-md">
      <div class="text-red-500">
        <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div class="text-center">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
          {{ title }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ message }}
        </p>
      </div>
      <button v-if="showRetry" @click="$emit('retry')"
        class="mt-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
        Try Again
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
	title?: string
	message?: string
	showRetry?: boolean
}

withDefaults(defineProps<Props>(), {
	title: 'Error Loading Component',
	message: 'Failed to load this component. Please try again.',
	showRetry: true,
})

defineEmits<{
	retry: []
}>()
</script>
