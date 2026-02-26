export function calculateTimeDifference(start: string, end: string): number {
	if (!start || !end) return 0

	try {
		const [startHours, startMinutes] = start.split(':').map(Number)
		const [endHours, endMinutes] = end.split(':').map(Number)

		if (
			startHours === undefined ||
			startMinutes === undefined ||
			endHours === undefined ||
			endMinutes === undefined
		) {
			return 0
		}

		const startTotalMinutes = startHours * 60 + startMinutes
		let endTotalMinutes = endHours * 60 + endMinutes

		if (Number.isNaN(startTotalMinutes) || Number.isNaN(endTotalMinutes)) {
			return 0
		}

		// Handle crossing midnight
		if (endTotalMinutes < startTotalMinutes) {
			endTotalMinutes += 24 * 60
		}

		const diffMinutes = endTotalMinutes - startTotalMinutes
		return diffMinutes / 60
	} catch (error) {
		console.error('Error calculating time difference:', error)
		return 0
	}
}
