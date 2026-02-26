<template>
  <AdminLayout>
    <div class="space-y-4">
      <!-- Header -->
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.ptbCalendar.title') }}</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.ptbCalendar.subtitle') }}</p>
        </div>
        <div class="flex flex-wrap items-center gap-2 sm:justify-end">
          <!-- View Mode Toggle - same size as buttons -->
          <div class="flex rounded-lg border border-gray-300 dark:border-gray-600 overflow-hidden h-10">
            <button v-for="mode in viewModes" :key="mode.value" @click="viewMode = mode.value" :class="[
              'px-4 py-2 text-sm font-semibold transition',
              viewMode === mode.value
                ? 'bg-brand-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            ]">
              {{ mode.label }}
            </button>
          </div>

          <!-- Add Holiday - only for PTB admin -->
          <button v-if="isPtbAdmin" type="button"
            class="h-10 rounded-lg border border-brand-300 bg-brand-50 px-5 text-sm font-semibold text-brand-700 transition hover:bg-brand-100 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-200"
            @click="openHolidayForm">
            {{ t('calendar.addHoliday') }}
          </button>
          <button type="button"
            class="h-10 rounded-lg border border-emerald-300 bg-emerald-50 px-5 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-100 focus:outline-hidden focus:ring-3 focus:ring-emerald-500/20 dark:border-emerald-500/40 dark:bg-emerald-500/10 dark:text-emerald-200"
            @click="openLeaveForm">
            {{ t('calendar.takeLeave') }}
          </button>
        </div>
      </div>

      <!-- Navigation Header -->
      <div
        class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <button @click="navigatePrev"
          class="p-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition flex items-center justify-center min-w-[56px] min-h-[56px]">
          <ChevronLeftIcon class="w-7 h-7 text-gray-600 dark:text-gray-400" />
        </button>

        <div class="text-center">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            {{ currentPeriodLabel }}
          </h2>
          <button @click="goToToday" class="text-sm text-brand-600 hover:text-brand-700 dark:text-brand-400">
            {{ t('calendar.today') }}
          </button>
        </div>

        <button @click="navigateNext"
          class="p-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition flex items-center justify-center min-w-[56px] min-h-[56px]">
          <ChevronRightIcon class="w-7 h-7 text-gray-600 dark:text-gray-400" />
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="h-10 w-10 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></div>
      </div>

      <!-- Calendar Views -->
      <template v-else>
        <!-- Month View -->
        <MonthView v-if="viewMode === 'month'" :year="currentYear" :month="currentMonth" :holidays="holidays"
          :leaves="leaves" :holiday-color="holidayColor" @date-click="handleDateClick"
          @date-range-select="handleDateRangeSelect" @holiday-click="editHoliday" @leave-click="editLeave"
          @leave-move="handleLeaveMove" @week-click="goToWeek" />

        <!-- Week View -->
        <WeekView v-if="viewMode === 'week'" :start-date="weekStartDate" :holidays="holidays" :leaves="leaves"
          :holiday-color="holidayColor" @date-click="handleDateClick" @date-range-select="handleDateRangeSelect"
          @holiday-click="editHoliday" @leave-click="editLeave" @leave-move="handleLeaveMove" />

        <!-- Year View -->
        <YearView v-if="viewMode === 'year'" :year="currentYear" :holidays="holidays" :leaves="leaves"
          :holiday-color="holidayColor" @month-click="goToMonth" @holiday-click="editHoliday" @leave-click="editLeave"
          @date-click="handleDateClick" @date-range-select="handleDateRangeSelect" @week-click="goToWeek" />

        <!-- List View -->
        <ListView v-if="viewMode === 'list'" :year="currentYear" :month="currentMonth" :holidays="holidays"
          :leaves="leaves" :holiday-color="holidayColor" @holiday-click="editHoliday" @leave-click="editLeave" />
      </template>

      <!-- Holiday Form Modal -->
      <HolidayFormModal v-if="showHolidayForm" :holiday="selectedHoliday" :initial-date="selectedDate"
        :initial-dates="selectedDates" :can-delete="canDelete" @close="closeHolidayForm" @save="saveHoliday"
        @delete="confirmDeleteHoliday" />

      <!-- Leave Form Modal -->
      <LeaveFormModal v-if="showLeaveForm" :leave="selectedLeave" :initial-date="selectedDate"
        :initial-dates="selectedDates" :employees="employees" :can-delete="canDelete" @close="closeLeaveForm"
        @save="saveLeave" @delete="confirmDeleteLeave" />

      <!-- Combined Modal for PTB Admins (when clicking on a date) -->
      <Teleport to="body">
        <div v-if="showCombinedModal" class="fixed inset-0 z-[99999] flex items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-black/50" @click="closeCombinedModal"></div>

          <!-- Modal -->
          <div
            role="dialog" aria-modal="true" aria-labelledby="ptb-combined-modal-title"
            class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
            <!-- Header with Tabs -->
            <div class="border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-center justify-between px-4 pt-4">
                <h3 id="ptb-combined-modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ selectedDate ? formatDateForHeader(selectedDate) : t('calendar.newEvent') }}
                </h3>
                <button @click="closeCombinedModal"
                  class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
                  <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div class="flex px-4 mt-2">
                <button @click="combinedModalTab = 'leave'" :class="[
                  'px-4 py-2 text-sm font-medium border-b-2 transition',
                  combinedModalTab === 'leave'
                    ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                ]">
                  {{ t('calendar.tabLeave') }}
                </button>
                <button @click="combinedModalTab = 'holiday'" :class="[
                  'px-4 py-2 text-sm font-medium border-b-2 transition',
                  combinedModalTab === 'holiday'
                    ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                ]">
                  {{ t('calendar.tabHoliday') }}
                </button>
              </div>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto">
              <!-- Leave Tab -->
              <CombinedLeaveForm v-if="combinedModalTab === 'leave'" :initial-date="selectedDate"
                :initial-dates="selectedDates" :employees="employees" @save="saveCombinedLeave"
                @cancel="closeCombinedModal" />

              <!-- Holiday Tab -->
              <CombinedHolidayForm v-if="combinedModalTab === 'holiday'" :initial-date="selectedDate"
                :initial-dates="selectedDates" @save="saveCombinedHoliday" @cancel="closeCombinedModal" />
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Delete Confirmation Modal -->
      <Teleport to="body">
        <div v-if="showDeleteModal"
          class="fixed inset-0 z-[100000] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div
            role="dialog" aria-modal="true" aria-labelledby="ptb-delete-modal-title"
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6 transform transition-[transform,opacity]">
            <div class="flex items-center gap-3 mb-4">
              <div
                class="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 id="ptb-delete-modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ deleteType === 'holiday' ? t('calendar.deleteHoliday') : t('calendar.deleteLeave') }}
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('calendar.deleteConfirm') }}
                </p>
              </div>
            </div>

            <p class="text-gray-600 dark:text-gray-300 mb-6">
              {{ deleteType === 'holiday' ? t('calendar.deleteHolidayConfirm') : t('calendar.deleteLeaveConfirm') }}
              <span v-if="deleteItemName" class="font-medium block mt-1">
                "{{ deleteItemName }}"
              </span>
            </p>

            <div class="flex gap-3 justify-end">
              <button @click="cancelDelete"
                class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                {{ t('common.cancel') }}
              </button>
              <button @click="executeDelete" :disabled="isDeleting"
                class="px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 rounded-lg border border-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition">
                <span v-if="isDeleting" class="flex items-center gap-2">
                  <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                    </circle>
                    <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                  </svg>
                  {{ t('common.deleting') }}
                </span>
                <span v-else>{{ t('common.delete') }}</span>
              </button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import CombinedHolidayForm from '@/components/ptb-calendar/CombinedHolidayForm.vue'
