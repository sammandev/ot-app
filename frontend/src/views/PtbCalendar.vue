<template>
	<AdminLayout>
		<div class="space-y-4">
			<!-- Header -->
			<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.ptbCalendar.title') }}
					</h1>
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
					:leaves="leaves" :holiday-color="holidayColor" :can-manage-leave="canManageLeave" @date-click="handleDateClick"
					@date-range-select="handleDateRangeSelect" @holiday-click="openHolidayDetails"
					@leave-click="openLeaveDetails" @leave-move="handleLeaveMove" @week-click="goToWeek" />

				<!-- Week View -->
				<WeekView v-if="viewMode === 'week'" :start-date="weekStartDate" :holidays="holidays" :leaves="leaves"
					:holiday-color="holidayColor" :can-manage-leave="canManageLeave" @date-click="handleDateClick"
					@date-range-select="handleDateRangeSelect" @holiday-click="openHolidayDetails"
					@leave-click="openLeaveDetails" @leave-move="handleLeaveMove" />

				<!-- Year View -->
				<YearView v-if="viewMode === 'year'" :year="currentYear" :holidays="holidays" :leaves="leaves"
					:holiday-color="holidayColor" @month-click="goToMonth" @holiday-click="openHolidayDetails"
					@leave-click="openLeaveDetails" @date-click="handleDateClick"
					@date-range-select="handleDateRangeSelect" @week-click="goToWeek" />

				<!-- List View -->
				<ListView v-if="viewMode === 'list'" :year="currentYear" :month="currentMonth" :holidays="holidays"
					:leaves="leaves" :holiday-color="holidayColor" @holiday-click="openHolidayDetails"
					@leave-click="openLeaveDetails" />
			</template>

			<HolidayDetailsModal v-if="showHolidayDetails && selectedHolidayDetails" :holiday="selectedHolidayDetails"
				:can-edit="isPtbAdmin" @close="closeHolidayDetails" @edit="editHolidayFromDetails" />

			<LeaveDetailsModal v-if="showLeaveDetails && selectedLeaveDetails" :leave="selectedLeaveDetails"
				:related-leaves="selectedLeaveGroup" :can-edit="selectedLeaveCanManage" @close="closeLeaveDetails"
				@edit="editLeaveFromDetails" />

			<!-- Holiday Form Modal -->
			<HolidayFormModal v-if="showHolidayForm" :holiday="selectedHoliday" :initial-date="selectedDate"
				:initial-dates="selectedDates" :can-delete="canDelete" @close="closeHolidayForm" @save="saveHoliday"
				@delete="confirmDeleteHoliday" />

			<!-- Leave Form Modal -->
			<LeaveFormModal v-if="showLeaveForm" :leave="selectedLeave" :initial-date="selectedDate"
				:initial-dates="selectedDates" :employees="employees" :can-delete="selectedLeaveCanManage" @close="closeLeaveForm"
				@save="saveLeave" @delete="confirmDeleteLeave" />

			<!-- Combined Modal for PTB Admins (when clicking on a date) -->
			<Teleport to="body">
				<div v-if="showCombinedModal" class="fixed inset-0 z-[99999] flex items-center justify-center p-4">
					<!-- Backdrop -->
					<div class="absolute inset-0 bg-black/50" @click="closeCombinedModal"></div>

					<!-- Modal -->
					<div role="dialog" aria-modal="true" aria-labelledby="ptb-combined-modal-title"
						class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
						<!-- Header with Tabs -->
						<div class="border-b border-gray-200 dark:border-gray-700">
							<div class="flex items-center justify-between px-4 pt-4">
								<h3 id="ptb-combined-modal-title"
									class="text-lg font-semibold text-gray-900 dark:text-white">
									{{ selectedDate ? formatDateForHeader(selectedDate) : t('calendar.newEvent') }}
								</h3>
								<button @click="closeCombinedModal"
									class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
									<svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor"
										viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
											d="M6 18L18 6M6 6l12 12" />
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
								:initial-dates="selectedDates" @save="saveCombinedHoliday"
								@cancel="closeCombinedModal" />
						</div>
					</div>
				</div>
			</Teleport>

			<!-- Delete Confirmation Modal -->
			<Teleport to="body">
				<div v-if="showDeleteModal"
					class="fixed inset-0 z-[100000] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
					<div role="dialog" aria-modal="true" aria-labelledby="ptb-delete-modal-title"
						class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full p-6 transform transition-[transform,opacity]">
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
								<h3 id="ptb-delete-modal-title"
									class="text-lg font-semibold text-gray-900 dark:text-white">
									{{ deleteType === 'holiday' ? t('calendar.deleteHoliday') :
										t('calendar.deleteLeave') }}
								</h3>
								<p class="text-sm text-gray-500 dark:text-gray-400">
									{{ t('calendar.deleteConfirm') }}
								</p>
							</div>
						</div>

						<p class="text-gray-600 dark:text-gray-300 mb-6">
							{{ deleteType === 'holiday' ? t('calendar.deleteHolidayConfirm') : deleteLeaveIntroText }}
							<span v-if="deleteItemName" class="font-medium block mt-1">
								"{{ deleteItemName }}"
							</span>
						</p>

						<div v-if="deleteType === 'leave' && deleteLeaveOptions.length > 1" class="mb-6 space-y-4">
							<div
								class="rounded-2xl border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900/60">
								<label
									class="flex cursor-pointer items-start gap-3 rounded-xl px-3 py-2 transition hover:bg-white dark:hover:bg-gray-800/80">
									<input v-model="deleteLeaveScope" type="radio" value="selection"
										class="mt-1 h-4 w-4 border-gray-300 text-red-600 focus:ring-red-500" />
									<div>
										<p class="text-sm font-semibold text-gray-900 dark:text-white">
											{{ t('calendar.deleteLeaveOneDate') }}</p>
										<p class="mt-1 text-xs leading-5 text-gray-500 dark:text-gray-400">
											{{ t('calendar.deleteLeaveSingleHint') }}</p>
									</div>
								</label>
								<label
									class="mt-2 flex cursor-pointer items-start gap-3 rounded-xl px-3 py-2 transition hover:bg-white dark:hover:bg-gray-800/80">
									<input v-model="deleteLeaveScope" type="radio" value="batch"
										class="mt-1 h-4 w-4 border-gray-300 text-red-600 focus:ring-red-500" />
									<div>
										<p class="text-sm font-semibold text-gray-900 dark:text-white">
											{{ t('calendar.deleteLeaveWholeBatch') }}
										</p>
										<p class="mt-1 text-xs leading-5 text-gray-500 dark:text-gray-400">
											{{ t('calendar.deleteLeaveBatchHint', { count: deleteLeaveOptions.length }) }}
										</p>
									</div>
								</label>
							</div>

							<div v-if="deleteLeaveScope === 'selection'"
								class="rounded-2xl border border-gray-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-900/60">
								<p
									class="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
									{{ t('calendar.deleteLeaveChooseDate') }}</p>
								<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">{{
									t('calendar.deleteLeaveSelectionSummary', {
										count: deleteLeaveSelectedCount, total:
									deleteLeaveOptions.length }) }}</p>
								<div class="mt-3 max-h-52 space-y-2 overflow-y-auto pr-1">
									<label v-for="leaveOption in deleteLeaveOptions" :key="leaveOption.id"
										class="flex cursor-pointer items-center gap-3 rounded-xl border border-gray-200 px-3 py-3 transition hover:border-red-300 hover:bg-red-50/60 dark:border-gray-700 dark:hover:border-red-500/40 dark:hover:bg-red-900/10">
										<input v-model="deleteLeaveTargetIds" type="checkbox" :value="leaveOption.id"
											class="h-4 w-4 border-gray-300 text-red-600 focus:ring-red-500" />
										<div class="min-w-0">
											<p class="text-sm font-semibold text-gray-900 dark:text-white">
												{{ formatDeleteLeaveDate(leaveOption.date) }}</p>
											<p class="text-xs text-gray-500 dark:text-gray-400">
												{{ leaveOption.employee_name }} · {{ leaveOption.employee_emp_id || '-' }}
											</p>
										</div>
									</label>
								</div>
							</div>

							<div v-else
								class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 dark:border-red-500/30 dark:bg-red-900/10">
								<p class="text-sm font-semibold text-red-900 dark:text-red-100">{{
									t('calendar.deleteLeaveBatchConfirm', { count: deleteLeaveOptions.length }) }}</p>
								<p class="mt-2 text-xs leading-5 text-red-700 dark:text-red-200">{{
									deleteLeaveBatchSummary }}</p>
							</div>
						</div>

						<div class="flex gap-3 justify-end">
							<button @click="cancelDelete"
								class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
								{{ t('common.cancel') }}
							</button>
							<button @click="executeDelete" :disabled="isDeleting"
								class="px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 rounded-lg border border-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition">
								<span v-if="isDeleting" class="flex items-center gap-2">
									<svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
											stroke-width="4">
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
import { useRoute, useRouter } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import CombinedHolidayForm from '@/components/ptb-calendar/CombinedHolidayForm.vue'
import CombinedLeaveForm from '@/components/ptb-calendar/CombinedLeaveForm.vue'
import HolidayDetailsModal from '@/components/ptb-calendar/HolidayDetailsModal.vue'
import HolidayFormModal from '@/components/ptb-calendar/HolidayFormModal.vue'
import LeaveDetailsModal from '@/components/ptb-calendar/LeaveDetailsModal.vue'
import LeaveFormModal from '@/components/ptb-calendar/LeaveFormModal.vue'
import ListView from '@/components/ptb-calendar/ListView.vue'
import { getLeaveBatch } from '@/components/ptb-calendar/leaveSummary'
// Components
import MonthView from '@/components/ptb-calendar/MonthView.vue'
import WeekView from '@/components/ptb-calendar/WeekView.vue'
import YearView from '@/components/ptb-calendar/YearView.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToast } from '@/composables/useToast'
import { STORAGE_KEY_PTB_CALENDAR_VIEW_MODE } from '@/constants/storage'
import { DEBOUNCE_FETCH_MS } from '@/constants/ui'
import { ChevronLeftIcon, ChevronRightIcon } from '@/icons'
import {
	type EmployeeLeave,
	employeeLeaveAPI,
	type Holiday,
	holidayAPI,
} from '@/services/api/holiday'
import { disconnectCalendarWebSocket, useCalendarWebSocket } from '@/services/websocket'
import { useAuthStore } from '@/stores/auth'
import { useEmployeeStore } from '@/stores/employee'
import { extractApiError } from '@/utils/extractApiError'

