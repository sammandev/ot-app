<template>
    <form @submit.prevent="handleSubmit" class="p-4 space-y-4">
        <!-- Employee Selection -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('calendar.leaveForm.employee') }} *
            </label>
            <div class="relative" ref="employeeDropdownRef">
                <input type="text" v-model="searchQuery" @focus="showDropdown = true" 
                    @blur="handleEmployeeBlur"
                    @input="showDropdown = true"
                    :placeholder="selectedEmployee ? '' : t('calendar.leaveForm.searchEmployee')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500" />

                <!-- Selected Employee Display -->
                <div v-if="selectedEmployee && !showDropdown && !searchQuery"
                    class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                    <span class="text-gray-900 dark:text-white">
                        {{ selectedEmployee.name }}
                    </span>
                </div>

                <!-- Dropdown -->
                <div v-if="showDropdown && filteredEmployees.length > 0"
                    class="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    <button v-for="emp in filteredEmployees" :key="emp.id" type="button" 
                        @mousedown.prevent="selectEmployee(emp)"
                        class="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                        <div class="font-medium text-gray-900 dark:text-white">{{ emp.name }}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">{{ emp.emp_id }}</div>
                    </button>
                </div>

                <!-- No results -->
                <div v-if="showDropdown && searchQuery && filteredEmployees.length === 0"
                    class="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3 text-center text-gray-500 dark:text-gray-400 text-sm">
                    {{ t('calendar.leaveForm.noEmployeesFound') }}
                </div>
            </div>
        </div>

        <!-- Date Range -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('calendar.leaveForm.dates') }} *
            </label>
            <div class="relative">
                <input ref="dateInput" type="text" v-model="dateDisplay" required readonly
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 cursor-pointer"
                    :placeholder="t('calendar.leaveForm.selectDates')" />
            </div>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {{ t('calendar.leaveForm.dateRangeHint') }}
            </p>
        </div>

        <!-- Agent Selection (Multiple) -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('calendar.leaveForm.agents') }} <span class="text-gray-400">{{ t('calendar.leaveForm.agentsCover') }}</span>
            </label>
            <div class="space-y-2">
                <!-- Selected Agents -->
				<div v-if="selectedAgents.length > 0" class="flex flex-wrap gap-2">
					<span v-for="agent in selectedAgents" :key="getLeaveAgentKey(agent)"
						:class="[
							'inline-flex items-center gap-1 px-2 py-1 text-sm rounded',
							isExternalAgent(agent)
								? 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300'
								: isManualAgent(agent)
									? 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300'
									: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'
						]">
						{{ getLeaveAgentDisplayName(agent) }}
						<span v-if="isExternalAgent(agent)" class="rounded-full bg-emerald-200 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-800 dark:bg-emerald-400/20 dark:text-emerald-200">
							{{ t('calendar.leaveForm.externalAgentBadge') }}
						</span>
						<button type="button" @click="removeAgent(agent)"
							:class="isExternalAgent(agent)
								? 'hover:text-emerald-900 dark:hover:text-emerald-100'
								: isManualAgent(agent)
									? 'hover:text-purple-900 dark:hover:text-purple-100'
									: 'hover:text-blue-900 dark:hover:text-blue-100'">
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
									d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					</span>
                </div>

                <!-- Agent Search -->
                <div class="relative" ref="agentDropdownRef">
                    <input type="text" v-model="agentSearchQuery" @focus="showAgentDropdown = true"
                        @blur="handleAgentBlur"
                        @input="showAgentDropdown = true"
                        @keydown.enter.prevent="handleAgentEnter"
                        :placeholder="t('calendar.leaveForm.searchAgents')"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500" />

                    <!-- Agent Dropdown -->
					<div v-if="showAgentDropdown && (filteredAgentEmployees.length > 0 || filteredExternalAgents.length > 0 || isExternalAgentLookupLoading || externalLookupMessage)"
                        class="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
						<div v-if="filteredAgentEmployees.length > 0" class="border-b border-gray-100 px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500 dark:border-gray-700 dark:text-gray-400">
							{{ t('calendar.leaveForm.localAgentSection') }}
						</div>
                        <button v-for="emp in filteredAgentEmployees" :key="emp.id" type="button" 
                            @mousedown.prevent="addAgent(emp)"
                            class="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                            <div class="font-medium text-gray-900 dark:text-white">{{ emp.name }}</div>
                            <div class="text-xs text-gray-500 dark:text-gray-400">{{ emp.emp_id }}</div>
                        </button>
						<div v-if="filteredExternalAgents.length > 0" class="border-b border-t border-gray-100 px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-600 dark:border-gray-700 dark:text-emerald-300">
							{{ t('calendar.leaveForm.externalAgentSection') }}
						</div>
						<button v-for="agent in filteredExternalAgents" :key="agent.email || agent.worker_id" type="button"
							@mousedown.prevent="addExternalAgent(agent)"
							class="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition">
							<div class="flex items-center gap-2">
								<div class="font-medium text-gray-900 dark:text-white">{{ getExternalAgentDisplayName(agent) }}</div>
								<span class="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300">
									{{ t('calendar.leaveForm.externalAgentBadge') }}
								</span>
							</div>
							<div class="text-xs text-gray-500 dark:text-gray-400">{{ [agent.worker_id, agent.site].filter(Boolean).join(' • ') }}</div>
							<div class="text-xs text-gray-500 dark:text-gray-400">{{ agent.email }}</div>
						</button>
						<div v-if="isExternalAgentLookupLoading" class="px-3 py-2 text-xs text-gray-500 dark:text-gray-400">
							{{ t('calendar.leaveForm.externalLookupLoading') }}
						</div>
						<div v-else-if="externalLookupMessage" class="px-3 py-2 text-xs text-gray-500 dark:text-gray-400">
							{{ externalLookupMessage }}
						</div>
                    </div>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ t('calendar.leaveForm.agentHint') }}
                </p>
            </div>
        </div>

        <!-- Notes -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('calendar.leaveForm.notes') }} <span class="text-gray-400">{{ t('calendar.leaveForm.optional') }}</span>
            </label>
            <textarea v-model="form.notes" rows="2"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 resize-none"
                :placeholder="t('calendar.leaveForm.notesPlaceholder')"></textarea>
        </div>

        <!-- Footer -->
		<div class="flex items-center justify-end gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <button type="button" @click="$emit('cancel')"
                class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                {{ t('calendar.leaveForm.cancel') }}
            </button>
			<button type="button" @click="handleSubmit" :disabled="!selectedEmployee || selectedDates.length === 0" :class="[
                'px-4 py-2 text-sm font-medium rounded-lg border transition',
                selectedEmployee && selectedDates.length > 0
                    ? 'text-emerald-700 dark:text-emerald-300 border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-900/20'
                    : 'text-gray-400 border-gray-300 dark:border-gray-600 cursor-not-allowed'
            ]">
                {{ t('calendar.leaveForm.submitLeave') }}
            </button>
        </div>

		<LeaveSubmitConfirmModal
			:visible="showConfirmModal"
			mode="create"
			:summary="confirmationSummary"
			@cancel="showConfirmModal = false"
			@confirm="confirmSubmit"
		/>
    </form>
