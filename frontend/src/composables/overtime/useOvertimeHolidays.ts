import { computed, type Ref, ref, watch } from 'vue'
import type { FlatpickrInstance } from '@/composables/useFlatpickrScroll'
import { type Holiday, holidayAPI } from '@/services/api'

export function useOvertimeHolidays(flatpickrInstances: Ref<FlatpickrInstance[]>) {
	const holidays = ref<Holiday[]>([])

	/** O(1) lookup set for holiday dates (YYYY-MM-DD strings) */
	const holidayDateSet = computed(() => new Set(holidays.value.map((h) => h.date)))

	/** Map of holiday date → title for tooltip */
	const holidayTitleMap = computed(() => {
		const map = new Map<string, string>()
		for (const h of holidays.value) {
			map.set(h.date, h.title)
		}
		return map
	})

	/** Check if the selected date is a holiday from PTB Calendar */
	function isDateHoliday(dateStr: string) {
		return holidays.value.some((h) => h.date === dateStr)
	}

	/** Fetch holidays for a given year (defaults to current year) */
	async function fetchHolidays(year?: number) {
		const targetYear = year || new Date().getFullYear()
		try {
			holidays.value = await holidayAPI.list({ year: targetYear })
			// Force flatpickr to redraw so onDayCreate applies holiday markers
			for (const fp of flatpickrInstances.value) {
				fp.redraw?.()
			}
		} catch (error) {
			console.error('Failed to fetch holidays:', error)
		}
	}

	// Redraw the flatpickr date picker when holidays data changes so day markers update
	watch(holidayDateSet, () => {
		for (const fp of flatpickrInstances.value) {
			if (fp.redraw && fp.calendarContainer) {
				fp.redraw()
			}
		}
	})

	return {
		holidays,
		holidayDateSet,
		holidayTitleMap,
		isDateHoliday,
		fetchHolidays,
	}
}