const authStore = useAuthStore()
const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const employeeStore = useEmployeeStore()
const { showToast } = useToast()
const { confirm: confirmDialog } = useConfirmDialog()

// View modes
const viewModes = computed<Array<{ value: 'week' | 'month' | 'year' | 'list'; label: string }>>(() => [
	{ value: 'week' as const, label: t('calendar.week') },
	{ value: 'month' as const, label: t('calendar.month') },
	{ value: 'year' as const, label: t('calendar.year') },
	{ value: 'list' as const, label: t('calendar.list') },
])

// Load view mode from localStorage or default to 'month'
const savedViewMode = localStorage.getItem(STORAGE_KEY_PTB_CALENDAR_VIEW_MODE) as
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
const showHolidayDetails = ref(false)
const showLeaveDetails = ref(false)
const showCombinedModal = ref(false)
const combinedModalTab = ref<'leave' | 'holiday'>('leave')
const selectedHoliday = ref<Holiday | null>(null)
const selectedLeave = ref<EmployeeLeave | null>(null)
const selectedHolidayDetails = ref<Holiday | null>(null)
const selectedLeaveDetails = ref<EmployeeLeave | null>(null)
const selectedLeaveBatch = ref<EmployeeLeave[]>([])
const selectedDate = ref<string | null>(null)
const selectedDates = ref<string[] | null>(null)

