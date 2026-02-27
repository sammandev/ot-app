import { type ComputedRef, computed, type Reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { OvertimeFormState } from '@/composables/overtime/useBreakScheduler'
import { type OvertimeLimitConfig, overtimeLimitAPI } from '@/services/api/overtime'
import type { useOvertimeStore } from '@/stores/overtime'

// ── Shared types ──────────────────────────────────────────────────

export interface RequestBreak {
	start_time?: string | null
	end_time?: string | null
}

export interface RawOvertimeResponse {
	id?: number | null
	project?: number | null
	project_id?: number | null
	status?: string | null
	request_date?: string | null
	created_at?: string | null
	is_holiday?: boolean
	has_break?: boolean
	break_start?: string | null
	break_end?: string | null
	total_hours?: number | string | null
	time_start?: string | null
	time_end?: string | null
	breaks?: RequestBreak[]
	break_hours?: number | string | null
	reason?: string | null
	detail?: string | null
}

// ── Helpers ───────────────────────────────────────────────────────

const parseMinutes = (timeStr?: string | null): number | null => {
	if (!timeStr) return null
	const parts = timeStr.split(':')
	if (parts.length < 2) return null
	const h = Number(parts[0])
	const m = Number(parts[1])
	if (Number.isNaN(h) || Number.isNaN(m)) return null
	return h * 60 + m
}

export const computeRequestHours = (req: RawOvertimeResponse): number => {
	// Prefer backend total_hours
	const rawTotal =
		typeof req.total_hours === 'string' ? Number.parseFloat(req.total_hours) : req.total_hours
	if (Number.isFinite(rawTotal) && rawTotal !== null && rawTotal !== undefined)
		return Number(rawTotal)

	// Fallback: derive from time fields
	const start = parseMinutes(req.time_start)
	const end = parseMinutes(req.time_end)
	if (start === null || end === null) return 0
	let duration = end - start
	if (duration <= 0) duration += 24 * 60

	// Deduct breaks if provided
	let breakMinutes = 0
	if (Array.isArray(req.breaks) && req.breaks.length > 0) {
		breakMinutes = req.breaks.reduce((sum: number, b: RequestBreak) => {
			const bs = parseMinutes(b.start_time)
			const be = parseMinutes(b.end_time)
			if (bs === null || be === null) return sum
			let span = be - bs
			if (span <= 0) span += 24 * 60
			return sum + span
		}, 0)
	} else if (req.break_hours) {
		breakMinutes = Number(req.break_hours) * 60
	}

	const netMinutes = Math.max(0, duration - breakMinutes)
	return Number((netMinutes / 60).toFixed(2))
}

// ── Composable ────────────────────────────────────────────────────

interface UseOvertimeStatsOptions {
	form: Reactive<OvertimeFormState>
	canViewStats: ComputedRef<boolean>
	isExcludedFromOTReports: ComputedRef<boolean>
	overtimeStore: ReturnType<typeof useOvertimeStore>
}

export function useOvertimeStats({
	form,
	canViewStats,
	isExcludedFromOTReports,
	overtimeStore,
}: UseOvertimeStatsOptions) {
	const { t } = useI18n()

	// Overtime limits (loaded from backend configuration)
	const overtimeLimits = ref<OvertimeLimitConfig | null>(null)
	const WEEKLY_LIMIT = computed(() => Number(overtimeLimits.value?.max_weekly_hours ?? 18))
	const MONTHLY_LIMIT = computed(() => Number(overtimeLimits.value?.max_monthly_hours ?? 72))
	const ADVISED_WEEKLY_LIMIT = computed(() =>
		Number(overtimeLimits.value?.advised_weekly_hours ?? 15),
	)
	const ADVISED_MONTHLY_LIMIT = computed(() =>
		Number(overtimeLimits.value?.advised_monthly_hours ?? 60),
	)

	/** Fetch active OT limit config from backend */
	async function loadLimits() {
		try {
			overtimeLimits.value = await overtimeLimitAPI.getActive()
		} catch (err) {
			console.warn('Failed to load overtime limits, using defaults:', err)
		}
	}

	// ── Period info ───────────────────────────────────────────────

	const periodInfo = computed(() => {
		const selectedDate = new Date(form.selectedDate)
		const today = new Date()
		today.setHours(0, 0, 0, 0)

		const isPastDate = selectedDate < today

		const monthStart = new Date(selectedDate)
		const monthEnd = new Date(selectedDate)

		if (isExcludedFromOTReports.value) {
			// 18th-17th cycle for excluded employees
			if (selectedDate.getDate() <= 17) {
				monthStart.setMonth(monthStart.getMonth() - 1, 18)
				monthEnd.setDate(17)
			} else {
				monthStart.setDate(18)
				monthEnd.setMonth(monthEnd.getMonth() + 1, 17)
			}
		} else {
			// 26th-25th cycle for regular employees
			if (selectedDate.getDate() <= 25) {
				monthStart.setMonth(monthStart.getMonth() - 1, 26)
				monthEnd.setDate(25)
			} else {
				monthStart.setDate(26)
				monthEnd.setMonth(monthEnd.getMonth() + 1, 25)
			}
		}

		const formatMonth = (date: Date) =>
			date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
		const periodText = `(${formatMonth(monthStart)} - ${formatMonth(monthEnd)})`

		return {
			isPastDate,
			periodText,
			isCurrentPeriod: monthStart <= today && today <= monthEnd,
		}
	})

	const overtimePeriod = computed(() => periodInfo.value.periodText)

	// ── Actual hours (populated by calculateEmployeeOvertime) ─────

	const actualWeeklyHours = ref(0)
	const actualMonthlyHours = ref(0)

	const weeklyAppliedHours = computed(() => (canViewStats.value ? actualWeeklyHours.value : 0))
	const monthlyAppliedHours = computed(() => (canViewStats.value ? actualMonthlyHours.value : 0))

	const weeklyRemainingHours = computed(() => {
		if (!canViewStats.value) return WEEKLY_LIMIT.value
		return Math.max(0, WEEKLY_LIMIT.value - weeklyAppliedHours.value)
	})

	const monthlyRemainingHours = computed(() => {
		if (!canViewStats.value) return MONTHLY_LIMIT.value
		return Math.max(0, MONTHLY_LIMIT.value - monthlyAppliedHours.value)
	})

	// ── Color computeds ───────────────────────────────────────────

	const weeklyStatusColor = computed(() => {
		if (!canViewStats.value) return 'text-gray-400 dark:text-gray-500'
		if (weeklyAppliedHours.value >= WEEKLY_LIMIT.value) return 'text-error-600 dark:text-error-400'
		if (weeklyAppliedHours.value >= ADVISED_WEEKLY_LIMIT.value)
			return 'text-warning-600 dark:text-warning-400'
		return 'text-gray-900 dark:text-white'
	})

	const monthlyStatusColor = computed(() => {
		if (!canViewStats.value) return 'text-gray-400 dark:text-gray-500'
		if (monthlyAppliedHours.value >= MONTHLY_LIMIT.value) return 'text-error-600 dark:text-error-400'
		if (monthlyAppliedHours.value >= ADVISED_MONTHLY_LIMIT.value)
			return 'text-warning-600 dark:text-warning-400'
		return 'text-gray-900 dark:text-white'
	})

	const weeklyRemainingColor = computed(() => {
		if (!canViewStats.value) return 'text-gray-400 dark:text-gray-500'
		if (weeklyRemainingHours.value <= 0) return 'text-error-600 dark:text-error-400'
		if (weeklyRemainingHours.value <= 3) return 'text-warning-600 dark:text-warning-400'
		return 'text-gray-900 dark:text-white'
	})

	const monthlyRemainingColor = computed(() => {
		if (!canViewStats.value) return 'text-gray-400 dark:text-gray-500'
		if (monthlyRemainingHours.value <= 0) return 'text-error-600 dark:text-error-400'
		if (monthlyRemainingHours.value <= 12) return 'text-warning-600 dark:text-warning-400'
		return 'text-gray-900 dark:text-white'
	})

	// ── Warning computeds ─────────────────────────────────────────

	const weeklyWarning = computed(() => {
		if (!canViewStats.value) return ''
		if (weeklyAppliedHours.value >= WEEKLY_LIMIT.value) {
			return t('otForm.messages.weeklyExceeded', {
				hours: (weeklyAppliedHours.value - WEEKLY_LIMIT.value).toFixed(2),
			})
		}
		if (weeklyAppliedHours.value >= ADVISED_WEEKLY_LIMIT.value) {
			return t('otForm.messages.weeklyLimitReached')
		}
		return ''
	})

	const monthlyWarning = computed(() => {
		if (!canViewStats.value) return ''
		if (monthlyAppliedHours.value >= MONTHLY_LIMIT.value) {
			return t('otForm.messages.monthlyExceeded', {
				hours: (monthlyAppliedHours.value - MONTHLY_LIMIT.value).toFixed(2),
			})
		}
		if (monthlyAppliedHours.value >= ADVISED_MONTHLY_LIMIT.value) {
			return t('otForm.messages.monthlyLimitReached')
		}
		return ''
	})

	const remainingWarning = computed(() => {
		if (!canViewStats.value) return ''
		if (weeklyRemainingHours.value <= 0 && monthlyRemainingHours.value <= 0)
			return t('otForm.messages.noRemainingAll')
		if (weeklyRemainingHours.value <= 0) return t('otForm.messages.noRemainingWeekly')
		if (monthlyRemainingHours.value <= 0) return t('otForm.messages.noRemainingMonthly')
		return ''
	})

	const weeklyWarningClass = computed(() =>
		weeklyAppliedHours.value >= WEEKLY_LIMIT.value
			? 'text-error-600 dark:text-error-400'
			: weeklyWarning.value
				? 'text-warning-600 dark:text-warning-400'
				: '',
	)

	const monthlyWarningClass = computed(() =>
		monthlyAppliedHours.value >= MONTHLY_LIMIT.value
			? 'text-error-600 dark:text-error-400'
			: monthlyWarning.value
				? 'text-warning-600 dark:text-warning-400'
				: '',
	)

	const remainingWarningClass = computed(() =>
		remainingWarning.value ? 'text-warning-600 dark:text-warning-400' : '',
	)

	// ── Calculate employee overtime stats ─────────────────────────

	async function calculateEmployeeOvertime(employeeId: string, date: string) {
		if (!employeeId) {
			actualWeeklyHours.value = 0
			actualMonthlyHours.value = 0
			return
		}

		try {
			const selectedDate = new Date(date)

			// Calculate monthly period: 26th of previous month to 25th of current month
			const currentMonthStart = new Date(selectedDate)
			const currentMonthEnd = new Date(selectedDate)

			if (selectedDate.getDate() >= 26) {
				currentMonthStart.setDate(26)
				currentMonthStart.setHours(0, 0, 0, 0)
				currentMonthEnd.setMonth(currentMonthEnd.getMonth() + 1, 25)
				currentMonthEnd.setHours(23, 59, 59, 999)
			} else {
				currentMonthStart.setMonth(currentMonthStart.getMonth() - 1, 26)
				currentMonthStart.setHours(0, 0, 0, 0)
				currentMonthEnd.setDate(25)
				currentMonthEnd.setHours(23, 59, 59, 999)
			}

			// Calculate week range (Monday to Sunday) based on selected date
			const dayOfWeek = selectedDate.getDay()
			const daysFromMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1

			const weekStart = new Date(selectedDate)
			weekStart.setDate(selectedDate.getDate() - daysFromMonday)
			weekStart.setHours(0, 0, 0, 0)

			const weekEnd = new Date(weekStart)
			weekEnd.setDate(weekStart.getDate() + 6)
			weekEnd.setHours(23, 59, 59, 999)

			// Fetch date range must cover both monthly period AND the full week
			const fetchStart = new Date(Math.min(currentMonthStart.getTime(), weekStart.getTime()))
			const fetchEnd = new Date(Math.max(currentMonthEnd.getTime(), weekEnd.getTime()))

			const formatYMD = (d: Date) => d.toISOString().slice(0, 10)
			const requests = await overtimeStore.fetchAllRequests({
				employee: Number(employeeId),
				start_date: formatYMD(fetchStart),
				end_date: formatYMD(fetchEnd),
			})

			// Calculate monthly hours (include pending/approved; exclude rejected)
			const monthlyRequests = requests.filter((req) => {
				const reqDate = new Date(req.request_date)
				return reqDate >= currentMonthStart && reqDate <= currentMonthEnd && req.status !== 'rejected'
			})

			actualMonthlyHours.value = monthlyRequests.reduce(
				(sum, req) => sum + computeRequestHours(req),
				0,
			)

			// Calculate weekly hours (include pending/approved; exclude rejected)
			const weeklyRequests = requests.filter((req) => {
				const reqDate = new Date(req.request_date)
				return reqDate >= weekStart && reqDate <= weekEnd && req.status !== 'rejected'
			})

			actualWeeklyHours.value = weeklyRequests.reduce((sum, req) => sum + computeRequestHours(req), 0)
		} catch (error) {
			console.error('Failed to calculate overtime:', error)
			actualWeeklyHours.value = 0
			actualMonthlyHours.value = 0
		}
	}

	return {
		// Limits
		overtimeLimits,
		WEEKLY_LIMIT,
		MONTHLY_LIMIT,
		loadLimits,
		// Period
		periodInfo,
		overtimePeriod,
		// Applied / remaining
		weeklyAppliedHours,
		monthlyAppliedHours,
		weeklyRemainingHours,
		monthlyRemainingHours,
		// Colors
		weeklyStatusColor,
		monthlyStatusColor,
		weeklyRemainingColor,
		monthlyRemainingColor,
		// Warnings
		weeklyWarning,
		monthlyWarning,
		remainingWarning,
		weeklyWarningClass,
		monthlyWarningClass,
		remainingWarningClass,
		// Action
		calculateEmployeeOvertime,
	}
}
