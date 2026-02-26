<template>
    <div class="space-y-4">
        <!-- Calendar Grid -->
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <!-- Day Headers -->
            <div class="grid grid-cols-7 border-b border-gray-200 dark:border-gray-700">
                <div v-for="(day, index) in weekDays" :key="index"
                    class="p-3 text-center border-r border-gray-200 dark:border-gray-700 last:border-r-0">
                    <div class="text-sm font-semibold text-gray-600 dark:text-gray-400">
                        {{ day.dayName }}
                    </div>
                    <div :class="[
                        'flex items-center justify-center w-10 h-10 mx-auto mt-1 rounded-full text-2xl font-bold',
                        day.isToday
                            ? 'bg-brand-600 text-white'
                            : 'text-gray-900 dark:text-white'
                    ]">
                        {{ day.date }}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-500">
                        {{ day.monthName }}
                    </div>
                </div>
            </div>

            <!-- Week Content -->
            <div class="relative">
                <div class="grid grid-cols-7 min-h-[400px]">
                    <div v-for="(day, index) in weekDays" :key="index" @click="handleDayClick(day)"
                        @mousedown="handleMouseDown($event, day)" @mouseenter="handleMouseEnter(day)"
                        @mouseup="handleMouseUp()" @dragover.prevent="handleDragOver" @drop="handleDrop($event, day)"
                        :class="[
                            'p-3 border-r border-gray-200 dark:border-gray-700 last:border-r-0 cursor-pointer transition select-none',
                            day.isToday
                                ? 'bg-brand-50/50 dark:bg-brand-900/10'
                                : 'hover:bg-gray-50 dark:hover:bg-gray-700/50',
                            getDayHolidayStyle(day),
                            isInSelection(day) && 'bg-brand-100 dark:bg-brand-900/40 ring-2 ring-brand-400'
                        ]">
                        <!-- Holiday Indicators (dots only in grid) -->
                        <div v-if="getDayHolidays(day).length > 0" class="flex flex-wrap gap-1 mb-2">
                            <span v-for="holiday in getDayHolidays(day)" :key="'h-' + holiday.id"
                                @click.stop="$emit('holiday-click', holiday)"
                                @mousedown.stop @mouseup.stop
                                class="w-3 h-3 rounded-full cursor-pointer hover:ring-2 ring-offset-1"
                                :style="{ backgroundColor: holiday.color || holidayColor }" :title="holiday.title">
                            </span>
                        </div>

                        <!-- Leave entries for each day (draggable) -->
                        <div v-for="leave in getDayLeaves(day)" :key="'l-' + leave.id"
                            @click.stop="$emit('leave-click', leave)" draggable="true"
                            @mousedown.stop @mouseup.stop
                            @dragstart="handleDragStart($event, leave)"
                            class="text-sm p-2 mb-2 rounded-lg cursor-move bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/60 transition">
                            <div class="font-semibold">{{ leave.employee_name }}</div>
                            <div v-if="getAgentDisplay(leave)" class="text-xs mt-0.5 text-blue-500 dark:text-blue-400">
                                {{ t('calendar.agentShort') }} {{ getAgentDisplay(leave) }}
                            </div>
                            <div v-if="leave.notes" class="text-xs mt-1 opacity-80 line-clamp-2">
                                {{ leave.notes }}
                            </div>
                        </div>

                        <!-- Empty State -->
                        <div v-if="getDayHolidays(day).length === 0 && getDayLeaves(day).length === 0"
                            class="text-center text-gray-400 dark:text-gray-600 text-sm py-4">
                            {{ t('calendar.noEvents') }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Events List Below Calendar -->
        <div :class="['grid grid-cols-1 gap-4', hasBothSections && 'md:grid-cols-2']">
            <!-- Holidays Section -->
            <div v-if="currentWeekHolidays.length > 0"
                class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: holidayColor }"></span>
                    {{ t('calendar.holidaysThisWeek', { count: currentWeekHolidays.length }) }}
                </h3>
                <div class="space-y-2">
                    <div v-for="holiday in currentWeekHolidays" :key="holiday.id"
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
            <div v-if="currentWeekLeaves.length > 0"
                class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full bg-blue-500"></span>
                    {{ t('calendar.leavesThisWeek', { count: currentWeekLeaves.length }) }}
                </h3>
                <div class="space-y-2">
                    <div v-for="leave in currentWeekLeaves" :key="leave.id" @click="$emit('leave-click', leave)"
                        class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition">
                        <div class="w-10 text-center flex-shrink-0">
                            <div class="text-lg font-bold text-gray-900 dark:text-white">{{ formatDay(leave.date) }}
                            </div>
                            <div class="text-xs text-gray-500">{{ formatDayNameShort(leave.date) }}</div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="text-sm font-medium text-gray-900 dark:text-white">
                                {{ leave.employee_name }}
                                <span v-if="leave.employee_emp_id" class="text-sm text-gray-500 dark:text-gray-400 font-normal ml-1">({{ leave.employee_emp_id }})</span>
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
	startDate: Date
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
}>()

