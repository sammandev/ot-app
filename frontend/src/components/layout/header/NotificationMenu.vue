<template>
  <div class="relative" ref="dropdownRef">
    <button
      class="relative flex items-center justify-center text-gray-500 transition-colors bg-white border border-gray-200 rounded-full hover:text-dark-900 h-11 w-11 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
      @click="toggleDropdown">
      <span v-if="unreadCount > 0"
        class="absolute -right-1 -top-1 z-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-orange-500 px-1 text-[10px] font-bold leading-none text-white ring-2 ring-white dark:ring-gray-900">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
      <svg class="fill-current" width="20" height="20" viewBox="0 0 20 20" fill="none"
        xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd"
          d="M10.75 2.29248C10.75 1.87827 10.4143 1.54248 10 1.54248C9.58583 1.54248 9.25004 1.87827 9.25004 2.29248V2.83613C6.08266 3.20733 3.62504 5.9004 3.62504 9.16748V14.4591H3.33337C2.91916 14.4591 2.58337 14.7949 2.58337 15.2091C2.58337 15.6234 2.91916 15.9591 3.33337 15.9591H4.37504H15.625H16.6667C17.0809 15.9591 17.4167 15.6234 17.4167 15.2091C17.4167 14.7949 17.0809 14.4591 16.6667 14.4591H16.375V9.16748C16.375 5.9004 13.9174 3.20733 10.75 2.83613V2.29248ZM14.875 14.4591V9.16748C14.875 6.47509 12.6924 4.29248 10 4.29248C7.30765 4.29248 5.12504 6.47509 5.12504 9.16748V14.4591H14.875ZM8.00004 17.7085C8.00004 18.1228 8.33583 18.4585 8.75004 18.4585H11.25C11.6643 18.4585 12 18.1228 12 17.7085C12 17.2943 11.6643 16.9585 11.25 16.9585H8.75004C8.33583 16.9585 8.00004 17.2943 8.00004 17.7085Z"
          fill="" />
      </svg>
    </button>

    <!-- Dropdown Start -->
    <div v-if="dropdownOpen"
      class="absolute -right-[240px] mt-[17px] flex flex-col rounded-2xl border border-gray-200 bg-white p-3 shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark sm:w-[361px] lg:right-0 w-[350px]"
      :style="{ maxHeight: dropdownHeight }">
      <div class="flex items-center justify-between pb-3 mb-3 border-b border-gray-100 dark:border-gray-800">
        <h5 class="text-lg font-semibold text-gray-800 dark:text-white/90">{{ t('header.notification') }} ({{ unreadCount }})</h5>

        <div class="flex gap-2">
          <button @click="markAllRead" class="text-xs text-brand-500 hover:text-brand-600 dark:text-brand-400">
            {{ t('header.markAllRead') }}
          </button>
          <button @click="closeDropdown" class="text-gray-500 dark:text-gray-400">
            <svg class="fill-current" width="24" height="24" viewBox="0 0 24 24" fill="none"
              xmlns="http://www.w3.org/2000/svg">
              <path fill-rule="evenodd" clip-rule="evenodd"
                d="M6.21967 7.28131C5.92678 6.98841 5.92678 6.51354 6.21967 6.22065C6.51256 5.92775 6.98744 5.92775 7.28033 6.22065L11.999 10.9393L16.7176 6.22078C17.0105 5.92789 17.4854 5.92788 17.7782 6.22078C18.0711 6.51367 18.0711 6.98855 17.7782 7.28144L13.0597 12L17.7782 16.7186C18.0711 17.0115 18.0711 17.4863 17.7782 17.7792C17.4854 18.0721 17.0105 18.0721 16.7176 17.7792L11.999 13.0607L7.28033 17.7794C6.98744 18.0722 6.51256 18.0722 6.21967 17.7794C5.92678 17.4865 5.92678 17.0116 6.21967 16.7187L10.9384 12L6.21967 7.28131Z"
                fill="" />
            </svg>
          </button>
        </div>
      </div>

      <div v-if="notifications.length === 0" class="flex items-center justify-center text-gray-400 py-8">
        {{ t('header.noNotifications') }}
      </div>

      <ul v-else class="flex flex-col overflow-y-auto custom-scrollbar">
        <li v-for="notification in notifications" :key="notification.id" @click="handleItemClick(notification)">
          <a class="flex gap-3 rounded-lg border-b border-gray-100 p-3 px-4.5 py-3 hover:bg-gray-100 dark:border-gray-800 dark:hover:bg-white/5 cursor-pointer"
            :class="{ 'bg-gray-50 dark:bg-white/5': !notification.is_read }">
            <span class="relative z-1 block h-10 w-10 flex-shrink-0">
              <span :class="getIconBgClass(notification.event_type)"
                class="flex h-10 w-10 items-center justify-center rounded-full text-xs font-semibold">
                {{ getIconText(notification.event_type) }}
              </span>
              <span v-if="!notification.is_read"
                class="bg-orange-500 absolute bottom-0 right-0 z-10 h-2.5 w-2.5 rounded-full border-[1.5px] border-white dark:border-gray-900"></span>
            </span>

            <span class="block flex-1 min-w-0">
              <span class="mb-1 block text-theme-sm text-gray-500 dark:text-gray-400">
                <span class="font-medium text-gray-800 dark:text-white/90">
                  {{ notification.title }}
                </span>
              </span>
              <span class="block text-xs text-gray-500 line-clamp-2">
                {{ notification.message }}
              </span>

              <!-- Meeting Link -->
              <a v-if="notification.meeting_url" :href="notification.meeting_url" target="_blank" @click.stop
                class="inline-flex items-center gap-1 mt-1.5 px-2 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 transition">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {{ t('header.joinMeeting') }}
              </a>

              <span class="flex items-center gap-2 text-gray-500 text-theme-xs dark:text-gray-400 mt-1">
                <span :title="formatFullLocalDateTime(notification.created_at)">{{ timeAgo(notification.created_at) }}</span>
              </span>
            </span>

            <!-- Action buttons -->
            <span class="flex flex-col gap-1 flex-shrink-0 ml-1">
              <button v-if="!notification.is_read" @click.stop="store.markAsRead(notification.id)"
                class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-400 hover:text-brand-500 transition" title="Mark as read">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
              <button @click.stop="handleArchive(notification)"
                class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-400 hover:text-amber-500 transition" title="Archive">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </button>
              <button @click.stop="handleDelete(notification)"
                class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-400 hover:text-error-500 transition" title="Delete">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </span>
          </a>
        </li>
      </ul>

      <router-link to="/notifications"
        class="mt-3 flex justify-center rounded-lg border border-gray-300 bg-white p-3 text-theme-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 hover:text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/[0.03] dark:hover:text-gray-200 flex-shrink-0"
        @click="handleViewAllClick">
        {{ t('header.viewAllNotifications') }}
      </router-link>
    </div>
    <!-- Dropdown End -->
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import type { Notification } from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import { formatFullLocalDateTime, timeAgo } from '@/utils/dateTime'