</template>

<script setup lang="ts">
import flatpickr from 'flatpickr'
import type { Instance } from 'flatpickr/dist/types/instance'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDebounce } from '@/composables/useDebounce'
import { attachMonthScrollStandalone } from '@/composables/useFlatpickrScroll'
import {
	employeeLeaveAPI,
	type EmployeeLeaveAgent,
	type ExternalLeaveAgent,
	type ExternalLookupLeaveAgent,
	type LeaveAgent,
} from '@/services/api/holiday'
import { extractApiError } from '@/utils/extractApiError'
import { attachLeaveDateDragSelection } from './leaveDateDragSelection'
import LeaveSubmitConfirmModal from './LeaveSubmitConfirmModal.vue'

const { t } = useI18n()

interface Employee {
	id: number
	name: string
	emp_id: string
	is_enabled?: boolean
}

interface Props {
	initialDate?: string | null
	initialDates?: string[] | null
	employees: Employee[]
}

const props = withDefaults(defineProps<Props>(), {
	initialDate: null,
	initialDates: null,
})

const emit = defineEmits<{
	(
		e: 'save',
		data: {
			employee: number
			date: string
			dates?: string[]
			notes?: string
			agents?: LeaveAgent[]
		},
	): void
	(e: 'cancel'): void
}>()

const searchQuery = ref('')
const showDropdown = ref(false)
const selectedEmployee = ref<Employee | null>(null)
const employeeDropdownRef = ref<HTMLElement | null>(null)

const agentSearchQuery = ref('')
const debouncedAgentSearchQuery = useDebounce(agentSearchQuery, 300)
const showAgentDropdown = ref(false)
const selectedAgents = ref<LeaveAgent[]>([])
const agentDropdownRef = ref<HTMLElement | null>(null)
const externalAgentResults = ref<ExternalLookupLeaveAgent[]>([])
const isExternalAgentLookupLoading = ref(false)
const externalLookupMessage = ref('')
const externalLookupUnsupported = ref(false)
let externalAgentLookupController: AbortController | null = null

