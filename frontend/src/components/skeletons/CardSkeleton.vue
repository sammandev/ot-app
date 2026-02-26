<template>
  <div
    class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]"
  >
    <div v-if="showHeader" class="mb-4 flex items-center justify-between">
      <div class="h-6 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
      <div v-if="showHeaderAction" class="h-8 w-20 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
    </div>
    <div class="space-y-3">
      <div v-for="line in lines" :key="line" class="h-4 animate-pulse rounded bg-gray-200 dark:bg-gray-700" :style="{ width: getRandomWidth() }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
	lines?: number
	showHeader?: boolean
	showHeaderAction?: boolean
}

withDefaults(defineProps<Props>(), {
	lines: 3,
	showHeader: true,
	showHeaderAction: false,
})

const getRandomWidth = () => {
	const widths = ['70%', '80%', '90%', '100%']
	return widths[Math.floor(Math.random() * widths.length)]
}
</script>
