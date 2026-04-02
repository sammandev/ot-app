import type { Notification } from '@/services/api/notification'

export const getUnreadFallbackCount = (
	dropdownNotifications: Notification[],
	pageNotifications: Notification[],
	currentArchivedMode: boolean,
	serverUnreadCount: number,
): number => {
	const unreadIds = new Set<number>()
	for (const notification of dropdownNotifications) {
		if (!notification.is_read && !notification.is_archived) unreadIds.add(notification.id)
	}
	for (const notification of pageNotifications) {
		if (!notification.is_read && !notification.is_archived && !currentArchivedMode) {
			unreadIds.add(notification.id)
		}
	}
	return Math.max(serverUnreadCount, unreadIds.size)
}