import CombinedLeaveForm from '@/components/ptb-calendar/CombinedLeaveForm.vue'
import HolidayFormModal from '@/components/ptb-calendar/HolidayFormModal.vue'
import LeaveFormModal from '@/components/ptb-calendar/LeaveFormModal.vue'
import ListView from '@/components/ptb-calendar/ListView.vue'
// Components
import MonthView from '@/components/ptb-calendar/MonthView.vue'
import WeekView from '@/components/ptb-calendar/WeekView.vue'
import YearView from '@/components/ptb-calendar/YearView.vue'
import { useToast } from '@/composables/useToast'
import { ChevronLeftIcon, ChevronRightIcon } from '@/icons'
import { type EmployeeLeave, employeeLeaveAPI, type Holiday, holidayAPI } from '@/services/api'
import { disconnectCalendarWebSocket, useCalendarWebSocket } from '@/services/websocket'
import { useAuthStore } from '@/stores/auth'
import { useEmployeeStore } from '@/stores/employee'

const authStore = useAuthStore()
const { t } = useI18n()
const employeeStore = useEmployeeStore()
const { showToast } = useToast()

// View modes
const viewModes = computed(() => [
	{ value: 'week' as const, label: t('calendar.week') },
	{ value: 'month' as const, label: t('calendar.month') },
	{ value: 'year' as const, label: t('calendar.year') },
	{ value: 'list' as const, label: t('calendar.list') },
])

