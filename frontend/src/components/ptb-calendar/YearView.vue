<template>
    <div class="space-y-4">
        <!-- Months Grid - 3 months per row for a larger view -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="month in 12" :key="month"
                class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-visible">
                <!-- Month Header -->
                <div @click="$emit('month-click', month - 1)"
                    class="p-3 bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition rounded-t-xl">
                    <h3 class="text-sm font-bold text-gray-900 dark:text-white text-center">
                        {{ monthNames[month - 1] }}
                    </h3>
                </div>

                <!-- Mini Calendar -->
                <div class="p-3">
                    <!-- Day Headers (with week number column) -->
                    <div class="grid grid-cols-[20px_repeat(7,1fr)] mb-1">
                        <div class="text-center text-[9px] font-medium text-gray-400 dark:text-gray-500 py-1">W</div>
                        <div v-for="day in weekDays" :key="day"
                            class="text-center text-xs font-medium text-gray-500 dark:text-gray-500 py-1">
                            {{ day }}
                        </div>
                    </div>

                    <!-- Calendar Grid with Week Numbers -->
					<div v-for="(week, weekIndex) in getMonthWeeks(month - 1)" :key="weekIndex"
						class="grid grid-cols-[20px_repeat(7,1fr)] gap-0.5">
                        <!-- Week Number - Clickable -->
                        <div @click="$emit('week-click', new Date(week.days[0]?.fullDate || ''))"
                            :class="[
                                'text-center text-[9px] py-1.5 cursor-pointer rounded transition',
                                week.isCurrentWeek
                                    ? 'bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 font-bold hover:bg-brand-200 dark:hover:bg-brand-900/60'
                                    : 'text-gray-400 dark:text-gray-500 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900/20'
                            ]"
                            title="Click to view this week">
                            {{ week.weekNumber }}
                        </div>
                        <!-- Days -->
                        <div v-for="(day, dayIndex) in week.days" :key="dayIndex"
                            @click="day.isCurrentMonth && $emit('date-click', day.fullDate)"
                            @mousedown="handleMouseDown($event, day)"
                            @mouseenter="handleMouseEnter(day)"
                            @mouseup="handleMouseUp()"
                            class="group relative"
                            >
                            <div :class="[
                                'text-center text-sm py-1.5 rounded relative cursor-pointer hover:ring-2 hover:ring-brand-400 transition select-none',
                                day.isCurrentMonth
                                    ? 'text-gray-700 dark:text-gray-300'
                                    : 'text-gray-300 dark:text-gray-600 cursor-default hover:ring-0',
                                day.isToday && 'bg-brand-600 text-white font-bold',
                                day.hasHoliday && !day.isToday && 'holiday-day font-medium',
								day.hasLeave && !day.isToday && !day.hasHoliday && 'my-px bg-blue-100 dark:bg-blue-900/40',
                                isInSelection(day) && 'bg-brand-100 dark:bg-brand-900/40 ring-2 ring-brand-400'
                            ]" :style="day.hasHoliday && !day.isToday ? { backgroundColor: holidayColor + '60' } : {}">
                                {{ day.date }}
								<span v-if="day.leaveCount > 0" class="absolute bottom-0.5 left-1/2 flex -translate-x-1/2 items-center gap-0.5">
									<span v-for="index in day.leaveCount" :key="`${day.fullDate}-${index}`" :class="[
										'w-1 h-1 rounded-full',
										day.isToday ? 'bg-white/95' : 'bg-blue-500',
									]"></span>
								</span>
                            </div>
                            <!-- Tooltip on hover -->
                            <div v-if="day.isCurrentMonth && (day.hasHoliday || day.hasLeave)"
                                class="pointer-events-none absolute left-1/2 -translate-x-1/2 top-full mt-1 z-50 hidden group-hover:block w-max max-w-[200px]">
                                <div class="bg-gray-900 dark:bg-gray-700 text-white text-[10px] leading-snug rounded-lg px-2.5 py-1.5 shadow-lg">
                                    <div class="absolute left-1/2 -translate-x-1/2 bottom-full w-0 h-0 border-x-4 border-x-transparent border-b-4 border-b-gray-900 dark:border-b-gray-700"></div>
                                    <div v-for="h in getDayHolidays(day)" :key="'th-' + h.id" class="flex items-center gap-1 mb-0.5">
                                        <span class="w-1.5 h-1.5 rounded-full shrink-0" :style="{ backgroundColor: h.color || holidayColor }"></span>
                                        <span>{{ h.title }}</span>
                                    </div>
									<div v-for="l in getDayLeaves(day)" :key="'tl-' + l.id" class="space-y-0.5 last:mb-0 mb-1">
										<div class="flex items-center gap-1 font-semibold">
                                            <span class="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0"></span>
                                            <span>{{ l.employee_name }}</span>
                                        </div>
										<div class="pl-3 text-gray-300">{{ t('calendar.agent') }} <span class="font-normal">{{ getAgentDisplayShort(l) }}</span></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tabbed Holidays/Leaves Section - Always shown -->
                <div class="border-t border-gray-200 dark:border-gray-700">
                    <!-- Tabs -->
                    <div class="flex border-b border-gray-200 dark:border-gray-700">
						<button @click="monthTabs[month - 1] = 'leaves'" :class="[
                            'flex-1 px-2 py-1.5 text-[10px] font-medium transition flex items-center justify-center gap-1',
							monthTabs[month - 1] === 'leaves'
								? 'bg-gray-50 dark:bg-gray-900/50 text-gray-900 dark:text-white border-b-2 border-blue-500'
                                : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                        ]">
							<span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
							{{ t('calendar.leavesCount', { count: getMonthLeaveSummaries(month - 1).length }) }}
                        </button>
						<button @click="monthTabs[month - 1] = 'holidays'" :class="[
                            'flex-1 px-2 py-1.5 text-[10px] font-medium transition flex items-center justify-center gap-1',
							monthTabs[month - 1] === 'holidays'
								? 'bg-gray-50 dark:bg-gray-900/50 text-gray-900 dark:text-white border-b-2 border-brand-500'
                                : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                        ]">
							<span class="w-1.5 h-1.5 rounded-full" :style="{ backgroundColor: holidayColor }"></span>
							{{ t('calendar.holidaysCount', { count: getMonthHolidays(month - 1).length }) }}
                        </button>
                    </div>

                    <!-- Holidays Content -->
                    <div v-if="monthTabs[month - 1] === 'holidays' && getMonthHolidays(month - 1).length > 0"
                        class="p-2 bg-gray-50/50 dark:bg-gray-900/30 h-36 overflow-y-auto">
                        <div v-for="holiday in getMonthHolidays(month - 1)" :key="holiday.id"
                            @click.stop="$emit('holiday-click', holiday)"
                            class="text-xs py-1 px-2 mb-1 rounded cursor-pointer hover:opacity-80 transition truncate"
                            :style="{
                                backgroundColor: holiday.color || holidayColor,
                                color: getContrastColor(holiday.color || holidayColor)
                            }">
                            {{ formatDay(holiday.date) }} - {{ holiday.title }}
                        </div>
                    </div>
                    <div v-if="monthTabs[month - 1] === 'holidays' && getMonthHolidays(month - 1).length === 0"
                        class="p-2 h-36 flex items-center justify-center text-[10px] text-gray-400">{{ t('calendar.noHolidaysThisMonth') }}</div>

                    <!-- Leaves Content -->
					<div v-if="monthTabs[month - 1] === 'leaves' && getMonthLeaveSummaries(month - 1).length > 0"
                        class="h-36 overflow-y-auto bg-blue-50/50 p-3 dark:bg-blue-900/10">
						<div v-for="summary in getMonthLeaveSummaries(month - 1)" :key="summary.employeeId"
							@click.stop="$emit('leave-click', summary.representativeLeave)"
							class="mb-2 flex items-start gap-3.5 rounded-xl bg-blue-100 px-3 py-2.5 text-blue-700 transition last:mb-0 hover:bg-blue-200 dark:bg-blue-900/40 dark:text-blue-300 dark:hover:bg-blue-900/60">
							<div class="w-11 text-center flex-shrink-0 pt-0.5">
								<div class="text-lg font-bold text-blue-700 dark:text-blue-300">{{ summary.leaveDays }}</div>
								<div class="text-xs font-bold text-blue-600 dark:text-blue-400">{{ t('calendar.daysLabel') }}</div>
							</div>
							<div class="flex-1 min-w-0">
								<div class="text-sm text-gray-900 dark:text-white">
									<span class="font-bold">{{ summary.employeeName }}</span>
									<span v-if="summary.employeeEmpId" class="ml-1 text-sm font-normal text-gray-500 dark:text-gray-400">({{ summary.employeeEmpId }})</span>
								</div>
								<div class="mt-1 text-xs text-blue-500 dark:text-blue-400 truncate">
									{{ formatSummaryDates(summary.dates) }}
								</div>
								<div class="mt-1 text-xs text-blue-600 dark:text-blue-400 truncate">
									{{ t('calendar.agent') }} <span class="font-bold">{{ summary.agentDisplay }}</span>
								</div>
							</div>
						</div>
                    </div>
					<div v-if="monthTabs[month - 1] === 'leaves' && getMonthLeaveSummaries(month - 1).length === 0"
                        class="p-2 h-36 flex items-center justify-center text-[10px] text-gray-400">{{ t('calendar.noLeavesThisMonth') }}</div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { EmployeeLeave, Holiday } from '@/services/api/holiday'
