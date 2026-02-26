/**
 * Shared date/time formatting utilities.
 *
 * All helper functions automatically convert server timestamps (UTC / ISO 8601)
 * to the user's **local** browser timezone so that employees across different
 * countries always see times in their own time zone.
 */

/**
 * Return the user's current UTC offset label, e.g. "UTC+7", "UTC-5", "UTC+5:30".
 */
export function getUtcOffsetLabel(date?: Date): string {
	const d = date ?? new Date()
	const offsetMin = -d.getTimezoneOffset() // positive = east of UTC
	const sign = offsetMin >= 0 ? '+' : '-'
	const absMin = Math.abs(offsetMin)
	const hours = Math.floor(absMin / 60)
	const minutes = absMin % 60
	return minutes > 0
		? `UTC${sign}${hours}:${String(minutes).padStart(2, '0')}`
		: `UTC${sign}${hours}`
}

/**
 * Format an ISO date string into the full local datetime with timezone indicator.
 *
 * Example output: `Thu, 26 Feb 2026, 13:16:05 (UTC+7)`
 */
export function formatFullLocalDateTime(isoStr: string | undefined | null): string {
	if (!isoStr) return ''
	const d = new Date(isoStr)
	if (Number.isNaN(d.getTime())) return ''

	const weekday = d.toLocaleDateString('en-US', { weekday: 'short' }) // "Thu"
	const day = d.getDate() // 26
	const month = d.toLocaleDateString('en-US', { month: 'short' }) // "Feb"
	const year = d.getFullYear() // 2026
	const time = d.toLocaleTimeString('en-US', {
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit',
		hour12: false,
	}) // "13:16:05"

	return `${weekday}, ${day} ${month} ${year}, ${time} (${getUtcOffsetLabel(d)})`
}

/**
 * Format an ISO date string into a short local datetime (no seconds, no offset).
 *
 * Example output: `Feb 26, 2026, 13:16`
 */
export function formatLocalDateTime(isoStr: string | undefined | null): string {
	if (!isoStr) return ''
	const d = new Date(isoStr)
	if (Number.isNaN(d.getTime())) return ''

	return d.toLocaleString('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
		hour: 'numeric',
		minute: '2-digit',
	})
}

/**
 * Compute a relative "time ago" string from an ISO date string, purely on the
 * client. This removes the dependency on the server-computed `time_ago` value.
 *
 * Returns: `just now`, `5m ago`, `2h ago`, `3d ago`, or falls back to short date.
 */
export function timeAgo(isoStr: string | undefined | null): string {
	if (!isoStr) return ''
	const d = new Date(isoStr)
	if (Number.isNaN(d.getTime())) return ''

	const seconds = (Date.now() - d.getTime()) / 1000

	if (seconds < 60) return 'just now'
	if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
	if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
	if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`

	return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