// Delete confirmation modal states
const showDeleteModal = ref(false)
const deleteType = ref<'holiday' | 'leave'>('holiday')
const deleteItemId = ref<number | null>(null)
const deleteItemName = ref<string>('')
const isDeleting = ref(false)
const deleteLeaveBatch = ref<EmployeeLeave[]>([])
const deleteLeaveScope = ref<'selection' | 'batch'>('selection')
const deleteLeaveTargetIds = ref<number[]>([])

// Permissions
const canDelete = computed(() => authStore.hasPermission('calendar', 'delete'))
const canUpdate = computed(() => authStore.hasPermission('calendar', 'update'))
const isPtbAdmin = computed(() => authStore.isPtbAdmin || authStore.isSuperAdmin)
const currentUserId = computed(() => authStore.user?.id ?? null)

const canManageLeave = (leave: EmployeeLeave | null | undefined) => {
	if (!leave) return false
	if (isPtbAdmin.value) return true
	return currentUserId.value !== null && leave.created_by === currentUserId.value
}

const selectedLeaveCanManage = computed(() => canManageLeave(selectedLeave.value ?? selectedLeaveDetails.value))

// Employees for leave form - only enabled employees
const employees = computed(() => employeeStore.employees.filter((e) => e.is_enabled))
const selectedLeaveGroup = computed(() => {
	if (selectedLeaveBatch.value.length > 0) return selectedLeaveBatch.value
	if (!selectedLeaveDetails.value) return []
	return getLeaveBatch(leaves.value, selectedLeaveDetails.value)
})