// Load view mode from localStorage or default to 'month'
const savedViewMode = localStorage.getItem('ptb-calendar-view-mode') as
	| 'week'
	| 'month'
	| 'year'
	| 'list'
	| null
const viewMode = ref<'week' | 'month' | 'year' | 'list'>(
	savedViewMode && ['week', 'month', 'year', 'list'].includes(savedViewMode)
		? savedViewMode
		: 'month',
)

// State
const loading = ref(false)
const holidays = ref<Holiday[]>([])
const leaves = ref<EmployeeLeave[]>([])
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth()) // 0-indexed
const currentWeekStart = ref(new Date())
let calendarFetchAbortController: AbortController | null = null

// Default soft pink color for holidays
const holidayColor = ref('#FFB6C1')

// Form states
const showHolidayForm = ref(false)
const showLeaveForm = ref(false)
const showCombinedModal = ref(false)
const combinedModalTab = ref<'leave' | 'holiday'>('leave')
const selectedHoliday = ref<Holiday | null>(null)
const selectedLeave = ref<EmployeeLeave | null>(null)
const selectedDate = ref<string | null>(null)
const selectedDates = ref<string[] | null>(null)

// Delete confirmation modal states
const showDeleteModal = ref(false)
const deleteType = ref<'holiday' | 'leave'>('holiday')
const deleteItemId = ref<number | null>(null)
const deleteItemName = ref<string>('')
const isDeleting = ref(false)

// Permissions
const canDelete = computed(() => authStore.hasPermission('calendar', 'delete'))
const isPtbAdmin = computed(() => authStore.isPtbAdmin || authStore.isSuperAdmin)

// Employees for leave form - only enabled employees
const employees = computed(() => employeeStore.employees.filter((e) => e.is_enabled))

// Computed
const currentPeriodLabel = computed(() => {
	const monthKeys = [
		'months.january',
		'months.february',
		'months.march',
		'months.april',
		'months.may',
		'months.june',
		'months.july',
		'months.august',
		'months.september',
		'months.october',
		'months.november',
		'months.december',
	]

	if (viewMode.value === 'year') {
		return `${currentYear.value}`
	} else if (viewMode.value === 'week') {
		const endDate = new Date(weekStartDate.value)
		endDate.setDate(endDate.getDate() + 6)
		const startMonth = t(monthKeys[weekStartDate.value.getMonth()]!)
		const endMonth = t(monthKeys[endDate.getMonth()]!)
		const weekNum = getWeekNumber(weekStartDate.value)
		if (startMonth === endMonth) {
			return `${startMonth} ${weekStartDate.value.getDate()} - ${endDate.getDate()}, ${currentYear.value} (Week ${weekNum})`
		}
		return `${startMonth} ${weekStartDate.value.getDate()} - ${endMonth} ${endDate.getDate()}, ${currentYear.value} (Week ${weekNum})`
	}
	return `${t(monthKeys[currentMonth.value]!)} ${currentYear.value}`
})

const weekStartDate = computed(() => {
	const date = new Date(currentWeekStart.value)
	const day = date.getDay()
	const diff = date.getDate() - day + (day === 0 ? -6 : 1) // Adjust when day is sunday
	date.setDate(diff)
	return date
})

// Methods
const isAbortError = (err: unknown) => {
	return (
		(err instanceof DOMException && err.name === 'AbortError') ||
		(typeof err === 'object' &&
			err !== null &&
			('code' in err || 'name' in err) &&
			((err as { code?: string }).code === 'ERR_CANCELED' ||
				(err as { name?: string }).name === 'CanceledError'))
	)
}