import {
	formatLeaveSummaryDates,
	getLeaveAgentDisplay,
	getUniqueLeaveEmployeeCountByDate,
	LEAVE_AGENT_FALLBACK,
	summarizeLeavesByEmployee,
} from './leaveSummary'

interface Props {
	year: number
	holidays: Holiday[]
	leaves: EmployeeLeave[]
	holidayColor?: string
}

const props = withDefaults(defineProps<Props>(), {
	holidayColor: '#FFB6C1',
})

const { t } = useI18n()

const emit = defineEmits<{
	(e: 'month-click', month: number): void
	(e: 'holiday-click', holiday: Holiday): void
	(e: 'leave-click', leave: EmployeeLeave): void
	(e: 'date-click', date: string): void
	(e: 'date-range-select', dates: string[]): void
	(e: 'week-click', startDate: Date): void
}>()

// Date range selection state
const isSelecting = ref(false)
const selectionStart = ref<string | null>(null)
const selectionEnd = ref<string | null>(null)

const YEAR_TAB_STORAGE_KEY = 'ptb-calendar-year-tabs-v2'

// Tab state for each month — restore from localStorage or default to 'leaves'
const loadSavedTabs = (): Record<number, 'holidays' | 'leaves'> => {
	const defaults: Record<number, 'holidays' | 'leaves'> = {
		0: 'leaves',
		1: 'leaves',
		2: 'leaves',
		3: 'leaves',
		4: 'leaves',
		5: 'leaves',
		6: 'leaves',
		7: 'leaves',
		8: 'leaves',
		9: 'leaves',
		10: 'leaves',
		11: 'leaves',
	}
	try {
		const saved = localStorage.getItem(YEAR_TAB_STORAGE_KEY)
		if (saved) {
			const parsed = JSON.parse(saved) as Record<string, string>
			for (const key of Object.keys(parsed)) {
				const idx = Number(key)
				if (idx >= 0 && idx <= 11 && (parsed[key] === 'holidays' || parsed[key] === 'leaves')) {
					defaults[idx] = parsed[key] as 'holidays' | 'leaves'
				}
			}
		}
	} catch {
		/* ignore */
	}
	return defaults
}
const monthTabs = reactive<Record<number, 'holidays' | 'leaves'>>(loadSavedTabs())