const getSelectedLeaveBatch = (leave: EmployeeLeave | null) => getLeaveBatch(leaves.value, leave)
const deleteLeaveOptions = computed<EmployeeLeave[]>(() =>
	[...deleteLeaveBatch.value].sort((left, right) => new Date(left.date).getTime() - new Date(right.date).getTime()),
)
const deleteLeaveSelectedIds = computed(() => {
	if (deleteLeaveScope.value === 'batch') {
		return deleteLeaveOptions.value.map((leave) => leave.id)
	}
	return deleteLeaveTargetIds.value
})
const deleteLeaveSelectedCount = computed(() => deleteLeaveSelectedIds.value.length)

const deleteLeaveIntroText = computed(() => {
	if (deleteType.value !== 'leave') return t('calendar.deleteLeaveConfirm')
	if (deleteLeaveOptions.value.length <= 1) return t('calendar.deleteLeaveConfirm')
	return deleteLeaveScope.value === 'batch'
		? t('calendar.deleteLeaveBatchConfirm', { count: deleteLeaveOptions.value.length })
		: deleteLeaveSelectedCount.value > 1
			? t('calendar.deleteLeaveSelectionConfirm', { count: deleteLeaveSelectedCount.value })
			: t('calendar.deleteLeaveSingleHint')
})

const deleteLeaveBatchSummary = computed(() =>
	deleteLeaveOptions.value.map((leave) => formatDeleteLeaveDate(leave.date)).join(', '),
)

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
		const startMonth = t(monthKeys[weekStartDate.value.getMonth()] ?? '')
		const endMonth = t(monthKeys[endDate.getMonth()] ?? '')
		const weekNum = getWeekNumber(weekStartDate.value)
		if (startMonth === endMonth) {
			return `${startMonth} ${weekStartDate.value.getDate()} - ${endDate.getDate()}, ${currentYear.value} (Week ${weekNum})`
		}
		return `${startMonth} ${weekStartDate.value.getDate()} - ${endMonth} ${endDate.getDate()}, ${currentYear.value} (Week ${weekNum})`
	}
	return `${t(monthKeys[currentMonth.value] ?? '')} ${currentYear.value}`
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

const isRecord = (value: unknown): value is Record<string, unknown> =>
	typeof value === 'object' && value !== null

const isEmployeeLeave = (value: unknown): value is EmployeeLeave =>
	isRecord(value) && typeof value.id === 'number' && typeof value.date === 'string'