const dateInput = ref<HTMLInputElement | null>(null)
let flatpickrInstance: Instance | null = null
let detachDragSelection: (() => void) | null = null
const selectedDates = ref<string[]>([])
const showConfirmModal = ref(false)

const form = ref({
	notes: '',
})

const isEmployeeAgent = (agent: LeaveAgent): agent is EmployeeLeaveAgent => agent.type === 'employee'
const isExternalAgent = (agent: LeaveAgent): agent is ExternalLeaveAgent => agent.type === 'external'
const isManualAgent = (agent: LeaveAgent): agent is Extract<LeaveAgent, { type: 'manual' }> => agent.type === 'manual'

const normalizeManualAgentName = (value: string): string => value.trim().replace(/\s+/g, ' ')

const getExternalAgentDisplayName = (agent: ExternalLookupLeaveAgent | ExternalLeaveAgent): string =>
	agent.username?.trim() || agent.email?.trim() || agent.worker_id?.trim() || '-'

const getLeaveAgentDisplayName = (agent: LeaveAgent): string =>
	isEmployeeAgent(agent)
		? agent.name
		: isExternalAgent(agent)
			? getExternalAgentDisplayName(agent)
			: agent.name

const getLeaveAgentKey = (agent: LeaveAgent): string => {
	if (isEmployeeAgent(agent)) {
		return `employee:${agent.employee_id}`
	}
	if (isExternalAgent(agent)) {
		return `external:${(agent.worker_id || '').trim().toLowerCase()}|${agent.email.trim().toLowerCase()}`
	}
	return `manual:${normalizeManualAgentName(agent.name).toLowerCase()}`
}

const toEmployeeAgent = (employee: Employee): EmployeeLeaveAgent => ({
	type: 'employee',
	employee_id: employee.id,
	name: employee.name,
	emp_id: employee.emp_id,
})

const toExternalAgent = (agent: ExternalLookupLeaveAgent | ExternalLeaveAgent): ExternalLeaveAgent => ({
	type: 'external',
	username: agent.username?.trim() || agent.email?.trim() || agent.worker_id?.trim() || '-',
	email: agent.email.trim().toLowerCase(),
	worker_id: agent.worker_id?.trim() || '',
	site: agent.site ?? null,
	source: 'external_lookup',
})

const confirmationSummary = computed(() => ({
	employeeName: selectedEmployee.value?.name ?? '-',
	employeeId: selectedEmployee.value?.emp_id,
	dates: [...selectedDates.value],
	agents: selectedAgents.value.map((agent) => getLeaveAgentDisplayName(agent)),
	notes: form.value.notes,
}))

const sortDateStrings = (dates: string[]) => [...dates].sort((left, right) => new Date(left).getTime() - new Date(right).getTime())

const formatDateChip = (dateStr: string): string => {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return date.toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
	})
}

const dateDisplay = computed(() => {
	if (selectedDates.value.length === 0) return ''
	if (selectedDates.value.length === 1) return formatDateDisplay(selectedDates.value[0] ?? '')
	const previewDates = selectedDates.value.slice(0, 3).map((date) => formatDateChip(date))
	const remainingCount = selectedDates.value.length - previewDates.length
	return remainingCount > 0
		? `${selectedDates.value.length} dates selected: ${previewDates.join(', ')} +${remainingCount} more`
		: previewDates.join(', ')
})

watch(
	() => [props.initialDate, props.initialDates],
	() => {
		const today = new Date().toISOString().split('T')[0] ?? ''
		showConfirmModal.value = false
		selectedAgents.value = []
		externalAgentResults.value = []
		externalLookupMessage.value = ''
		externalLookupUnsupported.value = false
		if (props.initialDates && props.initialDates.length > 0) {
			selectedDates.value = sortDateStrings([...props.initialDates])
		} else {
			selectedDates.value = props.initialDate ? [props.initialDate] : [today]
		}
		if (flatpickrInstance) {
			flatpickrInstance.setDate(sortDateStrings(selectedDates.value), false)
		}
	},
	{ immediate: true },
)