// Persist tab state to localStorage whenever it changes
watch(
	() => ({ ...monthTabs }),
	(tabs) => {
		localStorage.setItem(YEAR_TAB_STORAGE_KEY, JSON.stringify(tabs))
	},
	{ deep: true },
)

const monthNames = computed(() => [
	t('calendar.january'),
	t('calendar.february'),
	t('calendar.march'),
	t('calendar.april'),
	t('calendar.may'),
	t('calendar.june'),
	t('calendar.july'),
	t('calendar.august'),
	t('calendar.september'),
	t('calendar.october'),
	t('calendar.november'),
	t('calendar.december'),
])
const monthNamesShort = computed(() => [
	t('calendar.janShort'),
	t('calendar.febShort'),
	t('calendar.marShort'),
	t('calendar.aprShort'),
	t('calendar.mayShort'),
	t('calendar.junShort'),
	t('calendar.julShort'),
	t('calendar.augShort'),
	t('calendar.sepShort'),
	t('calendar.octShort'),
	t('calendar.novShort'),
	t('calendar.decShort'),
])
const dateWeekdayLabels = computed(() => [
	t('calendar.daySun'),
	t('calendar.dayMon'),
	t('calendar.dayTue'),
	t('calendar.dayWed'),
	t('calendar.dayThu'),
	t('calendar.dayFri'),
	t('calendar.daySat'),
])
const weekDays = computed(() => [
	t('calendar.dayM'),
	t('calendar.dayT'),
	t('calendar.dayW'),
	t('calendar.dayTh'),
	t('calendar.dayF'),
	t('calendar.dayS'),
	t('calendar.daySu'),
])

