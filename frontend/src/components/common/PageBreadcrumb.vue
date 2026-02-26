<template>
  <nav>
    <ol class="flex items-center gap-2 text-sm">
      <li>
        <router-link
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 flex items-center gap-1.5"
          to="/">
          Home
        </router-link>
      </li>
      <li class="text-gray-400 dark:text-gray-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </li>
      <li v-if="parentLabel && parentTo">
        <router-link class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
          :to="parentTo">
          {{ parentLabel }}
        </router-link>
      </li>
      <li v-else>
        <router-link class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
          to="/ot/summary">
          Overtime Summary
        </router-link>
      </li>
      <li class="text-gray-400 dark:text-gray-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </li>
      <li class="text-gray-700 font-medium dark:text-gray-300">
        {{ pageTitle }}
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
interface BreadcrumbProps {
	pageTitle: string
	parentLabel?: string
	parentTo?: string
}

defineProps<BreadcrumbProps>()
</script>
