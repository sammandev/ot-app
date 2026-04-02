import { describe, expect, it } from 'vitest'

import type { Notification } from '@/services/api/notification'
import { getUnreadFallbackCount } from '@/stores/notificationUnread'

const makeNotification = (overrides: Partial<Notification>): Notification => ({
	id: overrides.id ?? 1,
	title: overrides.title ?? 'Notice',
	message: overrides.message ?? 'Message',
	is_read: overrides.is_read ?? false,
	is_archived: overrides.is_archived ?? false,
	created_at: overrides.created_at ?? '2026-04-01T00:00:00Z',
	time_ago: overrides.time_ago ?? 'now',
	recipient: overrides.recipient ?? 1,
	event: overrides.event ?? null,
	event_type: overrides.event_type,
	computed_event_type: overrides.computed_event_type,
	meeting_url: overrides.meeting_url ?? null,
})

describe('getUnreadFallbackCount', () => {
	it('ignores archived page notifications when archived mode is active', () => {
		const count = getUnreadFallbackCount(
			[makeNotification({ id: 1, is_read: false })],
			[makeNotification({ id: 2, is_read: false, is_archived: true })],
			true,
			0,
		)

		expect(count).toBe(1)
	})

	it('prefers the higher server unread count', () => {
		const count = getUnreadFallbackCount([], [], false, 4)

		expect(count).toBe(4)
	})
})
