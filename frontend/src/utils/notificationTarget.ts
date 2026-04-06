import type { LocationQueryRaw, RouteLocationRaw } from 'vue-router'
import type { Notification } from '@/services/api/notification'

type NotificationTargetData = {
	route?: string
	query?: Record<string, string | number | boolean | null | undefined>
}

const buildQuery = (
	query?: Record<string, string | number | boolean | null | undefined>,
): LocationQueryRaw | undefined => {
	if (!query) return undefined

	const normalized = Object.fromEntries(
		Object.entries(query)
			.filter(([, value]) => value !== undefined && value !== null && value !== '')
			.map(([key, value]) => [key, String(value)]),
	)

	return Object.keys(normalized).length > 0 ? normalized : undefined
}

export const resolveNotificationRoute = (notification: Notification): RouteLocationRaw => {
	const targetData = notification.target_data as NotificationTargetData | undefined

	if (targetData?.route) {
		return {
			path: targetData.route,
			query: buildQuery(targetData.query),
		}
	}

	switch (notification.event_type) {
		case 'task':
		case 'task_mention':
			return {
				path: '/kanban',
				query: notification.event ? { taskId: String(notification.event) } : undefined,
			}
		case 'meeting':
		case 'calendar':
			return {
				path: '/calendar',
				query: notification.event ? { eventId: String(notification.event) } : undefined,
			}
		case 'holiday':
			return {
				path: '/ptb-calendar',
				query: notification.event ? { holidayId: String(notification.event) } : undefined,
			}
		case 'leave':
			return {
				path: '/ptb-calendar',
				query: notification.event ? { eventId: String(notification.event) } : undefined,
			}
		case 'purchase_request':
			return {
				path: '/purchasing/list',
				query: notification.event ? { requestId: String(notification.event) } : undefined,
			}
		case 'overtime_approved':
		case 'overtime_rejected':
		case 'overtime_request':
			return {
				path: '/ot/history',
				query: notification.event ? { requestId: String(notification.event) } : undefined,
			}
		case 'user_report':
			return { path: '/notifications' }
		default:
			return { path: '/notifications' }
	}
}