interface MiniCalendarDay {
	date: number
	fullDate: string
	isCurrentMonth: boolean
	isToday: boolean
	hasHoliday: boolean
	hasLeave: boolean
	leaveCount: number
}

interface CalendarWeek {
	weekNumber: number
	days: MiniCalendarDay[]
	isCurrentWeek: boolean
}

// Format date string to local date (fixes timezone issue)
const formatDateStr = (date: Date): string => {
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

// Get today's date string correctly in local time
const getTodayStr = (): string => {
	const today = new Date()
	return formatDateStr(today)
}

// Get ISO week number
const getWeekNumber = (date: Date): number => {
	const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
	const dayNum = d.getUTCDay() || 7
	d.setUTCDate(d.getUTCDate() + 4 - dayNum)
	const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
	return Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
}

// Get current week number
const currentWeekNumber = computed(() => {
	return getWeekNumber(new Date())
})

const getMonthWeeks = (month: number): CalendarWeek[] => {
	const weeks: CalendarWeek[] = []
	const todayStr = getTodayStr()

	const firstDay = new Date(props.year, month, 1)
	const lastDay = new Date(props.year, month + 1, 0)

	let startDayOfWeek = firstDay.getDay()
	startDayOfWeek = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1

	const allDays: MiniCalendarDay[] = []

	// Previous month days
	const prevMonthLastDay = new Date(props.year, month, 0)
	for (let i = startDayOfWeek - 1; i >= 0; i--) {
		const date = prevMonthLastDay.getDate() - i
		const fullDate = formatDateStr(new Date(props.year, month - 1, date))
		allDays.push({
			date,
			fullDate,
			isCurrentMonth: false,
			isToday: fullDate === todayStr,
			hasHoliday: props.holidays.some((h) => h.date === fullDate),
			hasLeave: props.leaves.some((l) => l.date === fullDate),
			leaveCount: getUniqueLeaveEmployeeCountByDate(props.leaves, fullDate),
		})
	}

	// Current month days
	for (let i = 1; i <= lastDay.getDate(); i++) {
		const fullDate = formatDateStr(new Date(props.year, month, i))
		allDays.push({
			date: i,
			fullDate,
			isCurrentMonth: true,
			isToday: fullDate === todayStr,
			hasHoliday: props.holidays.some((h) => h.date === fullDate),
			hasLeave: props.leaves.some((l) => l.date === fullDate),
			leaveCount: getUniqueLeaveEmployeeCountByDate(props.leaves, fullDate),
		})
	}

	// Next month days to complete grid (6 rows)
	const remainingDays = 42 - allDays.length
	for (let i = 1; i <= remainingDays; i++) {
		const fullDate = formatDateStr(new Date(props.year, month + 1, i))
		allDays.push({
			date: i,
			fullDate,
			isCurrentMonth: false,
			isToday: fullDate === todayStr,
			hasHoliday: props.holidays.some((h) => h.date === fullDate),
			hasLeave: props.leaves.some((l) => l.date === fullDate),
			leaveCount: getUniqueLeaveEmployeeCountByDate(props.leaves, fullDate),
		})
	}

	// Group into weeks with week numbers
	for (let i = 0; i < allDays.length; i += 7) {
		const weekDays = allDays.slice(i, i + 7)
		// Get week number from first current month day in the week, or first day
		const firstValidDay = weekDays.find((d) => d.isCurrentMonth) || weekDays[0]
		const weekNumber = getWeekNumber(new Date(firstValidDay?.fullDate || ''))

		weeks.push({
			weekNumber,
			days: weekDays,
			isCurrentWeek: weekNumber === currentWeekNumber.value,
		})
	}

	return weeks
}

const getMonthHolidays = (month: number): Holiday[] => {
	return props.holidays
		.filter((h) => {
			const holidayDate = new Date(h.date)
			return holidayDate.getMonth() === month && holidayDate.getFullYear() === props.year
		})
		.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
}

const getMonthLeaves = (month: number): EmployeeLeave[] => {
	return props.leaves
		.filter((l) => {
			const leaveDate = new Date(l.date)
			return leaveDate.getMonth() === month && leaveDate.getFullYear() === props.year
		})
		.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
}

const getMonthLeaveSummaries = (month: number) =>
	summarizeLeavesByEmployee(getMonthLeaves(month), LEAVE_AGENT_FALLBACK)

const formatDay = (dateStr: string): string => {
	const date = new Date(dateStr)
	return date.getDate().toString()
}

// Short agent display (names only, no IDs) — for tooltip and compact leaves tab
const getAgentDisplayShort = (leave: EmployeeLeave): string =>
	getLeaveAgentDisplay(leave, LEAVE_AGENT_FALLBACK)

const formatSummaryDates = (dates: string[]): string => {
	return formatLeaveSummaryDates(dates, dateWeekdayLabels.value, 4)
}

// Get holidays for a specific day (for tooltips)
const getDayHolidays = (day: MiniCalendarDay): Holiday[] => {
	return props.holidays.filter((h) => h.date === day.fullDate)
}

// Get leaves for a specific day (for tooltips)
const getDayLeaves = (day: MiniCalendarDay): EmployeeLeave[] => {
	return props.leaves.filter((l) => l.date === day.fullDate)
}

const getContrastColor = (hexColor: string): string => {
	const hex = hexColor.replace('#', '')
	const r = parseInt(hex.substr(0, 2), 16)
	const g = parseInt(hex.substr(2, 2), 16)
	const b = parseInt(hex.substr(4, 2), 16)
	const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
	return luminance > 0.5 ? '#1f2937' : '#ffffff'
}

// Format date string to local date (fixes timezone issue)
const formatDateStrForRange = (date: Date): string => {
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

// Date range selection functions
const handleMouseDown = (event: MouseEvent, day: MiniCalendarDay) => {
	// Start selection on left mouse button only, and only for current month days
	if (event.button !== 0 || !day.isCurrentMonth) return

	isSelecting.value = true
	selectionStart.value = day.fullDate
	selectionEnd.value = day.fullDate
}

const handleMouseEnter = (day: MiniCalendarDay) => {
	if (isSelecting.value && day.isCurrentMonth) {
		selectionEnd.value = day.fullDate
	}
}

const handleMouseUp = () => {
	if (isSelecting.value && selectionStart.value && selectionEnd.value) {
		const dates = getDateRange(selectionStart.value, selectionEnd.value)
		if (dates.length > 0) {
			emit('date-range-select', dates)
		}
	}

	isSelecting.value = false
	selectionStart.value = null
	selectionEnd.value = null
}

// Get all dates between start and end (inclusive)
const getDateRange = (start: string, end: string): string[] => {
	const startDate = new Date(start)
	const endDate = new Date(end)

	// Ensure start is before end
	const [from, to] = startDate <= endDate ? [startDate, endDate] : [endDate, startDate]

	const dates: string[] = []
	const current = new Date(from)

	while (current <= to) {
		dates.push(formatDateStrForRange(current))
		current.setDate(current.getDate() + 1)
	}

	return dates
}

// Check if a day is within the current selection
const isInSelection = (day: MiniCalendarDay): boolean => {
	if (!isSelecting.value || !selectionStart.value || !selectionEnd.value || !day.isCurrentMonth) {
		return false
	}

	const dayDate = new Date(day.fullDate)
	const startDate = new Date(selectionStart.value)
	const endDate = new Date(selectionEnd.value)

	const [from, to] = startDate <= endDate ? [startDate, endDate] : [endDate, startDate]

	return dayDate >= from && dayDate <= to
}

// Global mouseup listener to handle selection ending outside the calendar
const handleGlobalMouseUp = () => {
	if (isSelecting.value && selectionStart.value && selectionEnd.value) {
		const dates = getDateRange(selectionStart.value, selectionEnd.value)
		if (dates.length > 0) {
			emit('date-range-select', dates)
		}
	}

	isSelecting.value = false
	selectionStart.value = null
	selectionEnd.value = null
}

onMounted(() => {
	document.addEventListener('mouseup', handleGlobalMouseUp)
})

onUnmounted(() => {
	document.removeEventListener('mouseup', handleGlobalMouseUp)
})
</script>
