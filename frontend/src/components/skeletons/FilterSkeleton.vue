<template>
  <div
    class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]"
  >
    <div class="grid gap-4" :class="gridClass">
      <div v-for="filter in filters" :key="filter" class="space-y-2">
        <div class="h-4 w-20 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
        <div class="h-11 w-full animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
	filters?: number
}

const props = withDefaults(defineProps<Props>(), {
	filters: 4,
})

const gridClass = computed(() => {
	if (props.filters <= 2) return 'grid-cols-1 sm:grid-cols-2'
	if (props.filters <= 4) return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
	return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5'
})
</script>