const filteredEmployees = computed(() => {
	const excludedIds = new Set(
		selectedAgents.value.filter(isEmployeeAgent).map((agent) => agent.employee_id),
	)
	const list = props.employees.filter((emp) => !excludedIds.has(emp.id))

	if (!searchQuery.value) {
		return list.slice(0, 10)
	}
	const query = searchQuery.value.toLowerCase()
	return list
		.filter(
			(emp) => emp.name.toLowerCase().includes(query) || emp.emp_id.toLowerCase().includes(query),
		)
		.slice(0, 10)
})

const filteredAgentEmployees = computed(() => {
	const selectedIds = new Set([
		...(selectedEmployee.value ? [selectedEmployee.value.id] : []),
		...selectedAgents.value.filter(isEmployeeAgent).map((agent) => agent.employee_id),
	])

	let list = props.employees.filter((emp) => !selectedIds.has(emp.id))

	if (agentSearchQuery.value) {
		const query = agentSearchQuery.value.toLowerCase()
		list = list.filter(
			(emp) => emp.name.toLowerCase().includes(query) || emp.emp_id.toLowerCase().includes(query),
		)
	}

	return list.slice(0, 10)
})

const filteredExternalAgents = computed(() => {
	const selectedExternalKeys = new Set(
		selectedAgents.value
			.filter(isExternalAgent)
			.map((agent) => `${(agent.worker_id || '').trim().toLowerCase()}|${agent.email.trim().toLowerCase()}`),
	)
	const localEmployeeWorkerIds = new Set(
		props.employees
			.map((employee) => employee.emp_id?.trim().toLowerCase())
			.filter((workerId): workerId is string => Boolean(workerId)),
	)

	return externalAgentResults.value
		.filter(
			(agent) =>
				!selectedExternalKeys.has(
					`${(agent.worker_id || '').trim().toLowerCase()}|${agent.email.trim().toLowerCase()}`,
				),
		)
		.filter((agent) => !localEmployeeWorkerIds.has((agent.worker_id || '').trim().toLowerCase()))
		.slice(0, 10)
})

const handleEmployeeBlur = () => {
	setTimeout(() => {
		showDropdown.value = false
	}, 150)
}

const handleAgentBlur = () => {
	setTimeout(() => {
		showAgentDropdown.value = false
	}, 150)
}

const selectEmployee = (emp: Employee) => {
	selectedEmployee.value = emp
	searchQuery.value = ''
	showDropdown.value = false
}

const addAgent = (emp: Employee) => {
	if (!selectedAgents.value.some((agent) => isEmployeeAgent(agent) && agent.employee_id === emp.id)) {
		selectedAgents.value.push(toEmployeeAgent(emp))
	}
	agentSearchQuery.value = ''
	showAgentDropdown.value = false
}

const addExternalAgent = (agent: ExternalLookupLeaveAgent | ExternalLeaveAgent) => {
	const normalizedAgent = toExternalAgent(agent)
	if (!selectedAgents.value.some((entry) => isExternalAgent(entry) && getLeaveAgentKey(entry) === getLeaveAgentKey(normalizedAgent))) {
		selectedAgents.value.push(normalizedAgent)
	}
	agentSearchQuery.value = ''
	showAgentDropdown.value = false
}

const removeAgent = (agentToRemove: LeaveAgent) => {
	const agentKey = getLeaveAgentKey(agentToRemove)
	selectedAgents.value = selectedAgents.value.filter((agent) => getLeaveAgentKey(agent) !== agentKey)
}

const handleAgentEnter = () => {
	const name = normalizeManualAgentName(agentSearchQuery.value)
	if (name) {
		const matchingEmployee = props.employees.find((employee) => employee.name.toLowerCase() === name.toLowerCase())
		const matchingExternalAgent = filteredExternalAgents.value.find(
			(agent) =>
				getExternalAgentDisplayName(agent).toLowerCase() === name.toLowerCase() ||
				agent.email.toLowerCase() === name.toLowerCase() ||
				agent.worker_id.toLowerCase() === name.toLowerCase(),
		)
		if (matchingEmployee) {
			addAgent(matchingEmployee)
		} else if (matchingExternalAgent) {
			addExternalAgent(matchingExternalAgent)
			return
		} else if (!selectedAgents.value.some((agent) => isManualAgent(agent) && normalizeManualAgentName(agent.name).toLowerCase() === name.toLowerCase())) {
			selectedAgents.value.push({ type: 'manual', name })
		}
	}
	agentSearchQuery.value = ''
	showAgentDropdown.value = false
}

const formatDateDisplay = (dateStr: string): string => {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
	const monthNames = [
		'Jan',
		'Feb',
		'Mar',
		'Apr',
		'May',
		'Jun',
		'Jul',
		'Aug',
		'Sep',
		'Oct',
		'Nov',
		'Dec',
	]
	return `${dayNames[date.getDay()]}, ${monthNames[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`
}

