<template>
    <AdminLayout>
        <div class="p-6">
            <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <h2 class="text-title-md2 font-bold text-black dark:text-white">
                    {{ t('pages.notifications.title') }}
                    <span v-if="store.totalCount > 0" class="text-sm font-normal text-gray-500 dark:text-gray-400">
                        ({{ store.notifications.length }} of {{ store.totalCount }})
                    </span>
                </h2>
                <button v-if="activeTab === 'all'" @click="markAllRead"
                    class="inline-flex items-center justify-center rounded-md bg-brand-600 px-6 py-2.5 text-center font-medium text-white hover:bg-opacity-90 lg:px-8 xl:px-10">
                    {{ t('pages.notifications.readAll') }}
                </button>
            </div>

            <!-- Tabs -->
            <div class="mb-4 flex gap-1 rounded-lg bg-gray-100 p-1 dark:bg-gray-800">
                <button @click="switchTab('all')"
                    class="flex-1 rounded-md px-4 py-2 text-sm font-medium transition"
                    :class="activeTab === 'all' ? 'bg-white text-gray-900 shadow dark:bg-gray-700 dark:text-white' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'">
                    {{ t('pages.notifications.allTab') }}
                </button>
                <button @click="switchTab('archived')"
                    class="flex-1 rounded-md px-4 py-2 text-sm font-medium transition"
                    :class="activeTab === 'archived' ? 'bg-white text-gray-900 shadow dark:bg-gray-700 dark:text-white' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'">
                    {{ t('pages.notifications.archivedTab') }}
                </button>
            </div>

            <div class="flex flex-col gap-4">
                <div v-if="store.loading && store.notifications.length === 0" class="flex justify-center p-8">
                    <div class="w-8 h-8 border-4 border-brand-600 border-t-transparent rounded-full animate-spin"></div>
                </div>

                <div v-else-if="store.notifications.length === 0"
                    class="text-center p-8 text-gray-500 bg-white rounded-lg shadow-default dark:bg-gray-800 dark:text-gray-400">
                    {{ activeTab === 'archived' ? t('pages.notifications.noArchivedNotifications') : t('pages.notifications.noNotifications') }}
                </div>

                <template v-else>
                    <div v-for="notification in store.sortedNotifications" :key="notification.id"
                        class="rounded-sm border border-stroke bg-white px-7.5 py-6 shadow-default dark:border-gray-700 dark:bg-gray-800"
                        :class="{ 'border-l-4 border-l-brand-600': !notification.is_read }">
                        <div class="flex items-start justify-between gap-4">
                            <div class="flex-1">
                                <div class="flex items-center gap-2 mb-1">
                                    <span v-if="notification.event_type"
                                        :class="getEventTypeBadgeClass(notification.event_type)"
                                        class="px-2 py-0.5 rounded-full text-xs font-medium">
                                        {{ getEventTypeLabel(notification.event_type) }}
                                    </span>
                                </div>
                                <h4 class="mb-1 text-lg font-bold text-black dark:text-white">{{ notification.title }}
                                </h4>
                                <p class="mb-3 font-medium text-gray-600 dark:text-gray-400 whitespace-pre-line">{{
                                    notification.message }}</p>

                                <!-- Meeting Link -->
                                <a v-if="notification.meeting_url" :href="notification.meeting_url" target="_blank"
                                    class="inline-flex items-center gap-2 mb-3 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                    </svg>
                                    {{ t('header.joinMeeting') }}
                                </a>

                                <span class="text-sm text-gray-500" :title="formatFullLocalDateTime(notification.created_at)">{{ timeAgo(notification.created_at) }}</span>
                            </div>

                            <!-- Action buttons -->
                            <div class="flex items-center gap-1 flex-shrink-0">
                                <button v-if="!notification.is_read && activeTab === 'all'"
                                    @click="store.markAsRead(notification.id)"
                                    class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-brand-500 transition"
                                    :title="t('pages.notifications.markAsRead')">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                </button>
                                <button v-if="activeTab === 'all'" @click="handleArchive(notification.id)"
                                    class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-amber-500 transition"
                                    :title="t('pages.notifications.archive')">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                                    </svg>
                                </button>
                                <button v-if="activeTab === 'archived'" @click="handleUnarchive(notification.id)"
                                    class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-brand-500 transition"
                                    :title="t('pages.notifications.unarchive')">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                                    </svg>
                                </button>
                                <button @click="handleDelete(notification.id)"
                                    class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-error-500 transition"
                                    :title="t('pages.notifications.deleteNotification')">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Load More Sentinel for Infinite Scroll -->
                    <div ref="loadMoreSentinel" class="h-4"></div>

                    <!-- Loading More Indicator -->
                    <div v-if="store.loadingMore" class="flex justify-center py-4">
                        <div class="w-6 h-6 border-3 border-brand-600 border-t-transparent rounded-full animate-spin">
                        </div>
                        <span class="ml-2 text-sm text-gray-500 dark:text-gray-400">Loading more...</span>
                    </div>

                    <!-- End of List Indicator -->
                    <div v-else-if="!store.hasMore && store.notifications.length > 0"
                        class="text-center py-4 text-sm text-gray-500 dark:text-gray-400">
                        {{ t('pages.notifications.endOfList') }}
                    </div>
                </template>
            </div>
        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