const normalizeLeaveCollection = (payload: unknown): EmployeeLeave[] => {
	if (Array.isArray(payload)) {
		return payload.filter(isEmployeeLeave)
	}

	if (isRecord(payload) && Array.isArray(payload.results)) {
		return payload.results.filter(isEmployeeLeave)
	}

	if (isEmployeeLeave(payload)) {
		return [payload]
	}

	return []
}

const mergeLeavesById = (baseLeaves: EmployeeLeave[], incomingLeaves: EmployeeLeave[]) => {
	const leaveMap: Record<number, EmployeeLeave> = {}
	for (const leave of baseLeaves) {
		leaveMap[leave.id] = leave
	}
	for (const leave of incomingLeaves) {
		leaveMap[leave.id] = leave
	}
	const mergedLeaves: EmployeeLeave[] = []
	for (const leaveId in leaveMap) {
		const mappedLeave = leaveMap[leaveId]
		if (mappedLeave) {
			mergedLeaves.push(mappedLeave)
		}
	}
	return mergedLeaves.sort((left, right) => {
		const dateDiff = new Date(left.date).getTime() - new Date(right.date).getTime()
		if (dateDiff !== 0) return dateDiff
		return left.id - right.id
	})
}

const removeLeavesByIds = (baseLeaves: EmployeeLeave[], leaveIds: number[]) => {
	if (leaveIds.length === 0) return baseLeaves
	return baseLeaves.filter((leave) => leaveIds.indexOf(leave.id) === -1)
}

const extractDeletedLeaveIds = (payload: unknown): number[] => {
	if (Array.isArray(payload)) {
		const deletedIds: number[] = []
		for (const entry of payload) {
			deletedIds.push(...extractDeletedLeaveIds(entry))
		}
		return deletedIds
	}

	if (!isRecord(payload)) {
		return []
	}

	if (typeof payload.id === 'number') {
		return [payload.id]
	}

	if (Array.isArray(payload.deleted_ids)) {
		return payload.deleted_ids.filter((entry): entry is number => typeof entry === 'number')
	}

	return []
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
		leaves.value = normalizeLeaveCollection(leaveData)
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
	return `${t(dayKeys[date.getDay()] ?? '')}, ${t(monthKeys[date.getMonth()] ?? '')} ${date.getDate()}, ${date.getFullYear()}`
}

const formatDeleteLeaveDate = (dateStr: string): string =>
	new Intl.DateTimeFormat(undefined, {
		weekday: 'short',
		month: 'short',
		day: 'numeric',
		year: 'numeric',
	}).format(new Date(dateStr))

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
		openHolidayDetails(holiday)
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
		// Create holidays for all dates in parallel
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
	agents?: import('@/services/api/holiday').LeaveAgent[]
}) => {
	try {
		const dates = data.dates && data.dates.length > 0 ? data.dates : [data.date]
		await employeeLeaveAPI.createBatch({
			employee: data.employee,
			dates,
			notes: data.notes,
			agents: data.agents,
		})
		closeCombinedModal()
		await fetchData()
	} catch (err) {
		console.error('Failed to save leave:', err)
		showToast(extractApiError(err, 'Failed to save leave'), 'error', 5000)
	}
}

// Holiday form
const openHolidayForm = () => {
	selectedHoliday.value = null
	showHolidayForm.value = true
}

const openHolidayDetails = (holiday: Holiday) => {
	selectedHolidayDetails.value = holiday
	showHolidayDetails.value = true
}

const closeHolidayDetails = () => {
	showHolidayDetails.value = false
	selectedHolidayDetails.value = null
}

const editHolidayFromDetails = () => {
	if (!selectedHolidayDetails.value) return
	const holiday = selectedHolidayDetails.value
	closeHolidayDetails()
	editHoliday(holiday)
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
	if (!canManageLeave(leave)) {
		showToast(t('calendar.leavePermissionDenied'), 'error', 5000)
		return
	}
	deleteType.value = 'leave'
	deleteItemId.value = id
	deleteItemName.value = leave?.employee_name || ''
	deleteLeaveBatch.value = leave ? getSelectedLeaveBatch(leave) : []
	deleteLeaveScope.value = 'selection'
	deleteLeaveTargetIds.value = leave?.id ? [leave.id] : [id]
	showDeleteModal.value = true
}

