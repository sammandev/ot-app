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
                <div v-if="selectedAgents.length > 0 || customAgentNames.length > 0" class="flex flex-wrap gap-2">
                    <span v-for="agent in selectedAgents" :key="agent.id"
                        class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 text-sm rounded">
                        {{ agent.name }}
                        <button type="button" @click="removeAgent(agent.id)"
                            class="hover:text-blue-900 dark:hover:text-blue-100">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </span>
                    <!-- Custom agent name tags -->
                    <span v-for="(name, index) in customAgentNames" :key="'custom-' + index"
                        class="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 text-sm rounded">
                        {{ name }}
                        <button type="button" @click="removeCustomAgent(index)"
                            class="hover:text-purple-900 dark:hover:text-purple-100">
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
                    <div v-if="showAgentDropdown && filteredAgentEmployees.length > 0"
                        class="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        <button v-for="emp in filteredAgentEmployees" :key="emp.id" type="button" 
                            @mousedown.prevent="addAgent(emp)"
                            class="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                            <div class="font-medium text-gray-900 dark:text-white">{{ emp.name }}</div>
                            <div class="text-xs text-gray-500 dark:text-gray-400">{{ emp.emp_id }}</div>
                        </button>
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
            <button type="submit" :disabled="!selectedEmployee || selectedDates.length === 0" :class="[
                'px-4 py-2 text-sm font-medium rounded-lg border transition',
                selectedEmployee && selectedDates.length > 0
                    ? 'text-emerald-700 dark:text-emerald-300 border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-900/20'
                    : 'text-gray-400 border-gray-300 dark:border-gray-600 cursor-not-allowed'
            ]">
                {{ t('calendar.leaveForm.submitLeave') }}
            </button>
        </div>
    </form>
</template>

<script setup lang="ts">
import flatpickr from 'flatpickr'
import type { Instance } from 'flatpickr/dist/types/instance'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { attachMonthScrollStandalone } from '@/composables/useFlatpickrScroll'

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
			agents?: number[]
			agent_names?: string
		},
	): void
	(e: 'cancel'): void
}>()

const searchQuery = ref('')
const showDropdown = ref(false)
const selectedEmployee = ref<Employee | null>(null)
const employeeDropdownRef = ref<HTMLElement | null>(null)

const agentSearchQuery = ref('')
const showAgentDropdown = ref(false)
const selectedAgents = ref<Employee[]>([])
const agentDropdownRef = ref<HTMLElement | null>(null)
const customAgentNames = ref<string[]>([])

const dateInput = ref<HTMLInputElement | null>(null)
let flatpickrInstance: Instance | null = null
const selectedDates = ref<string[]>([])

const form = ref({
	notes: '',
})

// Computed display for date(s)
const dateDisplay = computed(() => {
	if (selectedDates.value.length === 0) return ''
	const firstDate = selectedDates.value[0]
	if (selectedDates.value.length === 1) return formatDateDisplay(firstDate ?? '')
	const lastDate = selectedDates.value[selectedDates.value.length - 1]
	return `${firstDate ?? ''} to ${lastDate ?? ''}`
})

// Initialize with initial date or dates
watch(
	() => [props.initialDate, props.initialDates],
	() => {
		const today = new Date().toISOString().split('T')[0] ?? ''
		if (props.initialDates && props.initialDates.length > 0) {
			selectedDates.value = [...props.initialDates]
		} else {
			selectedDates.value = props.initialDate ? [props.initialDate] : [today]
		}
		if (flatpickrInstance) {
			flatpickrInstance.setDate(selectedDates.value, false)
		}
	},
	{ immediate: true },
)

// Filter employees based on search query - excludes selected agents
const filteredEmployees = computed(() => {
	const excludedIds = new Set(selectedAgents.value.map((a) => a.id))
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

// Filter employees for agent selection (exclude already selected and main employee)
const filteredAgentEmployees = computed(() => {
	const selectedIds = new Set([
		...(selectedEmployee.value ? [selectedEmployee.value.id] : []),
		...selectedAgents.value.map((a) => a.id),
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

// Handle blur for employee dropdown - auto close
const handleEmployeeBlur = () => {
	setTimeout(() => {
		showDropdown.value = false
	}, 150)
}

// Handle blur for agent dropdown - auto close
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
	if (!selectedAgents.value.find((a) => a.id === emp.id)) {
		selectedAgents.value.push(emp)
	}
	agentSearchQuery.value = ''
	showAgentDropdown.value = false
}

const removeAgent = (id: number) => {
	selectedAgents.value = selectedAgents.value.filter((a) => a.id !== id)
}

// Handle Enter key for adding custom agent names
const handleAgentEnter = () => {
	const name = agentSearchQuery.value.trim()
	if (name && !customAgentNames.value.includes(name)) {
		// Check if it matches an existing employee first
		const matchingEmployee = props.employees.find((e) => e.name.toLowerCase() === name.toLowerCase())
		if (matchingEmployee && !selectedAgents.value.find((a) => a.id === matchingEmployee.id)) {
			// If it's an exact match to an employee name, add them as a selected agent
			selectedAgents.value.push(matchingEmployee)
		} else if (!matchingEmployee) {
			// Otherwise add as a custom name
			customAgentNames.value.push(name)
		}
	}
	agentSearchQuery.value = ''
	showAgentDropdown.value = false
}

const removeCustomAgent = (index: number) => {
	customAgentNames.value.splice(index, 1)
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

const handleSubmit = () => {
	if (!selectedEmployee.value || selectedDates.value.length === 0) return
	const primaryDate = selectedDates.value[0]
	if (!primaryDate) return

	emit('save', {
		employee: selectedEmployee.value.id,
		date: primaryDate, // Primary date for single-date compatibility
		dates: selectedDates.value, // All selected dates
		notes: form.value.notes || undefined,
		agents: selectedAgents.value.map((a) => a.id),
		agent_names: customAgentNames.value.length > 0 ? customAgentNames.value.join(', ') : undefined,
	})
}

// Helper function to format date to YYYY-MM-DD
const formatDateStr = (date: Date): string => {
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

// Helper function to generate all dates between start and end (inclusive)
const getDateRange = (startDate: Date, endDate: Date): string[] => {
	const dates: string[] = []
	const current = new Date(startDate)
	current.setHours(0, 0, 0, 0)
	const end = new Date(endDate)
	end.setHours(0, 0, 0, 0)

	while (current <= end) {
		dates.push(formatDateStr(current))
		current.setDate(current.getDate() + 1)
	}

	return dates
}

// Initialize flatpickr with range mode
onMounted(async () => {
	await nextTick()
	if (dateInput.value) {
		flatpickrInstance = flatpickr(dateInput.value, {
			mode: 'range',
			dateFormat: 'Y-m-d',
			defaultDate: selectedDates.value.length > 0 ? selectedDates.value : undefined,
			onChange: (dates) => {
				if (dates.length === 2) {
					// Range selected - generate all dates in between
					selectedDates.value = getDateRange(dates[0]!, dates[1]!)
				} else if (dates.length === 1) {
					// Single date selected
					selectedDates.value = [formatDateStr(dates[0]!)]
				} else {
					selectedDates.value = []
				}
			},
			onReady: (_selectedDates, _dateStr, instance) => {
				attachMonthScrollStandalone(instance)
			},
		})
	}
})

onUnmounted(() => {
	if (flatpickrInstance) {
		flatpickrInstance.destroy()
		flatpickrInstance = null
	}
})
</script>