// Date range selection state
const isSelecting = ref(false)
const selectionStart = ref<string | null>(null)
const selectionEnd = ref<string | null>(null)

const { t } = useI18n()

const dayNamesShort = computed(() => [
	t('calendar.dayMon'),
	t('calendar.dayTue'),
	t('calendar.dayWed'),
	t('calendar.dayThu'),
	t('calendar.dayFri'),
	t('calendar.daySat'),
	t('calendar.daySun'),
])
const monthNames = computed(() => [
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
const dayNamesFull = computed(() => [
	t('calendar.daySunFull'),
	t('calendar.dayMonFull'),
	t('calendar.dayTueFull'),
	t('calendar.dayWedFull'),
	t('calendar.dayThuFull'),
	t('calendar.dayFriFull'),
	t('calendar.daySatFull'),
])

interface WeekDay {
	dayName: string
	date: number
	monthName: string
	fullDate: string
	isToday: boolean
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

const weekDays = computed<WeekDay[]>(() => {
	const days: WeekDay[] = []
	const todayStr = getTodayStr()

	for (let i = 0; i < 7; i++) {
		const date = new Date(props.startDate)
		date.setDate(date.getDate() + i)
		const fullDate = formatDateStr(date)

		days.push({
			dayName: dayNamesShort.value[i] ?? '',
			date: date.getDate(),
			monthName: monthNames.value[date.getMonth()] ?? '',
			fullDate,
			isToday: fullDate === todayStr,
		})
	}

	return days
})

// Get holidays and leaves for current week
const currentWeekHolidays = computed(() => {
	const weekDates = weekDays.value.map((d) => d.fullDate)
	return props.holidays
		.filter((h) => weekDates.includes(h.date))
		.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const currentWeekLeaves = computed(() => {
	const weekDates = weekDays.value.map((d) => d.fullDate)
	return props.leaves
		.filter((l) => weekDates.includes(l.date))
		.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

// Check if both summary sections have content (for grid layout)
const hasBothSections = computed(
	() => currentWeekHolidays.value.length > 0 && currentWeekLeaves.value.length > 0,
)

const getDayHolidays = (day: WeekDay): Holiday[] => {
	return props.holidays.filter((h) => h.date === day.fullDate)
}

const getDayLeaves = (day: WeekDay): EmployeeLeave[] => {
	return props.leaves.filter((l) => l.date === day.fullDate)
}

const getDayHolidayStyle = (day: WeekDay): string => {
	const dayHolidays = getDayHolidays(day)
	if (dayHolidays.length > 0) {
		return 'holiday-bg'
	}
	return ''
}

const formatDay = (dateStr: string): string => {
	return new Date(dateStr).getDate().toString()
}

const formatDayName = (dateStr: string): string => {
	return dayNamesFull.value[new Date(dateStr).getDay()] ?? ''
}

const formatDayNameShort = (dateStr: string): string => {
	return dayNamesShort.value[(new Date(dateStr).getDay() + 6) % 7] ?? ''
}

// Get agent display text for a leave (names only - for calendar event display)
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

// Get agent display with full details (name, emp_id) - for list section
const getAgentDisplayWithDetails = (leave: EmployeeLeave): string => {
	const parts: string[] = []

	// Add agent details with emp_id
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

const handleDayClick = (day: WeekDay) => {
	emit('date-click', day.fullDate)
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

const handleDrop = (event: DragEvent, day: WeekDay) => {
	event.preventDefault()
	if (draggedLeave && draggedLeave.date !== day.fullDate) {
		emit('leave-move', draggedLeave.id, day.fullDate)
	}
	draggedLeave = null
}

// Date range selection functions
const handleMouseDown = (event: MouseEvent, day: WeekDay) => {
	// Start selection on left mouse button only
	if (event.button !== 0) return

	isSelecting.value = true
	selectionStart.value = day.fullDate
	selectionEnd.value = day.fullDate
}

const handleMouseEnter = (day: WeekDay) => {
	if (isSelecting.value) {
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
		dates.push(formatDateStr(current))
		current.setDate(current.getDate() + 1)
	}

	return dates
}

// Check if a day is within the current selection
const isInSelection = (day: WeekDay): boolean => {
	if (!isSelecting.value || !selectionStart.value || !selectionEnd.value) {
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

<style scoped>
.holiday-bg {
    background-color: v-bind('holidayColor + "20"') !important;
}
</style>