const cancelDelete = () => {
	showDeleteModal.value = false
	deleteItemId.value = null
	deleteItemName.value = ''
	deleteLeaveBatch.value = []
	deleteLeaveScope.value = 'selection'
	deleteLeaveTargetIds.value = []
}

const executeDelete = async () => {
	if (!deleteItemId.value) return

	isDeleting.value = true
	try {
		if (deleteType.value === 'holiday') {
			await holidayAPI.delete(deleteItemId.value)
			closeHolidayForm()
		} else {
			if (deleteLeaveBatch.value.some((leave) => !canManageLeave(leave))) {
				showToast(t('calendar.leavePermissionDenied'), 'error', 5000)
				return
			}
			if (deleteLeaveScope.value === 'batch' && deleteLeaveOptions.value.length > 1) {
				await employeeLeaveAPI.deleteBatch({
					leave_ids: deleteLeaveOptions.value.map((leave) => leave.id),
				})
			} else {
				const selectedIds = deleteLeaveSelectedIds.value
				if (selectedIds.length > 1) {
					await employeeLeaveAPI.deleteBatch({ leave_ids: selectedIds })
				} else {
					const leaveIdToDelete = selectedIds[0] ?? deleteItemId.value
					await employeeLeaveAPI.delete(leaveIdToDelete)
				}
			}
			closeLeaveForm()
			closeLeaveDetails()
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

const openLeaveDetails = (leave: EmployeeLeave, leaveBatch = getSelectedLeaveBatch(leave)) => {
	selectedLeaveDetails.value = leave
	selectedLeaveBatch.value = leaveBatch
	showLeaveDetails.value = true
}

const clearLeaveBatchQuery = async () => {
	if (typeof route.query.leaveBatch !== 'string') return
	const nextQuery = { ...route.query }
	delete nextQuery.leaveBatch
	await router.replace({ query: nextQuery })
}

const closeLeaveDetails = () => {
	showLeaveDetails.value = false
	selectedLeaveDetails.value = null
	selectedLeaveBatch.value = []
	void clearLeaveBatchQuery()
}

const editLeaveFromDetails = () => {
	if (!selectedLeaveDetails.value) return
	const leave = selectedLeaveDetails.value
	closeLeaveDetails()
	editLeave(leave)
}

const editLeave = (leave: EmployeeLeave) => {
	if (!canManageLeave(leave)) {
		showToast(t('calendar.leavePermissionDenied'), 'error', 5000)
		return
	}
	const leaveBatch = getSelectedLeaveBatch(leave)
	selectedLeave.value = leave
	selectedLeaveBatch.value = leaveBatch
	selectedDates.value = leaveBatch.map((entry) => entry.date)
	selectedDate.value = selectedDates.value[0] ?? leave.date
	showLeaveForm.value = true
}

const closeLeaveForm = () => {
	showLeaveForm.value = false
	selectedLeave.value = null
	selectedLeaveBatch.value = []
	selectedDate.value = null
	selectedDates.value = null
}

const saveLeave = async (data: {
	employee: number
	date: string
	dates?: string[]
	notes?: string
	agents?: import('@/services/api/holiday').LeaveAgent[]
}) => {
	try {
		if (selectedLeave.value) {
			if (!canManageLeave(selectedLeave.value)) {
				showToast(t('calendar.leavePermissionDenied'), 'error', 5000)
				return
			}
			const leaveIds = selectedLeaveBatch.value.length > 0
				? selectedLeaveBatch.value.map((leave) => leave.id)
				: [selectedLeave.value.id]
			const dates = data.dates && data.dates.length > 0 ? data.dates : [data.date]
			await employeeLeaveAPI.updateBatch({
				leave_ids: leaveIds,
				employee: data.employee,
				dates,
				notes: data.notes,
				agents: data.agents,
			})
		} else {
			const dates = data.dates && data.dates.length > 0 ? data.dates : [data.date]
			await employeeLeaveAPI.createBatch({
				employee: data.employee,
				dates,
				notes: data.notes,
				agents: data.agents,
			})
		}
		closeLeaveForm()
		await fetchData()
	} catch (err) {
		console.error('Failed to save leave:', err)
		showToast(extractApiError(err, 'Failed to save leave'), 'error', 5000)
	}
}

// Handle leave drag and drop
const handleLeaveMove = async (leaveId: number, newDate: string) => {
	const leave = leaves.value.find((l) => l.id === leaveId)
	if (!leave) return
	if (!canManageLeave(leave)) {
		showToast(t('calendar.leavePermissionDenied'), 'error', 5000)
		return
	}

	const confirmed = await confirmDialog({
		title: t('calendar.moveLeaveTitle'),
		message: t('calendar.moveLeaveMessage', {
			employee: leave.employee_name,
			from: formatDeleteLeaveDate(leave.date),
			to: formatDeleteLeaveDate(newDate),
		}),
		type: 'warning',
		confirmLabel: t('calendar.moveLeaveConfirmAction'),
		cancelLabel: t('common.cancel'),
	})
	if (!confirmed) return

	try {
		await employeeLeaveAPI.update(leaveId, {
			employee: leave.employee,
			date: newDate,
			notes: leave.notes,
		})
		await fetchData()
	} catch (err) {
		console.error('Failed to move leave:', err)
		showToast(extractApiError(err, 'Failed to move leave'), 'error', 5000)
	}
}

let batchRouteLookupPromise: Promise<void> | null = null

const syncLeaveDetailsFromRoute = async () => {
	const leaveBatchKey = typeof route.query.leaveBatch === 'string' ? route.query.leaveBatch.trim() : ''
	if (!leaveBatchKey || showLeaveDetails.value || showLeaveForm.value) {
		return
	}

	const leave = leaves.value.find((entry) => entry.batch_key === leaveBatchKey)
	if (leave) {
		openLeaveDetails(leave)
		return
	}

	if (batchRouteLookupPromise) {
		return
	}

	batchRouteLookupPromise = employeeLeaveAPI
		.list({ batch_key: leaveBatchKey })
		.then((leaveBatch) => {
			if (leaveBatch.length > 0) {
				openLeaveDetails(leaveBatch[0]!, leaveBatch)
			}
		})
		.catch((error) => {
			console.error('Failed to resolve leave batch from route:', error)
			showToast(extractApiError(error, 'Failed to open leave details from email link'), 'error', 5000)
		})
		.finally(() => {
			batchRouteLookupPromise = null
		})

	await batchRouteLookupPromise
}

// Watchers — debounce to avoid double-fires on month boundary
let fetchDebounceTimer: ReturnType<typeof setTimeout> | null = null
watch([viewMode, currentYear, currentMonth, currentWeekStart], () => {
	if (fetchDebounceTimer) clearTimeout(fetchDebounceTimer)
	fetchDebounceTimer = setTimeout(() => {
		void fetchData()
	}, DEBOUNCE_FETCH_MS)
})

// Save view mode to localStorage when it changes
watch(viewMode, (newMode) => {
	localStorage.setItem(STORAGE_KEY_PTB_CALENDAR_VIEW_MODE, newMode)
})

watch([() => route.query.leaveBatch, leaves], () => {
	void syncLeaveDetailsFromRoute()
}, { immediate: true })

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
			if (action === 'deleted') {
				leaves.value = removeLeavesByIds(leaves.value, extractDeletedLeaveIds(data))
				return
			}

			const incomingLeaves = normalizeLeaveCollection(data)
			if (incomingLeaves.length === 0) {
				console.warn('[PTB Calendar] Ignoring unexpected leave realtime payload:', data)
				return
			}

			leaves.value = mergeLeavesById(leaves.value, incomingLeaves)
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