const fetchData = async () => {
	if (calendarFetchAbortController) {
		calendarFetchAbortController.abort()
	}
	const controller = new AbortController()
	calendarFetchAbortController = controller

	loading.value = true
	try {
		let params: {
			year?: number
			month?: number
			start_date?: string
			end_date?: string
		} = {}

		if (viewMode.value === 'year') {
			params = { year: currentYear.value }
		} else if (viewMode.value === 'week') {
			const startDate = weekStartDate.value
			const endDate = new Date(startDate)
			endDate.setDate(endDate.getDate() + 6)
			params = {
				start_date: formatDate(startDate),
				end_date: formatDate(endDate),
			}
		} else {
			params = { year: currentYear.value, month: currentMonth.value + 1 }
		}

		const [holidayData, leaveData] = await Promise.all([
			holidayAPI.list(params, { signal: controller.signal }),
			employeeLeaveAPI.list(params, { signal: controller.signal }),
		])

		holidays.value = holidayData
		leaves.value = leaveData
	} catch (err) {
		if (isAbortError(err)) {
			return
		}
		console.error('Failed to fetch calendar data:', err)
	} finally {
		if (calendarFetchAbortController === controller) {
			calendarFetchAbortController = null
			loading.value = false
		}
	}
}

const formatDate = (date: Date): string => {
	// Use local date components to avoid UTC timezone shift
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

// Get ISO week number
const getWeekNumber = (date: Date): number => {
	const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
	const dayNum = d.getUTCDay() || 7
	d.setUTCDate(d.getUTCDate() + 4 - dayNum)
	const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
	return Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
}

const formatDateForHeader = (dateStr: string): string => {
	const date = new Date(dateStr)
	const dayKeys = [
		'common.sunday',
		'common.monday',
		'common.tuesday',
		'common.wednesday',
		'common.thursday',
		'common.friday',
		'common.saturday',
	]
	const monthKeys = [
		'months.january',
		'months.february',
		'months.march',
		'months.april',
		'months.may',
		'months.june',
		'months.july',
		'months.august',
		'months.september',
		'months.october',
		'months.november',
		'months.december',
	]
	return `${t(dayKeys[date.getDay()]!)}, ${t(monthKeys[date.getMonth()]!)} ${date.getDate()}, ${date.getFullYear()}`
}

const navigatePrev = () => {
	if (viewMode.value === 'year') {
		currentYear.value--
	} else if (viewMode.value === 'week') {
		const newDate = new Date(currentWeekStart.value)
		newDate.setDate(newDate.getDate() - 7)
		currentWeekStart.value = newDate
		currentYear.value = newDate.getFullYear()
		currentMonth.value = newDate.getMonth()
	} else {
		if (currentMonth.value === 0) {
			currentMonth.value = 11
			currentYear.value--
		} else {
			currentMonth.value--
		}
	}
}

const navigateNext = () => {
	if (viewMode.value === 'year') {
		currentYear.value++
	} else if (viewMode.value === 'week') {
		const newDate = new Date(currentWeekStart.value)
		newDate.setDate(newDate.getDate() + 7)
		currentWeekStart.value = newDate
		currentYear.value = newDate.getFullYear()
		currentMonth.value = newDate.getMonth()
	} else {
		if (currentMonth.value === 11) {
			currentMonth.value = 0
			currentYear.value++
		} else {
			currentMonth.value++
		}
	}
}

const goToToday = () => {
	const today = new Date()
	currentYear.value = today.getFullYear()
	currentMonth.value = today.getMonth()
	currentWeekStart.value = today
}

const goToMonth = (month: number) => {
	currentMonth.value = month
	viewMode.value = 'month'
}

const goToWeek = (startDate: Date) => {
	currentWeekStart.value = startDate
	currentYear.value = startDate.getFullYear()
	currentMonth.value = startDate.getMonth()
	viewMode.value = 'week'
}

const handleDateClick = (date: string) => {
	selectedDate.value = date
	selectedDates.value = null
	// Check if there's a holiday on this date
	const holiday = holidays.value.find((h) => h.date === date)
	if (holiday) {
		editHoliday(holiday)
	} else {
		// For PTB admins, show combined modal with tabs
		// For regular users, just show leave form
		if (isPtbAdmin.value) {
			combinedModalTab.value = 'leave' // Default to leave tab
			showCombinedModal.value = true
		} else {
			openLeaveForm()
		}
	}
}

// Handle date range selection from calendar views
const handleDateRangeSelect = (dates: string[]) => {
	if (dates.length === 0) return
	selectedDate.value = dates[0] ?? null
	selectedDates.value = dates
	// For PTB admins, show combined modal with tabs
	// For regular users, just show leave form
	if (isPtbAdmin.value) {
		combinedModalTab.value = 'leave' // Default to leave tab
		showCombinedModal.value = true
	} else {
		openLeaveForm()
	}
}

// Combined modal (for PTB admins clicking on date)
const closeCombinedModal = () => {
	showCombinedModal.value = false
	selectedDate.value = null
	selectedDates.value = null
}

const saveCombinedHoliday = async (data: Partial<Holiday> & { dates?: string[] }) => {
	try {
		// Create a holiday for each date in the range
		const dates = data.dates && data.dates.length > 0 ? data.dates : data.date ? [data.date] : []
		for (const date of dates) {
			await holidayAPI.create({
				title: data.title,
				date: date,
				description: data.description,
				color: data.color,
				is_recurring: data.is_recurring,
			} as Omit<Holiday, 'id' | 'created_at' | 'updated_at' | 'created_by' | 'created_by_username'>)
		}
		closeCombinedModal()
		await fetchData()
	} catch (err) {
		console.error('Failed to save holiday:', err)
		showToast('Failed to save holiday', 'error')
	}
}

const saveCombinedLeave = async (data: {
	employee: number
	date: string
	dates?: string[]
	notes?: string
	agents?: number[]
	agent_names?: string
}) => {
	try {
		// Create a leave for each date in the range
		const dates = data.dates && data.dates.length > 0 ? data.dates : [data.date]
		for (const date of dates) {
			await employeeLeaveAPI.create({
				employee: data.employee,
				date: date,
				notes: data.notes,
				agents: data.agents,
				agent_names: data.agent_names,
			})
		}
		closeCombinedModal()
		await fetchData()
	} catch (err) {
		console.error('Failed to save leave:', err)
		showToast('Failed to save leave', 'error')
	}
}

// Holiday form
const openHolidayForm = () => {
	selectedHoliday.value = null
	showHolidayForm.value = true
}

const editHoliday = (holiday: Holiday) => {
	// Only PTB admins can edit/delete holidays
	if (!isPtbAdmin.value) return
	selectedHoliday.value = holiday
	selectedDate.value = holiday.date
	showHolidayForm.value = true
}

const closeHolidayForm = () => {
	showHolidayForm.value = false
	selectedHoliday.value = null
	selectedDate.value = null
}

const saveHoliday = async (data: Partial<Holiday> & { dates?: string[] }) => {
	try {
		if (selectedHoliday.value) {
			// For update, just update the single holiday
			await holidayAPI.update(selectedHoliday.value.id, data)
		} else {
			// For create, make multiple holidays for each date in range
			const dates = data.dates && data.dates.length > 0 ? data.dates : data.date ? [data.date] : []
			await Promise.all(
				dates.map((date) =>
					holidayAPI.create({
						title: data.title,
						date: date,
						description: data.description,
						color: data.color,
						is_recurring: data.is_recurring,
					} as Omit<Holiday, 'id' | 'created_at' | 'updated_at' | 'created_by' | 'created_by_username'>),
				),
			)
		}
		closeHolidayForm()
		await fetchData()
	} catch (err) {
		console.error('Failed to save holiday:', err)
		showToast('Failed to save holiday', 'error')
	}
}

// Delete confirmation modal methods
const confirmDeleteHoliday = (id: number) => {
	const holiday = holidays.value.find((h) => h.id === id)
	deleteType.value = 'holiday'
	deleteItemId.value = id
	deleteItemName.value = holiday?.title || ''
	showDeleteModal.value = true
}

const confirmDeleteLeave = (id: number) => {
	const leave = leaves.value.find((l) => l.id === id)
	deleteType.value = 'leave'
	deleteItemId.value = id
	deleteItemName.value = leave?.employee_name || ''
	showDeleteModal.value = true
}

const cancelDelete = () => {
	showDeleteModal.value = false
	deleteItemId.value = null
	deleteItemName.value = ''
}

const executeDelete = async () => {
	if (!deleteItemId.value) return

	isDeleting.value = true
	try {
		if (deleteType.value === 'holiday') {
			await holidayAPI.delete(deleteItemId.value)
			closeHolidayForm()
		} else {
			await employeeLeaveAPI.delete(deleteItemId.value)
			closeLeaveForm()
		}
		await fetchData()
	} catch (err) {
		console.error(`Failed to delete ${deleteType.value}:`, err)
		showToast(`Failed to delete ${deleteType.value}`, 'error')
	} finally {
		isDeleting.value = false
		cancelDelete()
	}
}

// Leave form
const openLeaveForm = () => {
	selectedLeave.value = null
	showLeaveForm.value = true
}

const editLeave = (leave: EmployeeLeave) => {
	selectedLeave.value = leave
	selectedDate.value = leave.date
	showLeaveForm.value = true
}

const closeLeaveForm = () => {
	showLeaveForm.value = false
	selectedLeave.value = null
	selectedDate.value = null
}

const saveLeave = async (data: {
	employee: number
	date: string
	dates?: string[]
	notes?: string
	agents?: number[]
	agent_names?: string
}) => {
	try {
		if (selectedLeave.value) {
			// For update, just update the single leave
			await employeeLeaveAPI.update(selectedLeave.value.id, data)
		} else {
			// For create, make multiple leaves for each date in range
			const dates = data.dates && data.dates.length > 0 ? data.dates : [data.date]
			await Promise.all(
				dates.map((date) =>
					employeeLeaveAPI.create({
						employee: data.employee,
						date: date,
						notes: data.notes,
						agents: data.agents,
						agent_names: data.agent_names,
					}),
				),
			)
		}
		closeLeaveForm()
		await fetchData()
	} catch (err) {
		console.error('Failed to save leave:', err)
		showToast('Failed to save leave', 'error')
	}
}

// Handle leave drag and drop
const handleLeaveMove = async (leaveId: number, newDate: string) => {
	const leave = leaves.value.find((l) => l.id === leaveId)
	if (!leave) return

	try {
		await employeeLeaveAPI.update(leaveId, {
			employee: leave.employee,
			date: newDate,
			notes: leave.notes,
		})
		await fetchData()
	} catch (err) {
		console.error('Failed to move leave:', err)
		showToast('Failed to move leave', 'error')
	}
}

// Watchers — debounce to avoid double-fires on month boundary
let fetchDebounceTimer: ReturnType<typeof setTimeout> | null = null
watch([viewMode, currentYear, currentMonth, currentWeekStart], () => {
	if (fetchDebounceTimer) clearTimeout(fetchDebounceTimer)
	fetchDebounceTimer = setTimeout(() => {
		void fetchData()
	}, 50)
})

// Save view mode to localStorage when it changes
watch(viewMode, (newMode) => {
	localStorage.setItem('ptb-calendar-view-mode', newMode)
})

// Lifecycle
onMounted(async () => {
	// Fetch employees and calendar data in parallel
	await Promise.all([employeeStore.fetchEmployees(), fetchData()])

	// Connect Calendar WebSocket for real-time updates
	const calendarWs = useCalendarWebSocket()
	calendarWs.onCalendarUpdate = (action, entityType, data) => {
		if (entityType === 'holiday') {
			if (action === 'created') {
				const h = data as unknown as Holiday
				// Avoid duplicates
				if (!holidays.value.find((x) => x.id === h.id)) {
					holidays.value.push(h)
				}
			} else if (action === 'updated') {
				const h = data as unknown as Holiday
				const idx = holidays.value.findIndex((x) => x.id === h.id)
				if (idx !== -1) holidays.value[idx] = h
				else holidays.value.push(h)
			} else if (action === 'deleted') {
				holidays.value = holidays.value.filter((x) => x.id !== (data as { id: number }).id)
			}
		} else if (entityType === 'leave') {
			if (action === 'created') {
				const l = data as unknown as EmployeeLeave
				if (!leaves.value.find((x) => x.id === l.id)) {
					leaves.value.push(l)
				}
			} else if (action === 'updated') {
				const l = data as unknown as EmployeeLeave
				const idx = leaves.value.findIndex((x) => x.id === l.id)
				if (idx !== -1) leaves.value[idx] = l
				else leaves.value.push(l)
			} else if (action === 'deleted') {
				leaves.value = leaves.value.filter((x) => x.id !== (data as { id: number }).id)
			}
		}
	}
	calendarWs.connect()
})

onUnmounted(() => {
	if (fetchDebounceTimer) {
		clearTimeout(fetchDebounceTimer)
		fetchDebounceTimer = null
	}
	if (calendarFetchAbortController) {
		calendarFetchAbortController.abort()
		calendarFetchAbortController = null
	}
	disconnectCalendarWebSocket()
})
</script>
