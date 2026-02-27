<template>
  <Teleport to="body">
    <div v-if="visible"
      class="fixed inset-0 z-[100002] flex items-center justify-center bg-gray-900/50 dark:bg-gray-950/70"
      @click.self="onCancel">
      <div
        role="dialog" aria-modal="true" aria-labelledby="confirm-dialog-title"
        class="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900 animate-in fade-in zoom-in-95">
        <!-- Icon -->
        <div class="mb-4">
          <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full" :class="iconBgClass">
            <!-- Danger icon -->
            <svg v-if="options.type === 'danger'" class="h-6 w-6" :class="iconColorClass" fill="none"
              viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            <!-- Warning icon -->
            <svg v-else-if="options.type === 'warning'" class="h-6 w-6" :class="iconColorClass" fill="none"
              viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
            <!-- Info icon -->
            <svg v-else class="h-6 w-6" :class="iconColorClass" fill="none" viewBox="0 0 24 24" stroke-width="2"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
            </svg>
          </div>
        </div>

        <!-- Content -->
        <div class="text-center">
          <h3 id="confirm-dialog-title" class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">{{ options.title }}</h3>
          <p class="mb-6 text-sm text-gray-600 dark:text-gray-400">{{ options.message }}</p>
        </div>

        <!-- Actions -->
        <div class="flex gap-3">
          <button type="button"
            class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-700 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
            @click="onCancel">
            {{ options.cancelLabel }}
          </button>
          <button type="button" class="h-11 flex-1 rounded-lg px-4 text-sm font-semibold text-white shadow-theme-xs transition focus:outline-hidden focus:ring-3"
            :class="confirmBtnClass" @click="onConfirm">
            {{ options.confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'

const { visible, options, onConfirm, onCancel } = useConfirmDialog()

const iconBgClass = computed(() => {
	switch (options.type) {
		case 'danger':
			return 'bg-error-100 dark:bg-error-500/20'
		case 'warning':
			return 'bg-amber-100 dark:bg-amber-500/20'
		default:
			return 'bg-blue-100 dark:bg-blue-500/20'
	}
})

const iconColorClass = computed(() => {
	switch (options.type) {
		case 'danger':
			return 'text-error-600 dark:text-error-400'
		case 'warning':
			return 'text-amber-600 dark:text-amber-400'
		default:
			return 'text-blue-600 dark:text-blue-400'
	}
})

const confirmBtnClass = computed(() => {
	switch (options.type) {
		case 'danger':
			return 'bg-error-600 hover:bg-error-700 focus:ring-error-500/20'
		case 'warning':
			return 'bg-amber-600 hover:bg-amber-700 focus:ring-amber-500/20'
		default:
			return 'bg-brand-600 hover:bg-brand-700 focus:ring-brand-500/20'
	}
})
</script>
