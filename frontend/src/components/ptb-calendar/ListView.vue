<template>
    <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <!-- Tabs -->
        <div class="flex border-b border-gray-200 dark:border-gray-700">
            <button v-for="tab in tabs" :key="tab.value" @click="activeTab = tab.value" :class="[
                'px-4 py-3 text-sm font-medium transition border-b-2',
                activeTab === tab.value
                    ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            ]">
                {{ tab.label }} ({{ tab.value === 'holidays' ? holidays.length : leaves.length }})
            </button>
        </div>

        <!-- Holidays List -->
        <div v-if="activeTab === 'holidays'" class="divide-y divide-gray-200 dark:divide-gray-700">
            <div v-if="sortedHolidays.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
                {{ t('calendar.noHolidaysForPeriod') }}
            </div>
            <div v-for="holiday in sortedHolidays" :key="holiday.id" @click="$emit('holiday-click', holiday)" :class="[
                'p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition',
                isToday(holiday.date) && 'bg-brand-50/30 dark:bg-brand-900/10'
            ]">
                <div class="flex items-start gap-4">
                    <!-- Date Badge -->
                    <div class="flex-shrink-0 text-center">
                        <div class="w-14 h-14 rounded-lg flex flex-col items-center justify-center"
                            :style="{ backgroundColor: holiday.color || holidayColor }">
                            <span class="text-lg font-bold"
                                :style="{ color: getContrastColor(holiday.color || holidayColor) }">
                                {{ formatDay(holiday.date) }}
                            </span>
                            <span class="text-xs" :style="{ color: getContrastColor(holiday.color || holidayColor) }">
                                {{ formatMonth(holiday.date) }}
                            </span>
                        </div>
                        <span v-if="isToday(holiday.date)"
                            class="text-xs font-medium text-brand-600 dark:text-brand-400 mt-1 block">
                            {{ t('calendar.today') }}
                        </span>
                    </div>

                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                        <h4 class="text-base font-semibold text-gray-900 dark:text-white">
                            {{ holiday.title }}
                        </h4>
                        <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                            {{ formatFullDate(holiday.date) }}
                            <span v-if="holiday.is_recurring"
                                class="ml-2 text-xs px-1.5 py-0.5 rounded bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300">
                                {{ t('calendar.recurring') }}
                            </span>
                        </p>
                        <p v-if="holiday.description"
                            class="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                            {{ holiday.description }}
                        </p>
                    </div>

                    <!-- Arrow -->
                    <ChevronRightIcon class="w-5 h-5 text-gray-400 flex-shrink-0" />
                </div>
            </div>
        </div>

        <!-- Leaves List -->
        <div v-if="activeTab === 'leaves'" class="divide-y divide-gray-200 dark:divide-gray-700">
            <div v-if="sortedLeaves.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
                {{ t('calendar.noLeavesForPeriod') }}
            </div>
            <div v-for="leave in sortedLeaves" :key="leave.id" @click="$emit('leave-click', leave)" :class="[
                'p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition',
                isToday(leave.date) && 'bg-brand-50/30 dark:bg-brand-900/10'
            ]">
                <div class="flex items-start gap-4">
                    <!-- Date Badge -->
                    <div class="flex-shrink-0 text-center">
                        <div class="w-14 h-14 rounded-lg bg-blue-100 dark:bg-blue-900/40 flex flex-col items-center justify-center">
                            <span class="text-lg font-bold text-blue-700 dark:text-blue-300">
                                {{ formatDay(leave.date) }}
                            </span>
                            <span class="text-xs text-blue-600 dark:text-blue-400">
                                {{ formatMonth(leave.date) }}
                            </span>
                        </div>
                        <span v-if="isToday(leave.date)"
                            class="text-xs font-medium text-brand-600 dark:text-brand-400 mt-1 block">
                            {{ t('calendar.today') }}
                        </span>
                    </div>

                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                        <!-- Employee Name with ID inline -->
                        <div class="flex flex-wrap items-baseline gap-x-2">
                            <h4 class="text-base font-bold text-gray-900 dark:text-white">
                                {{ leave.employee_name }}
                            </h4>
                            <span v-if="leave.employee_emp_id" class="text-base text-gray-500 dark:text-gray-400">
                                ({{ leave.employee_emp_id }})
                            </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                            {{ formatFullDate(leave.date) }}
                        </p>
                        <p v-if="getAgentDisplayWithDetails(leave)" 
                           class="text-sm text-blue-600 dark:text-blue-400 mt-1 font-medium">
                            {{ t('calendar.agent') }} {{ getAgentDisplayWithDetails(leave) }}
                        </p>
                        <p v-if="leave.notes" class="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                            {{ leave.notes }}
                        </p>
                    </div>

                    <!-- Arrow -->
                    <ChevronRightIcon class="w-5 h-5 text-gray-400 flex-shrink-0" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronRightIcon } from '@/icons'
import type { EmployeeLeave, Holiday } from '@/services/api/holiday'

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

const { t } = useI18n()

defineEmits<{
	(e: 'holiday-click', holiday: Holiday): void
	(e: 'leave-click', leave: EmployeeLeave): void
}>()

const tabs = computed(() => [
	{ value: 'holidays' as const, label: t('calendar.holidays') },
	{ value: 'leaves' as const, label: t('calendar.leaves') },
])

const activeTab = ref<'holidays' | 'leaves'>('holidays')

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
const dayNames = computed(() => [
	t('calendar.daySunFull'),
	t('calendar.dayMonFull'),
	t('calendar.dayTueFull'),
	t('calendar.dayWedFull'),
	t('calendar.dayThuFull'),
	t('calendar.dayFriFull'),
	t('calendar.daySatFull'),
])

const sortedHolidays = computed(() => {
	return [...props.holidays].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const sortedLeaves = computed(() => {
	return [...props.leaves].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

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

const isToday = (dateStr: string): boolean => {
	return dateStr === getTodayStr()
}

const formatDay = (dateStr: string): string => {
	return new Date(dateStr).getDate().toString()
}

const formatMonth = (dateStr: string): string => {
	return monthNames.value[new Date(dateStr).getMonth()] ?? ''
}

const formatFullDate = (dateStr: string): string => {
	const date = new Date(dateStr)
	const dayName = dayNames.value[date.getDay()] ?? ''
	const day = date.getDate()
	const month = monthNames.value[date.getMonth()] ?? ''
	const year = date.getFullYear()
	return `${dayName}, ${month} ${day}, ${year}`
}

// Get agent display with full details (name, emp_id)
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

const getContrastColor = (hexColor: string): string => {
	const hex = hexColor.replace('#', '')
	const r = parseInt(hex.substr(0, 2), 16)
	const g = parseInt(hex.substr(2, 2), 16)
	const b = parseInt(hex.substr(4, 2), 16)
	const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
	return luminance > 0.5 ? '#1f2937' : '#ffffff'
}
</script>