const { t } = useI18n()
const store = useNotificationStore()
const dropdownOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

// Use store data - max 10 notifications in dropdown
const unreadCount = computed(() => store.unreadCount)
const notifications = computed(() => store.sortedNotifications.slice(0, 10))

// Dynamic height based on notification count
const dropdownHeight = computed(() => {
	if (notifications.value.length === 0) {
		return '180px' // Minimal height for "No notifications"
	}
	// Base height for header and footer + per-item height
	const baseHeight = 120 // header + footer + padding
	const itemHeight = 85 // approximate height per notification item
	const totalHeight = baseHeight + notifications.value.length * itemHeight
	return `${Math.min(totalHeight, 520)}px` // Cap at max 520px
})

const getIconBgClass = (eventType?: string) => {
	switch (eventType) {
		case 'meeting':
			return 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-200'
		case 'task':
			return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-200'
		case 'leave':
			return 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-200'
		case 'holiday':
			return 'bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-200'
		case 'purchase_request':
			return 'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-200'
		case 'task_mention':
			return 'bg-cyan-100 text-cyan-700 dark:bg-cyan-500/20 dark:text-cyan-200'
		default:
			return 'bg-brand-100 text-brand-700 dark:bg-brand-500/20 dark:text-brand-200'
	}
}

const getIconText = (eventType?: string) => {
	switch (eventType) {
		case 'meeting':
			return 'MT'
		case 'task':
			return 'TK'
		case 'leave':
			return 'LV'
		case 'holiday':
			return 'HD'
		case 'purchase_request':
			return 'PR'
		case 'task_mention':
			return '@'
		default:
			return 'NB'
	}
}

const toggleDropdown = () => {
	dropdownOpen.value = !dropdownOpen.value
}

const closeDropdown = () => {
	dropdownOpen.value = false
}

const markAllRead = async () => {
	await store.markAllAsRead()
}

const handleClickOutside = (event: MouseEvent) => {
	if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
		closeDropdown()
	}
}

const handleItemClick = async (notification: Notification) => {
	if (!notification.is_read) {
		await store.markAsRead(notification.id)
	}
}

const handleArchive = async (notification: Notification) => {
	await store.archiveNotification(notification.id)
}

const handleDelete = async (notification: Notification) => {
	await store.deleteNotification(notification.id)
}

const handleViewAllClick = () => {
	closeDropdown()
}

onMounted(() => {
	document.addEventListener('click', handleClickOutside)
	// Initialize notifications - WebSocket handles real-time updates
	store.initialize()
})

onUnmounted(() => {
	document.removeEventListener('click', handleClickOutside)
})
</script>
