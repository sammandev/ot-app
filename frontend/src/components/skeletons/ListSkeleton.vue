<template>
  <div
    class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
  >
    <div v-if="showHeader" class="border-b border-gray-200 px-6 py-4 dark:border-gray-800">
      <div class="h-6 w-40 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
    </div>
    <div class="divide-y divide-gray-200 dark:divide-gray-800">
      <div v-for="item in items" :key="item" class="flex items-center gap-4 px-6 py-4">
        <div v-if="showAvatar" class="h-10 w-10 animate-pulse rounded-full bg-gray-200 dark:bg-gray-700"></div>
        <div class="flex-1 space-y-2">
          <div class="h-4 animate-pulse rounded bg-gray-200 dark:bg-gray-700" :style="{ width: getRandomWidth() }"></div>
          <div class="h-3 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
        </div>
        <div v-if="showAction" class="h-8 w-16 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
	items?: number
	showHeader?: boolean
	showAvatar?: boolean
	showAction?: boolean
}

withDefaults(defineProps<Props>(), {
	items: 5,
	showHeader: true,
	showAvatar: false,
	showAction: false,
})

const getRandomWidth = () => {
	const widths = ['50%', '60%', '70%', '80%']
	return widths[Math.floor(Math.random() * widths.length)]
}
</script>
