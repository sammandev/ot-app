<template>
  <div :class="[
    'rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]',
    className,
  ]">
    <!-- Card Header -->
    <div class="flex flex-col gap-2 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h3 class="text-base font-medium text-gray-800 dark:text-white/90">
          {{ title }}
        </h3>
        <p v-if="desc" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {{ desc }}
        </p>
      </div>
      <div v-if="$slots['header-extra']" class="shrink-0">
        <slot name="header-extra"></slot>
      </div>
    </div>

    <!-- Card Body -->
    <div class="p-4 border-t border-gray-100 dark:border-gray-800 sm:p-6">
      <div class="space-y-5">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
	title: string
	className?: string
	desc?: string
}

defineProps<Props>()
</script>
