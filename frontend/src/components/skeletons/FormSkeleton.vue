<template>
  <div class="space-y-4">
    <div v-for="field in fields" :key="field" class="space-y-2">
      <div class="h-4 w-24 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
      <div class="h-11 w-full animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
    </div>
    <div v-if="showButtons" class="flex gap-3 pt-4">
      <div class="h-11 flex-1 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
      <div class="h-11 flex-1 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
	fields?: number
	showButtons?: boolean
}

withDefaults(defineProps<Props>(), {
	fields: 4,
	showButtons: true,
})
</script>
