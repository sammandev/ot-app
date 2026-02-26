<template>
  <div
    class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]"
  >
    <div v-if="showHeader" class="mb-6 flex items-center justify-between">
      <div>
        <div class="h-6 w-40 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
        <div class="mt-2 h-4 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
      </div>
      <div v-if="showControls" class="h-10 w-32 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
    </div>
    <div class="relative" :style="{ height: height + 'px' }">
      <!-- Chart bars/lines animation -->
      <div class="absolute inset-0 flex items-end justify-around gap-2 px-4 pb-8">
        <div v-for="bar in bars" :key="bar" class="flex-1 animate-pulse rounded-t bg-gray-200 dark:bg-gray-700" :style="{ height: getRandomHeight() }"></div>
      </div>
      <!-- X-axis skeleton -->
      <div class="absolute bottom-0 left-0 right-0 flex justify-around border-t border-gray-200 px-4 pt-2 dark:border-gray-700">
        <div v-for="label in bars" :key="label" class="h-3 w-8 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
	height?: number
	bars?: number
	showHeader?: boolean
	showControls?: boolean
}

withDefaults(defineProps<Props>(), {
	height: 300,
	bars: 8,
	showHeader: true,
	showControls: false,
})

const getRandomHeight = () => {
	const heights = ['40%', '50%', '60%', '70%', '80%', '90%']
	return heights[Math.floor(Math.random() * heights.length)]
}
</script>
