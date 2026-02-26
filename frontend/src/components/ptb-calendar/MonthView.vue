<template>
    <div class="space-y-4">
        <!-- Calendar Grid -->
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <!-- Day Headers with Week Numbers -->
            <div class="grid grid-cols-[28px_repeat(7,1fr)] border-b border-gray-200 dark:border-gray-700">
                <!-- Week Number Header -->
                <div
                    class="p-1 text-center text-[9px] font-semibold text-gray-500 dark:text-gray-500 bg-gray-50 dark:bg-gray-900/50">
                    {{ t('calendar.wk') }}
                </div>
                <div v-for="day in weekDays" :key="day"
                    class="p-3 text-center text-sm font-semibold text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/50">
                    {{ day }}
                </div>
            </div>

            <!-- Calendar Rows (6 weeks) -->
            <div v-for="(week, weekIndex) in calendarWeeks" :key="weekIndex" class="relative">
                <div class="grid grid-cols-[28px_repeat(7,1fr)]">
                    <!-- Week Number - Clickable to navigate to Week view -->
                    <div @click="handleWeekClick(week)" :class="[
                        'p-1 flex items-center justify-center border-b border-r border-gray-200 dark:border-gray-700 cursor-pointer transition',
                        week.isCurrentWeek
                            ? 'bg-brand-100 dark:bg-brand-900/40 hover:bg-brand-200 dark:hover:bg-brand-900/60'
                            : 'bg-gray-50/50 dark:bg-gray-900/30 hover:bg-brand-50 dark:hover:bg-brand-900/20'
                    ]" title="Click to view this week">
                        <span :class="[
                            'text-[9px] font-medium',
                            week.isCurrentWeek
                                ? 'text-brand-700 dark:text-brand-300 font-bold'
                                : 'text-gray-400 dark:text-gray-500 hover:text-brand-600 dark:hover:text-brand-400'
                        ]">
                            {{ week.weekNumber }}
                        </span>
                    </div>

                    <!-- Day Cells -->
                    <div v-for="(day, dayIndex) in week.days" :key="dayIndex" @click="handleDayClick(day)"
                        @mousedown="handleMouseDown($event, day)" @mouseenter="handleMouseEnter(day)"
                        @mouseup="handleMouseUp()" @dragover.prevent="handleDragOver" @drop="handleDrop($event, day)"
                        :class="[
                            'min-h-[100px] p-2 border-b border-r border-gray-200 dark:border-gray-700 transition cursor-pointer select-none overflow-hidden',
                            day.isCurrentMonth
                                ? 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                                : 'bg-gray-50 dark:bg-gray-900/30',
                            day.isToday && 'ring-2 ring-inset ring-brand-500',
                            getDayHolidayStyle(day),
                            isInSelection(day) && 'bg-brand-100 dark:bg-brand-900/40 ring-2 ring-brand-400'
                        ]">
                        <!-- Date Number + Holiday Dots -->
                        <div class="flex items-start justify-between mb-1">
                            <span :class="[
                                'flex items-center justify-center w-7 h-7 rounded-full text-sm font-medium shrink-0',
                                day.isCurrentMonth ? 'text-gray-900 dark:text-white' : 'text-gray-400 dark:text-gray-600',
                                day.isToday && 'bg-brand-600 text-white font-bold'
                            ]">
                                {{ day.date }}
                            </span>
                            <!-- Holiday Indicator (dots in top-right corner) -->
                            <div v-if="getDayHolidays(day).length > 0" class="flex flex-wrap gap-0.5 justify-end pt-1">
                                <span v-for="holiday in getDayHolidays(day)" :key="'h-' + holiday.id"
                                    @click.stop="$emit('holiday-click', holiday)" @mousedown.stop @mouseup.stop
                                    class="w-2 h-2 rounded-full cursor-pointer hover:ring-2 ring-offset-1"
                                    :style="{ backgroundColor: holiday.color || holidayColor }" :title="holiday.title">
                                </span>
                            </div>
                        </div>

                        <!-- Leave entries for each day -->
                        <div v-for="leave in getDayLeaves(day)" :key="'l-' + leave.id"
                            @click.stop="$emit('leave-click', leave)" draggable="true" @mousedown.stop @mouseup.stop
                            @dragstart="handleDragStart($event, leave)"
                            class="text-xs p-1 mb-1 rounded cursor-move bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/60 transition min-w-0">
                            <div class="truncate font-semibold">{{ leave.employee_name }}</div>
                            <div v-if="getAgentDisplay(leave)"
                                class="text-[10px] text-blue-500 dark:text-blue-400 truncate font-medium">
                                {{ t('calendar.agent') }} {{ getAgentDisplay(leave) }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Events List Below Calendar -->
        <div :class="['grid grid-cols-1 gap-4', hasBothSections && 'md:grid-cols-2']">
            <!-- Holidays Section -->
            <div v-if="currentMonthHolidays.length > 0"
                class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: holidayColor }"></span>
                    {{ t('calendar.holidaysThisMonth', { count: currentMonthHolidays.length }) }}
                </h3>
                <div class="space-y-2 max-h-48 overflow-y-auto">
                    <div v-for="holiday in currentMonthHolidays" :key="holiday.id"
                        @click="$emit('holiday-click', holiday)"
                        class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition">
                        <div class="w-10 text-center">
                            <div class="text-lg font-bold text-gray-900 dark:text-white">{{ formatDay(holiday.date) }}
                            </div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ holiday.title }}
                            </div>
                            <div class="text-xs text-gray-500">{{ formatDayName(holiday.date) }}</div>
                        </div>
                        <span class="w-3 h-3 rounded-full flex-shrink-0"
                            :style="{ backgroundColor: holiday.color || holidayColor }"></span>
                    </div>
                </div>
            </div>

            <!-- Leaves Section -->
            <div v-if="currentMonthLeaves.length > 0"
                class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full bg-blue-500"></span>
                    {{ t('calendar.leavesThisMonth', { count: currentMonthLeaves.length }) }}
                </h3>
                <div class="space-y-2 max-h-48 overflow-y-auto">
                    <div v-for="leave in currentMonthLeaves" :key="leave.id" @click="$emit('leave-click', leave)"
                        class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition">
                        <div class="w-10 text-center flex-shrink-0">
                            <div class="text-lg font-bold text-gray-900 dark:text-white">{{ formatDay(leave.date) }}
                            </div>
                            <div class="text-xs text-gray-500">{{ formatDayNameShort(leave.date) }}</div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="text-sm font-medium text-gray-900 dark:text-white">
                                {{ leave.employee_name }}
                                <span v-if="leave.employee_emp_id"
                                    class="text-sm text-gray-500 dark:text-gray-400 font-normal ml-1">({{
                                    leave.employee_emp_id }})</span>
                            </div>
                            <div v-if="getAgentDisplayWithDetails(leave)"
                                class="text-xs text-blue-600 dark:text-blue-400 mt-0.5">
                                {{ t('calendar.agent') }} {{ getAgentDisplayWithDetails(leave) }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { EmployeeLeave, Holiday } from '@/services/api'

interface Props {
	year: number
	month: number
	holidays: Holiday[]
	leaves: EmployeeLeave[]
	holidayColor?: string
}

const props = withDefaults(defineProps<Props>(), {
	holidayColor: '#FFB6C1',
})

const emit = defineEmits<{
	(e: 'date-click', date: string): void
	(e: 'date-range-select', dates: string[]): void
	(e: 'holiday-click', holiday: Holiday): void
	(e: 'leave-click', leave: EmployeeLeave): void
	(e: 'leave-move', leaveId: number, newDate: string): void
	(e: 'week-click', startDate: Date): void
}>()

// Date range selection state
const isSelecting = ref(false)
const selectionStart = ref<string | null>(null)
const selectionEnd = ref<string | null>(null)

const { t } = useI18n()

const weekDays = computed(() => [
	t('calendar.dayMon'),
	t('calendar.dayTue'),
	t('calendar.dayWed'),
	t('calendar.dayThu'),
	t('calendar.dayFri'),
	t('calendar.daySat'),
	t('calendar.daySun'),
])
const dayNames = computed(() => [
	t('calendar.daySunFull'),
	t('calendar.dayMonFull'),
	t('calendar.dayTueFull'),
	t('calendar.dayWedFull'),
	t('calendar.dayThuFull'),
	t('calendar.dayFriFull'),
	t('calendar.daySatFull'),
])
const dayNamesShort = computed(() => [
	t('calendar.dayMon'),
	t('calendar.dayTue'),
	t('calendar.dayWed'),
	t('calendar.dayThu'),
	t('calendar.dayFri'),
	t('calendar.daySat'),
	t('calendar.daySun'),
])

interface CalendarDay {
	date: number
	fullDate: string
	isCurrentMonth: boolean
	isToday: boolean
}

interface CalendarWeek {
	weekNumber: number
	days: CalendarDay[]
	isCurrentWeek: boolean
}

// Get ISO week number
const getWeekNumber = (date: Date): number => {
	const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
	const dayNum = d.getUTCDay() || 7
	d.setUTCDate(d.getUTCDate() + 4 - dayNum)
	const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
	return Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
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

// Get current week number
const currentWeekNumber = computed(() => {
	return getWeekNumber(new Date())
})

const calendarWeeks = computed<CalendarWeek[]>(() => {
	const weeks: CalendarWeek[] = []
	const todayStr = getTodayStr()

	// First day of the month
	const firstDay = new Date(props.year, props.month, 1)
	// Last day of the month
	const lastDay = new Date(props.year, props.month + 1, 0)

	// Get day of week for first day (0 = Sunday, adjust for Monday start)
	let startDayOfWeek = firstDay.getDay()
	startDayOfWeek = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1 // Adjust for Monday start

	const allDays: CalendarDay[] = []

	// Add days from previous month
	const prevMonthLastDay = new Date(props.year, props.month, 0)
	for (let i = startDayOfWeek - 1; i >= 0; i--) {
		const dateNum = prevMonthLastDay.getDate() - i
		const dateObj = new Date(props.year, props.month - 1, dateNum)
		const fullDate = formatDateStr(dateObj)
		allDays.push({
			date: dateNum,
			fullDate,
			isCurrentMonth: false,
			isToday: fullDate === todayStr,
		})
	}

	// Add days of current month
	for (let i = 1; i <= lastDay.getDate(); i++) {
		const dateObj = new Date(props.year, props.month, i)
		const fullDate = formatDateStr(dateObj)
		allDays.push({
			date: i,
			fullDate,
			isCurrentMonth: true,
			isToday: fullDate === todayStr,
		})
	}

	// Add days from next month to complete the grid (6 rows x 7 days = 42)
	const remainingDays = 42 - allDays.length
	for (let i = 1; i <= remainingDays; i++) {
		const dateObj = new Date(props.year, props.month + 1, i)
		const fullDate = formatDateStr(dateObj)
		allDays.push({
			date: i,
			fullDate,
			isCurrentMonth: false,
			isToday: fullDate === todayStr,
		})
	}

	// Group into weeks
	for (let i = 0; i < allDays.length; i += 7) {
		const weekDaysSlice = allDays.slice(i, i + 7)
		// Get week number from the first day of this week
		const firstDayOfWeek = new Date(weekDaysSlice[0]?.fullDate || '')
		const weekNum = getWeekNumber(firstDayOfWeek)
		weeks.push({
			weekNumber: weekNum,
			days: weekDaysSlice,
			isCurrentWeek: weekNum === currentWeekNumber.value,
		})
	}

	return weeks
})

// Filter holidays/leaves for current month only
const currentMonthHolidays = computed(() => {
	return props.holidays
		.filter((h) => {
			const date = new Date(h.date)
			return date.getMonth() === props.month && date.getFullYear() === props.year
		})
		.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const currentMonthLeaves = computed(() => {
	return props.leaves
		.filter((l) => {
			const date = new Date(l.date)
			return date.getMonth() === props.month && date.getFullYear() === props.year
		})
		.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const getDayHolidays = (day: CalendarDay): Holiday[] => {
	return props.holidays.filter((h) => h.date === day.fullDate)
}

const getDayLeaves = (day: CalendarDay): EmployeeLeave[] => {
	return props.leaves.filter((l) => l.date === day.fullDate)
}

// Check if both summary sections have content (for grid layout)
const hasBothSections = computed(
	() => currentMonthHolidays.value.length > 0 && currentMonthLeaves.value.length > 0,
)

const getDayHolidayStyle = (day: CalendarDay): string => {
	const dayHolidays = getDayHolidays(day)
	if (dayHolidays.length > 0 && day.isCurrentMonth) {
		return 'holiday-bg'
	}
	return ''
}

const formatDay = (dateStr: string): string => {
	return new Date(dateStr).getDate().toString()
}

const formatDayName = (dateStr: string): string => {
	return dayNames.value[new Date(dateStr).getDay()] ?? ''
}

const formatDayNameShort = (dateStr: string): string => {
	return dayNamesShort.value[(new Date(dateStr).getDay() + 6) % 7] ?? ''
}

// Get agent display text for a leave (names only - for calendar cell)
const getAgentDisplay = (leave: EmployeeLeave): string => {
	const parts: string[] = []

	// Add agent details (from selected employees)
	if (leave.agent_details && leave.agent_details.length > 0) {
		parts.push(...leave.agent_details.map((a) => a.name))
	}

	// Add custom agent names
	if (leave.agent_names) {
		parts.push(leave.agent_names)
	}

	return parts.join(', ')
}

// Get agent display with full details (name, emp_id, dept_code) - for list section
const getAgentDisplayWithDetails = (leave: EmployeeLeave): string => {
	const parts: string[] = []

	// Add agent details with emp_id and dept_code
	if (leave.agent_details && leave.agent_details.length > 0) {
		parts.push(
			...leave.agent_details.map((a) => {
				let display = a.name
				if (a.emp_id) display += ` (${a.emp_id})`
				return display
			}),
		)
	}

	// Add custom agent names
	if (leave.agent_names) {
		parts.push(leave.agent_names)
	}

	return parts.join('; ')
}

// Multi-day leave span logic remove due to non-usage

const handleDayClick = (day: CalendarDay) => {
	// Only emit date-click if not in selection mode
	if (!isSelecting.value) {
		emit('date-click', day.fullDate)
	}
}

// Date range selection handlers
const handleMouseDown = (_event: MouseEvent, day: CalendarDay) => {
	// Only start selection if clicking on a current month day
	if (!day.isCurrentMonth) return
	isSelecting.value = true
	selectionStart.value = day.fullDate
	selectionEnd.value = day.fullDate
}

const handleMouseEnter = (day: CalendarDay) => {
	if (isSelecting.value && day.isCurrentMonth) {
		selectionEnd.value = day.fullDate
	}
}

const handleMouseUp = () => {
	if (isSelecting.value && selectionStart.value && selectionEnd.value) {
		// Generate array of dates in range
		const dates = getDateRange(selectionStart.value, selectionEnd.value)
		if (dates.length > 1) {
			// Emit date range selection for multiple dates
			emit('date-range-select', dates)
		} else if (dates.length === 1) {
			// Single date click
			emit('date-click', dates[0] ?? '')
		}
	}
	isSelecting.value = false
	selectionStart.value = null
	selectionEnd.value = null
}

// Global mouseup handler to cancel selection when mouse released outside
const handleGlobalMouseUp = () => {
	if (isSelecting.value && selectionStart.value && selectionEnd.value) {
		const dates = getDateRange(selectionStart.value, selectionEnd.value)
		if (dates.length > 1) {
			emit('date-range-select', dates)
		}
	}
	isSelecting.value = false
	selectionStart.value = null
	selectionEnd.value = null
}

// Check if a day is in the current selection
const isInSelection = (day: CalendarDay): boolean => {
	if (!isSelecting.value || !selectionStart.value || !selectionEnd.value) return false
	if (!day.isCurrentMonth) return false

	const start = new Date(selectionStart.value).getTime()
	const end = new Date(selectionEnd.value).getTime()
	const current = new Date(day.fullDate).getTime()

	const minDate = Math.min(start, end)
	const maxDate = Math.max(start, end)

	return current >= minDate && current <= maxDate
}

// Get all dates between start and end (inclusive)
const getDateRange = (startDate: string, endDate: string): string[] => {
	const start = new Date(startDate)
	const end = new Date(endDate)

	// Swap if start > end
	const minDate = start <= end ? start : end
	const maxDate = start <= end ? end : start

	const dates: string[] = []
	const current = new Date(minDate)

	while (current <= maxDate) {
		dates.push(formatDateStr(current))
		current.setDate(current.getDate() + 1)
	}

	return dates
}

// Setup and cleanup global mouseup listener
onMounted(() => {
	document.addEventListener('mouseup', handleGlobalMouseUp)
})

onUnmounted(() => {
	document.removeEventListener('mouseup', handleGlobalMouseUp)
})

const handleWeekClick = (week: CalendarWeek) => {
	// Get the first day of the week to pass to week view
	const firstDay = week.days[0]
	if (firstDay) {
		const startDate = new Date(firstDay.fullDate)
		emit('week-click', startDate)
	}
}

// Drag and drop for leaves
let draggedLeave: EmployeeLeave | null = null

const handleDragStart = (event: DragEvent, leave: EmployeeLeave) => {
	draggedLeave = leave
	if (event.dataTransfer) {
		event.dataTransfer.effectAllowed = 'move'
		event.dataTransfer.setData('text/plain', leave.id.toString())
	}
}

const handleDragOver = (event: DragEvent) => {
	if (event.dataTransfer) {
		event.dataTransfer.dropEffect = 'move'
	}
}

const handleDrop = (event: DragEvent, day: CalendarDay) => {
	event.preventDefault()
	if (draggedLeave && draggedLeave.date !== day.fullDate) {
		emit('leave-move', draggedLeave.id, day.fullDate)
	}
	draggedLeave = null
}
</script>

<style scoped>
.holiday-bg {
    background-color: v-bind('holidayColor + "20"') !important;
}
</style>