defineOptions({ name: 'NotificationsView' })

import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { useNotificationStore } from '@/stores/notification'
import { formatFullLocalDateTime, timeAgo } from '@/utils/dateTime'

const store = useNotificationStore()
const { t } = useI18n()
const loadMoreSentinel = ref<HTMLElement | null>(null)
const activeTab = ref<'all' | 'archived'>('all')
let observer: IntersectionObserver | null = null

const markAllRead = async () => {
	await store.markAllAsRead()
}

const switchTab = async (tab: 'all' | 'archived') => {
	if (activeTab.value === tab) return
	activeTab.value = tab
	store.resetPagination()

	if (observer) {
		observer.disconnect()
	}

	await store.fetchPaginatedNotifications(1, 20, false, tab === 'archived')

	await nextTick()
	setupIntersectionObserver()
}

const handleArchive = async (id: number) => {
	await store.archiveNotification(id)
}

const handleUnarchive = async (id: number) => {
	await store.unarchiveNotification(id)
}

const handleDelete = async (id: number) => {
	await store.deleteNotification(id)
}

const getEventTypeBadgeClass = (eventType?: string) => {
	switch (eventType) {
		case 'meeting':
			return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
		case 'task':
			return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
		case 'leave':
			return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
		case 'holiday':
			return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
		case 'purchase_request':
			return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300'
		case 'task_mention':
			return 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-300'
		default:
			return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
	}
}

const getEventTypeLabel = (eventType?: string) => {
	switch (eventType) {
		case 'meeting':
			return t('pages.notifications.eventType.meeting')
		case 'task':
			return t('pages.notifications.eventType.task')
		case 'leave':
			return t('pages.notifications.eventType.leave')
		case 'holiday':
			return t('pages.notifications.eventType.holiday')
		case 'purchase_request':
			return t('pages.notifications.eventType.purchase')
		case 'task_mention':
			return t('pages.notifications.eventType.mention')
		default:
			return t('pages.notifications.eventType.notification')
	}
}

// Setup Intersection Observer for infinite scroll
const setupIntersectionObserver = () => {
	observer = new IntersectionObserver(
		(entries) => {
			const entry = entries[0]
			if (entry?.isIntersecting && store.hasMore && !store.loadingMore) {
				store.loadMore()
			}
		},
		{
			rootMargin: '100px', // Load more when within 100px of the sentinel
			threshold: 0.1,
		},
	)

	if (loadMoreSentinel.value) {
		observer.observe(loadMoreSentinel.value)
	}
}

onMounted(async () => {
	// Reset pagination and fetch first page
	store.resetPagination()
	await store.fetchPaginatedNotifications(1, 20)

	// Setup infinite scroll observer after initial load
	setupIntersectionObserver()
})

onUnmounted(() => {
	// Cleanup observer
	if (observer) {
		observer.disconnect()
		observer = null
	}
})
</script>