const buildPayloadAgents = (): LeaveAgent[] => {
	return selectedAgents.value.map((agent): LeaveAgent => {
		if (isEmployeeAgent(agent)) {
			return {
				type: 'employee',
				employee_id: agent.employee_id,
				name: agent.name,
				emp_id: agent.emp_id,
				dept_code: agent.dept_code,
			}
		}

		if (isExternalAgent(agent)) {
			return {
				type: 'external',
				username: agent.username,
				email: agent.email,
				worker_id: agent.worker_id,
				site: agent.site,
				source: 'external_lookup',
			}
		}

		return {
			type: 'manual',
			name: agent.name,
		}
	})
}

const handleSubmit = () => {
	if (!selectedEmployee.value || selectedDates.value.length === 0) return
	showConfirmModal.value = true
}

const confirmSubmit = () => {
	if (!selectedEmployee.value || selectedDates.value.length === 0) return
	const primaryDate = selectedDates.value[0]
	if (!primaryDate) return

	showConfirmModal.value = false
	emit('save', {
		employee: selectedEmployee.value.id,
		date: primaryDate,
		dates: selectedDates.value,
		notes: form.value.notes || undefined,
		agents: buildPayloadAgents(),
	})
}

watch(debouncedAgentSearchQuery, async (query) => {
	const keyword = query.trim()
	if (externalAgentLookupController) {
		externalAgentLookupController.abort()
		externalAgentLookupController = null
	}

	if (keyword.length < 2) {
		externalAgentResults.value = []
		externalLookupMessage.value = ''
		isExternalAgentLookupLoading.value = false
		return
	}

	if (externalLookupUnsupported.value) {
		externalAgentResults.value = []
		externalLookupMessage.value = t('calendar.leaveForm.externalLookupUnavailable')
		return
	}

	const controller = new AbortController()
	externalAgentLookupController = controller
	isExternalAgentLookupLoading.value = true
	externalLookupMessage.value = ''

	try {
		const results = await employeeLeaveAPI.lookupAgents(keyword, { signal: controller.signal })
		if (externalAgentLookupController !== controller) return
		externalAgentResults.value = results
		externalLookupMessage.value = results.length === 0 ? t('calendar.leaveForm.noExternalAgentsFound') : ''
	} catch (error) {
		if (controller.signal.aborted) return
		externalAgentResults.value = []
		const code = (error as { response?: { data?: { code?: string } } }).response?.data?.code
		if (code === 'external_lookup_requires_external_session' || code === 'external_lookup_session_unavailable') {
			externalLookupUnsupported.value = true
			externalLookupMessage.value = t('calendar.leaveForm.externalLookupUnavailable')
		} else if (code === 'external_lookup_auth_failed') {
			externalLookupMessage.value = t('calendar.leaveForm.externalLookupExpired')
		} else {
			externalLookupMessage.value = extractApiError(error, t('calendar.leaveForm.externalLookupFailed'))
		}
	} finally {
		if (externalAgentLookupController === controller) {
			externalAgentLookupController = null
			isExternalAgentLookupLoading.value = false
		}
	}
})

const formatDateStr = (date: Date): string => {
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

onMounted(async () => {
	await nextTick()
	if (dateInput.value) {
		flatpickrInstance = flatpickr(dateInput.value, {
			mode: 'multiple',
			dateFormat: 'Y-m-d',
			conjunction: ', ',
			defaultDate: selectedDates.value.length > 0 ? selectedDates.value : undefined,
			onChange: (dates) => {
				selectedDates.value = sortDateStrings(Array.from(new Set(dates.map((date) => formatDateStr(date)))))
			},
			onReady: (_selectedDates, _dateStr, instance) => {
				attachMonthScrollStandalone(instance)
				detachDragSelection?.()
				detachDragSelection = attachLeaveDateDragSelection(instance, {
					getSelectedDates: () => selectedDates.value,
					setSelectedDates: (dates) => {
						selectedDates.value = sortDateStrings(dates)
					},
				})
			},
			disableMobile: true,
		})
	}
})

onUnmounted(() => {
	if (externalAgentLookupController) {
		externalAgentLookupController.abort()
		externalAgentLookupController = null
	}
	detachDragSelection?.()
	detachDragSelection = null
	if (flatpickrInstance) {
		flatpickrInstance.destroy()
		flatpickrInstance = null
	}
})
</script>
