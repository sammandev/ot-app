import { computed, type Reactive } from 'vue'
import { calculateTimeDifference } from '@/utils/timeCalculations'

/** Shape of the overtime form reactive state */
export interface OvertimeFormState {
	selectedEmployee: string
	selectedProject: string
	selectedDate: string
	timeStart: string
	timeEnd: string
	isHoliday: boolean
	hasBreak: boolean
	breakStart: string
	breakEnd: string
	breakStart2: string
	breakEnd2: string
	breakStart3: string
	breakEnd3: string
	reason: string
	details: string
}

// ── Time utility helpers ──────────────────────────────────────────

export function parseTimeToDate(timeValue: string | Date): Date | null {
	if (!timeValue) return null
	if (timeValue instanceof Date) {
		const d = new Date()
		d.setHours(timeValue.getHours(), timeValue.getMinutes(), 0, 0)
		return d
	}
	const [h, m] = timeValue.split(':').map(Number)
	if (Number.isNaN(h) || Number.isNaN(m) || h === undefined || m === undefined) return null
	const d = new Date()
	d.setHours(h, m, 0, 0)
	return d
}

export function formatTime(dateObj: Date): string {
	const hh = String(dateObj.getHours()).padStart(2, '0')
	const mm = String(dateObj.getMinutes()).padStart(2, '0')
	return `${hh}:${mm}`
}

export function addHours(base: Date, hours: number): Date {
	return new Date(base.getTime() + hours * 60 * 60 * 1000)
}

export function isWeekend(dateStr: string): boolean {
	const d = new Date(dateStr)
	const day = d.getDay()
	return day === 0 || day === 6
}

// ── Composable ────────────────────────────────────────────────────

export function useBreakScheduler(form: Reactive<OvertimeFormState>) {
	const rawHours = computed(() => calculateTimeDifference(form.timeStart, form.timeEnd))

	const manualBreakHours = computed(() => {
		const first =
			form.breakStart && form.breakEnd ? calculateTimeDifference(form.breakStart, form.breakEnd) : 0
		const second =
			form.breakStart2 && form.breakEnd2
				? calculateTimeDifference(form.breakStart2, form.breakEnd2)
				: 0
		const third =
			form.breakStart3 && form.breakEnd3
				? calculateTimeDifference(form.breakStart3, form.breakEnd3)
				: 0
		return first + second + third
	})

	const autoBreakHours = computed(() => {
		if (!(form.isHoliday || isWeekend(form.selectedDate))) return 0
		if (rawHours.value > 4 && rawHours.value <= 5) return rawHours.value - 4
		if (rawHours.value > 9 && rawHours.value <= 9.5) return rawHours.value - 8
		return 0
	})

	const totalBreakHours = computed(
		() => (form.hasBreak ? manualBreakHours.value : 0) + autoBreakHours.value,
	)

	const totalHours = computed(() => {
		const raw = rawHours.value
		const breaks = totalBreakHours.value
		if (raw <= 0) return 0
		return Math.max(0, raw - breaks)
	})

	const breakCount = computed(
		() => [form.breakStart, form.breakStart2, form.breakStart3].filter(Boolean).length,
	)
	const showSecondBreak = computed(
		() => form.hasBreak && (breakCount.value >= 2 || rawHours.value >= 9),
	)
	const showThirdBreak = computed(
		() => form.hasBreak && (breakCount.value >= 3 || rawHours.value >= 13),
	)

	/** Automatically schedule up to 3 breaks every 4 hours of work */
	function scheduleBreaks() {
		const start = parseTimeToDate(form.timeStart)
		const rawEnd = parseTimeToDate(form.timeEnd)
		if (!start || !rawEnd) return

		let end = rawEnd
		if (end <= start) {
			end = addHours(end, 24)
		}

		const totalDuration = (end.getTime() - start.getTime()) / (60 * 60 * 1000)

		if (totalDuration <= 4) {
			form.hasBreak = false
			form.breakStart = ''
			form.breakEnd = ''
			form.breakStart2 = ''
			form.breakEnd2 = ''
			form.breakStart3 = ''
			form.breakEnd3 = ''
			return
		}

		form.hasBreak = true
		const breaks: { start: Date; end: Date }[] = []
		let workTime = 0
		let cursor = start

		// Schedule breaks every 4 hours of work
		while (workTime < totalDuration && breaks.length < 3) {
			const nextWorkSegment = Math.min(4, totalDuration - workTime)
			workTime += nextWorkSegment

			if (workTime >= 4 && workTime < totalDuration) {
				const breakStart = addHours(cursor, nextWorkSegment)
				const remainingTime = totalDuration - workTime
				const breakDuration = Math.min(1, remainingTime)
				const breakEnd = addHours(breakStart, breakDuration)

				breaks.push({ start: breakStart, end: breakEnd })
				cursor = addHours(cursor, nextWorkSegment + breakDuration)
			} else {
				break
			}
		}

		const [b1, b2, b3] = breaks
		form.breakStart = b1 ? formatTime(b1.start) : ''
		form.breakEnd = b1 ? formatTime(b1.end) : ''
		form.breakStart2 = b2 ? formatTime(b2.start) : ''
		form.breakEnd2 = b2 ? formatTime(b2.end) : ''
		form.breakStart3 = b3 ? formatTime(b3.start) : ''
		form.breakEnd3 = b3 ? formatTime(b3.end) : ''
	}

	return {
		rawHours,
		manualBreakHours,
		autoBreakHours,
		totalBreakHours,
		totalHours,
		breakCount,
		showSecondBreak,
		showThirdBreak,
		scheduleBreaks,
	}
}
