<template>
  <div
    class="overflow-x-auto rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
  >
    <table class="w-full text-sm">
      <thead class="border-b border-gray-200 dark:border-gray-800">
        <tr>
          <th
            v-for="col in columns"
            :key="col"
            class="px-6 py-4 text-left"
          >
            <div class="h-4 w-24 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
        <tr v-for="row in rows" :key="row">
          <td v-for="col in columns" :key="col" class="px-6 py-4">
            <div class="h-4 animate-pulse rounded bg-gray-200 dark:bg-gray-700" :style="{ width: getRandomWidth() }"></div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination skeleton -->
    <div
      class="flex flex-col gap-3 border-t border-gray-200 px-6 py-4 text-sm dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between"
    >
      <div class="flex items-center gap-3">
        <div class="h-4 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
        <div class="h-9 w-24 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
      </div>
      <div class="flex items-center gap-2">
        <div class="h-9 w-16 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
        <div class="h-4 w-24 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
        <div class="h-9 w-16 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
	rows?: number
	columns?: number
}

withDefaults(defineProps<Props>(), {
	rows: 5,
	columns: 5,
})

const getRandomWidth = () => {
	const widths = ['60%', '70%', '80%', '90%', '100%']
	return widths[Math.floor(Math.random() * widths.length)]
}
</script>
