<template>
	<slot v-if="!hasError" />
	<div v-else class="flex flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50 p-8 dark:border-red-800 dark:bg-red-900/20">
		<svg class="mb-4 h-12 w-12 text-red-400 dark:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
				d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
		</svg>
		<h3 class="mb-2 text-lg font-semibold text-red-700 dark:text-red-300">
			{{ title }}
		</h3>
		<p class="mb-4 text-sm text-red-600 dark:text-red-400">
			{{ message }}
		</p>
		<button
			class="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
			@click="reset"
		>
			{{ retryLabel }}
		</button>
	</div>
</template>

<script setup lang="ts">
import { onErrorCaptured, ref } from 'vue'

const props = withDefaults(
	defineProps<{
		title?: string
		message?: string
		retryLabel?: string
	}>(),
	{
		title: 'Something went wrong',
		message: 'An unexpected error occurred. Please try again.',
		retryLabel: 'Try Again',
	},
)

const emit = defineEmits<{
	error: [err: Error, info: string]
}>()

const hasError = ref(false)

onErrorCaptured((err: Error, _instance, info) => {
	hasError.value = true
	emit('error', err, info)
	console.error(`[ErrorBoundary] ${props.title}:`, err, info)
	return false
})

function reset() {
	hasError.value = false
}

defineExpose({ reset, hasError })
</script>
