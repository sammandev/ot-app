<template>
    <div v-if="viewers.length > 0" class="flex items-center gap-2">
        <!-- Viewer Avatars -->
        <div class="flex -space-x-2">
            <div v-for="viewer in displayedViewers" :key="viewer.user_id" :class="[
                'w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ring-2 ring-white dark:ring-gray-800',
                viewer.editing_task_id ? 'bg-yellow-100 text-yellow-700 ring-yellow-400' : 'bg-green-100 text-green-700'
            ]" :title="viewer.user_name + (viewer.editing_task_id ? ` (${t('kanban.editingTask')})` : ` (${t('kanban.viewing')})`)">
                {{ getInitials(viewer.user_name) }}
                <!-- Editing Indicator -->
                <span v-if="viewer.editing_task_id"
                    class="absolute -bottom-1 -right-1 w-3 h-3 bg-yellow-500 rounded-full border-2 border-white dark:border-gray-800 flex items-center justify-center">
                    <svg class="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path
                            d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                </span>
            </div>
            <!-- Overflow Counter -->
            <div v-if="overflowCount > 0"
                class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 flex items-center justify-center text-xs font-medium ring-2 ring-white dark:ring-gray-800"
                :title="t('kanban.moreViewers', { count: overflowCount })">
                +{{ overflowCount }}
            </div>
        </div>

        <!-- Connection Status -->
        <div class="flex items-center gap-1.5">
            <span :class="[
                'w-2 h-2 rounded-full',
                connected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
            ]">
            </span>
            <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ connected ? t('kanban.live') : t('kanban.connecting') }}
            </span>
        </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex items-center gap-2">
        <div class="flex items-center gap-1.5">
            <span :class="[
                'w-2 h-2 rounded-full',
                connected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
            ]">
            </span>
            <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ connected ? t('kanban.justYou') : t('kanban.connecting') }}
            </span>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BoardViewer } from '@/services/websocket'

const { t } = useI18n()

const props = defineProps<{
	viewers: BoardViewer[]
	connected: boolean
	maxDisplay?: number
}>()

const maxDisplayCount = computed(() => props.maxDisplay || 4)

const displayedViewers = computed(() => {
	return props.viewers.slice(0, maxDisplayCount.value)
})

const overflowCount = computed(() => {
	return Math.max(0, props.viewers.length - maxDisplayCount.value)
})

function getInitials(name: string): string {
	return name
		.split(' ')
		.map((n) => n[0])
		.join('')
		.toUpperCase()
		.slice(0, 2)
}
</script>
