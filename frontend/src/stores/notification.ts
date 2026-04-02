import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
	type Notification,
	notificationAPI,
	type PaginatedNotifications,
} from '@/services/api/notification'
import { useAuthStore } from '@/stores/auth'
import { getUnreadFallbackCount } from '@/stores/notificationUnread'

// Debounce utility function that preserves return values for async functions
function debounce<T extends (...args: Parameters<T>) => void>(
	fn: T,
	delay: number,
): (...args: Parameters<T>) => Promise<void> {
	let timeoutId: ReturnType<typeof setTimeout> | null = null
	return (...args: Parameters<T>) => {
		return new Promise<void>((resolve) => {
			if (timeoutId) {
				clearTimeout(timeoutId)
			}
			timeoutId = setTimeout(async () => {
				try {
					await fn(...args)
				} finally {
					timeoutId = null
					resolve()
				}
			}, delay)
		})
	}
}

// WebSocket notification message type
export interface WebSocketNotification {
	id: number
	title: string
	message: string
	event_type: string
	event_id: number | null
	is_read: boolean
	created_at: string
}

export const useNotificationStore = defineStore('notification', () => {
	const notifications = ref<Notification[]>([])
	const dropdownNotifications = ref<Notification[]>([])
	const loading = ref(false)
	const dropdownLoading = ref(false)
	let latestFetchAbortController: AbortController | null = null
	let unreadCountFetchAbortController: AbortController | null = null
	let paginatedFetchAbortController: AbortController | null = null

	// Pagination state for the Notifications page
	const totalCount = ref(0)
	const totalPages = ref(0)
	const currentPage = ref(1)
	const hasMore = ref(false)
	const loadingMore = ref(false)
	const currentArchivedMode = ref(false)
	const pageLoaded = ref(false)
	const serverUnreadCount = ref(0)

	const sortNotifications = (items: Notification[]) =>
		[...items].sort(
			(a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
		)

	const upsertNotification = (items: Notification[], notification: Notification) => {
		const existingIndex = items.findIndex((item) => item.id === notification.id)
		if (existingIndex === -1) {
			return [notification, ...items]
		}

		const nextItems = [...items]
		nextItems[existingIndex] = { ...nextItems[existingIndex], ...notification }
		return nextItems
	}

	const updateNotificationById = (
		items: Notification[],
		id: number,
		updater: (notification: Notification) => Notification,
	) => items.map((notification) => (notification.id === id ? updater(notification) : notification))

	const removeNotificationById = (items: Notification[], id: number) =>
		items.filter((notification) => notification.id !== id)

	const findNotificationById = (id: number) =>
		dropdownNotifications.value.find((notification) => notification.id === id) ||
		notifications.value.find((notification) => notification.id === id)

	// Prefer server unread count; local list acts as a fallback.
	const unreadCount = computed(() =>
		getUnreadFallbackCount(
			dropdownNotifications.value,
			notifications.value,
			currentArchivedMode.value,
			serverUnreadCount.value,
		),
	)

	const sortedNotifications = computed(() => sortNotifications(notifications.value))
	const sortedDropdownNotifications = computed(() => sortNotifications(dropdownNotifications.value))

	const isAbortError = (err: unknown) => {
		return (
			(err instanceof DOMException && err.name === 'AbortError') ||
			(typeof err === 'object' &&
				err !== null &&
				('code' in err || 'name' in err) &&
				((err as { code?: string }).code === 'ERR_CANCELED' ||
					(err as { name?: string }).name === 'CanceledError'))
		)
	}

	/**
	 * Add a new notification from WebSocket (real-time)
	 * This is called when a new notification is received via WebSocket
	 */
	function addNotification(notification: WebSocketNotification) {
		const newNotification: Notification = {
			id: notification.id,
			title: notification.title,
			message: notification.message,
			is_read: notification.is_read,
			created_at: notification.created_at,
			time_ago: 'Just now',
			recipient: useAuthStore().user?.id ?? 0,
			event: notification.event_id ?? null,
			event_type: notification.event_type,
			computed_event_type: notification.event_type,
		}

		const alreadyExists = !!findNotificationById(notification.id)
		dropdownNotifications.value = upsertNotification(dropdownNotifications.value, newNotification)

		if (pageLoaded.value && !currentArchivedMode.value && currentPage.value === 1) {
			notifications.value = upsertNotification(notifications.value, newNotification)
		}

		if (!alreadyExists) {
			if (!notification.is_read) {
				serverUnreadCount.value += 1
			}
			if (pageLoaded.value && !currentArchivedMode.value) {
				totalCount.value += 1
			}
		}
	}

	/**
	 * Fetch latest notifications for the dropdown menu (no pagination, limited to 10)
	 */
	async function fetchNotifications() {
		const authStore = useAuthStore()
		if (!authStore.isAuthenticated) {
			return
		}

		if (latestFetchAbortController) {
			latestFetchAbortController.abort()
		}
		const controller = new AbortController()
		latestFetchAbortController = controller

		dropdownLoading.value = true
		try {
			const notifData = await notificationAPI.getLatest(10, { signal: controller.signal })
			if (Array.isArray(notifData)) {
				dropdownNotifications.value = notifData
			}
		} catch (e) {
			if (isAbortError(e)) {
				return
			}
			console.error('Failed to fetch notifications', e)
		} finally {
			if (latestFetchAbortController === controller) {
				latestFetchAbortController = null
				dropdownLoading.value = false
			}
		}
	}

	/**
	 * Fetch unread notification count (dropdown badge path)
	 */
	async function fetchUnreadCount() {
		const authStore = useAuthStore()
		if (!authStore.isAuthenticated) {
			return null
		}

		if (unreadCountFetchAbortController) {
			unreadCountFetchAbortController.abort()
		}
		const controller = new AbortController()
		unreadCountFetchAbortController = controller

		try {
			const data = await notificationAPI.getUnreadCount({ signal: controller.signal })
			serverUnreadCount.value = Math.max(0, Number(data.unread_count) || 0)
			return data.unread_count
		} catch (e) {
			if (isAbortError(e)) {
				return null
			}
			console.error('Failed to fetch unread count', e)
			return null
		} finally {
			if (unreadCountFetchAbortController === controller) {
				unreadCountFetchAbortController = null
			}
		}
	}

	/**
	 * Fetch paginated notifications for the Notifications page
	 * @param page - Page number to fetch
	 * @param limit - Number of items per page
	 * @param append - If true, append to existing notifications (for infinite scroll)
	 */
	async function fetchPaginatedNotifications(
		page: number = 1,
		limit: number = 20,
		append: boolean = false,
		archivedOnly: boolean = false,
	) {
		const authStore = useAuthStore()
		if (!authStore.isAuthenticated) {
			return
		}

		if (paginatedFetchAbortController) {
			paginatedFetchAbortController.abort()
		}
		const controller = new AbortController()
		paginatedFetchAbortController = controller

		if (append) {
			loadingMore.value = true
		} else {
			loading.value = true
		}

		try {
			const data = (await notificationAPI.list(
				{
					page,
					limit,
					archived_only: archivedOnly || undefined,
				},
				{ signal: controller.signal },
			)) as PaginatedNotifications

			// Track mode for infinite scroll loadMore
			currentArchivedMode.value = archivedOnly

			if ('results' in data) {
				if (append) {
					// Deduplicate when appending
					const existingIds = new Set(notifications.value.map((n) => n.id))
					const newNotifications = data.results.filter((n) => !existingIds.has(n.id))
					notifications.value = [...notifications.value, ...newNotifications]
				} else {
					notifications.value = data.results
				}
				totalCount.value = data.count
				totalPages.value = data.total_pages
				currentPage.value = data.current_page
				hasMore.value = data.next !== null
				pageLoaded.value = true
			}
		} catch (e) {
			if (isAbortError(e)) {
				return
			}
			console.error('Failed to fetch paginated notifications', e)
		} finally {
			if (paginatedFetchAbortController === controller) {
				paginatedFetchAbortController = null
				loading.value = false
				loadingMore.value = false
			}
		}
	}

	/**
	 * Load more notifications (for infinite scroll) - debounced
	 */
	const loadMore = debounce(async () => {
		if (loadingMore.value || !hasMore.value) {
			return
		}

		const nextPage = currentPage.value + 1
		await fetchPaginatedNotifications(nextPage, 20, true, currentArchivedMode.value)
	}, 300) // 300ms debounce

	/**
	 * Reset pagination state
	 */
	function resetPagination() {
		if (paginatedFetchAbortController) {
			paginatedFetchAbortController.abort()
			paginatedFetchAbortController = null
		}
		currentPage.value = 1
		totalCount.value = 0
		totalPages.value = 0
		hasMore.value = false
		currentArchivedMode.value = false
		pageLoaded.value = false
		notifications.value = []
	}

	async function markAsRead(id: number) {
		try {
			await notificationAPI.markRead(id)
			const target = findNotificationById(id)
			if (target && !target.is_read) {
				dropdownNotifications.value = updateNotificationById(dropdownNotifications.value, id, (notification) => ({
					...notification,
					is_read: true,
				}))
				notifications.value = updateNotificationById(notifications.value, id, (notification) => ({
					...notification,
					is_read: true,
				}))
				serverUnreadCount.value = Math.max(0, serverUnreadCount.value - 1)
			}
		} catch (e) {
			console.error('Failed to mark as read', e)
		}
	}

	async function markAllAsRead() {
		try {
			const response = await notificationAPI.markAllRead()
			dropdownNotifications.value = dropdownNotifications.value.map((notification) => ({
				...notification,
				is_read: true,
			}))
			notifications.value.forEach((n) => {
				n.is_read = true
			})
			serverUnreadCount.value = Math.max(0, serverUnreadCount.value - response.count)
			return response.count
		} catch (e) {
			console.error('Failed to mark all as read', e)
			return 0
		}
	}

	async function archiveNotification(id: number) {
		try {
			const target = findNotificationById(id)
			const wasUnread = !!target && !target.is_read
			await notificationAPI.archiveNotification(id)
			if (wasUnread) {
				serverUnreadCount.value = Math.max(0, serverUnreadCount.value - 1)
			}
			dropdownNotifications.value = removeNotificationById(dropdownNotifications.value, id)
			notifications.value = notifications.value.filter((n) => n.id !== id)
			if (pageLoaded.value && !currentArchivedMode.value) {
				totalCount.value = Math.max(0, totalCount.value - 1)
			}
			return true
		} catch (e) {
			console.error('Failed to archive notification', e)
			return false
		}
	}

	async function unarchiveNotification(id: number) {
		try {
			await notificationAPI.unarchiveNotification(id)
			notifications.value = notifications.value.filter((n) => n.id !== id)
			if (pageLoaded.value && currentArchivedMode.value) {
				totalCount.value = Math.max(0, totalCount.value - 1)
			}
			return true
		} catch (e) {
			console.error('Failed to unarchive notification', e)
			return false
		}
	}

	async function deleteNotification(id: number) {
		try {
			const target = findNotificationById(id)
			const wasUnread = !!target && !target.is_read
			const pageHasTarget = notifications.value.some((notification) => notification.id === id)
			await notificationAPI.deleteNotification(id)
			if (wasUnread) {
				serverUnreadCount.value = Math.max(0, serverUnreadCount.value - 1)
			}
			dropdownNotifications.value = removeNotificationById(dropdownNotifications.value, id)
			notifications.value = notifications.value.filter((n) => n.id !== id)
			if (pageLoaded.value && (pageHasTarget || !currentArchivedMode.value)) {
				totalCount.value = Math.max(0, totalCount.value - 1)
			}
			return true
		} catch (e) {
			console.error('Failed to delete notification', e)
			return false
		}
	}

	/**
	 * Initialize notifications - fetch initial data
	 * WebSocket will handle real-time updates
	 */
	function initialize() {
		const authStore = useAuthStore()
		if (!authStore.isAuthenticated) {
			return
		}

		// Fetch initial notifications
		fetchNotifications()
		void fetchUnreadCount()
	}

	/**
	 * Abort all in-flight requests and clean up controllers.
	 * Call from onUnmounted or app teardown to prevent leaks.
	 */
	function disposeControllers() {
		latestFetchAbortController?.abort()
		latestFetchAbortController = null
		unreadCountFetchAbortController?.abort()
		unreadCountFetchAbortController = null
		paginatedFetchAbortController?.abort()
		paginatedFetchAbortController = null
	}

	/**
	 * Clear all notifications (on logout)
	 */
	function clearNotifications() {
		disposeControllers()
		notifications.value = []
		dropdownNotifications.value = []
		dropdownLoading.value = false
		serverUnreadCount.value = 0
		totalCount.value = 0
		totalPages.value = 0
		currentPage.value = 1
		hasMore.value = false
		currentArchivedMode.value = false
		pageLoaded.value = false
	}

	return {
		notifications,
		dropdownNotifications,
		unreadCount,
		loading,
		dropdownLoading,
		loadingMore,
		sortedNotifications,
		sortedDropdownNotifications,
		totalCount,
		totalPages,
		currentPage,
		hasMore,
		addNotification,
		fetchNotifications,
		fetchUnreadCount,
		fetchPaginatedNotifications,
		loadMore,
		resetPagination,
		markAsRead,
		markAllAsRead,
		archiveNotification,
		unarchiveNotification,
		deleteNotification,
		initialize,
		clearNotifications,
		disposeControllers,
	}
})
