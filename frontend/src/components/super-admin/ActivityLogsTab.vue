<template>
    <div class="space-y-6">
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <!-- Header -->
            <div class="flex items-center gap-4 border-b border-gray-200 px-6 py-5 dark:border-gray-800">
                <div class="rounded-xl bg-purple-100 p-3 dark:bg-purple-500/20">
                    <svg class="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
                    </svg>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">User Activity Logs</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Track user logins and actions</p>
                </div>
            </div>

            <!-- Filters -->
            <div class="border-b border-gray-200 bg-gray-50 px-6 py-4 dark:border-gray-800 dark:bg-gray-900/50">
                <div class="grid grid-cols-1 gap-4 md:grid-cols-5">
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Action Type</label>
                        <select v-model="activityFilters.action" @change="loadActivityLogs"
                            class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-brand-500 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white">
                            <option value="">All Actions</option>
                            <option value="login">Login</option>
                            <option value="logout">Logout</option>
                            <option value="page_view">Page View</option>
                            <option value="create">Create</option>
                            <option value="update">Update</option>
                            <option value="delete">Delete</option>
                            <option value="view">View</option>
                            <option value="export">Export</option>
                            <option value="import">Import</option>
                        </select>
                    </div>
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Resource</label>
                        <input v-model="activityFilters.resource" @input="debounceLoadLogs"
                            type="text" placeholder="e.g. employees, assets..."
                            class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-brand-500 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
                    </div>
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Start Date</label>
                        <div class="relative">
                            <flat-pickr
                                v-if="flatpickrReady"
                                v-model="activityFilters.start_date"
                                :config="datePickerOptions"
                                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 pr-10 text-sm text-gray-900 shadow-theme-xs transition focus:border-brand-500 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                                placeholder="Select start date" />
                            <input
                                v-else
                                type="text"
                                readonly
                                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                                placeholder="Loading..." />
                            <span class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                            </span>
                        </div>
                    </div>
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">End Date</label>
                        <div class="relative">
                            <flat-pickr
                                v-if="flatpickrReady"
                                v-model="activityFilters.end_date"
                                :config="datePickerOptions"
                                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 pr-10 text-sm text-gray-900 shadow-theme-xs transition focus:border-brand-500 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                                placeholder="Select end date" />
                            <input
                                v-else
                                type="text"
                                readonly
                                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                                placeholder="Loading..." />
                            <span class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                            </span>
                        </div>
                    </div>
                    <div class="flex items-end">
                        <button @click="clearActivityFilters"
                            class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-gray-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                            Clear Filters
                        </button>
                    </div>
                </div>
            </div>

            <!-- Activity Logs Table -->
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
                    <thead>
                        <tr class="border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900/50">
                            <th class="px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Timestamp</th>
                            <th class="px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">User</th>
                            <th class="px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Action</th>
                            <th class="px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Resource</th>
                            <th class="px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">IP Address</th>
                            <th class="px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Details</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                        <tr v-if="activityLoading">
                            <td colspan="6" class="px-5 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                                <div class="flex flex-col items-center gap-2">
                                    <svg class="h-8 w-8 animate-spin text-brand-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Loading activity logs...
                                </div>
                            </td>
                        </tr>
                        <tr v-else-if="activityLogs.length === 0">
                            <td colspan="6" class="px-5 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                                <div class="flex flex-col items-center gap-2">
                                    <svg class="h-12 w-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                                    </svg>
                                    No activity logs found
                                </div>
                            </td>
                        </tr>
                        <tr v-else v-for="log in activityLogs.filter(l => l && l.id)" :key="log.id"
                            class="transition hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td class="whitespace-nowrap px-5 py-4 text-sm text-gray-900 dark:text-gray-100">
                                {{ formatDateTime(log.timestamp) }}
                            </td>
                            <td class="whitespace-nowrap px-5 py-4 text-sm">
                                <div class="font-medium text-gray-900 dark:text-gray-100">{{ log.username }}</div>
                                <div class="text-gray-500 dark:text-gray-400">{{ log.worker_id }}</div>
                            </td>
                            <td class="whitespace-nowrap px-5 py-4 text-sm">
                                <span :class="getActionBadgeClass(log.action)"
                                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold leading-5">
                                    {{ log.action_display }}
                                </span>
                            </td>
                            <td class="whitespace-nowrap px-5 py-4 text-sm text-gray-900 dark:text-gray-100">
                                {{ log.resource || '-' }}
                                <span v-if="log.resource_id" class="text-gray-500 dark:text-gray-400">#{{ log.resource_id }}</span>
                            </td>
                            <td class="whitespace-nowrap px-5 py-4 text-sm text-gray-500 dark:text-gray-400">
                                {{ log.ip_address || '-' }}
                            </td>
                            <td class="px-5 py-4 text-sm text-gray-500 dark:text-gray-400">
                                <div v-if="Object.keys(log.details || {}).length > 0" class="max-w-xs truncate font-mono text-xs">
                                    {{ JSON.stringify(log.details) }}
                                </div>
                                <span v-else>-</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div v-if="!activityLoading && activityLogs.length > 0"
                class="border-t border-gray-200 px-6 py-4 dark:border-gray-800">
                <div class="flex items-center justify-between">
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                        Showing <span class="font-medium">{{ activityLogs.length }}</span> log{{ activityLogs.length !== 1 ? 's' : '' }}
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, reactive, ref } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useFlatpickrScroll } from '@/composables/useFlatpickrScroll'
import { apiClient } from '@/services/api'
import { formatLocalDateTime } from '@/utils/dateTime'

interface ActivityLog {
	id: number
	timestamp: string
	username: string
	worker_id: string | null
	action: string
	action_display: string
	resource: string | null
	resource_id: string | number | null
	ip_address: string | null
	details: Record<string, unknown> | null
}

const activityLogs = ref<ActivityLog[]>([])
const activityLoading = ref(false)
const activityFilters = reactive({
	action: '',
	resource: '',
	start_date: '',
	end_date: '',
})
let debounceTimer: ReturnType<typeof setTimeout> | null = null
let activityLogsAbortController: AbortController | null = null
const debounceLoadLogs = () => {
	if (debounceTimer) clearTimeout(debounceTimer)
	debounceTimer = setTimeout(() => loadActivityLogs(), 400)
}

// Flatpickr configuration for scrollable date selection
const { flatpickrInstances, attachMonthScroll, destroyFlatpickrs } = useFlatpickrScroll()
const flatpickrReady = ref(false)

const datePickerOptions = {
	dateFormat: 'Y-m-d',
	altInput: true,
	altFormat: 'M j, Y',
	onReady: (
		_selected: Date[],
		_dateStr: string,
		instance: Parameters<typeof attachMonthScroll>[0],
	) => {
		flatpickrInstances.value.push(instance)
		attachMonthScroll(instance)
	},
	onChange: () => {
		loadActivityLogs()
	},
}

const loadActivityLogs = async () => {
	if (activityLogsAbortController) {
		activityLogsAbortController.abort()
	}
	const controller = new AbortController()
	activityLogsAbortController = controller

	activityLoading.value = true
	try {
		const params = new URLSearchParams()
		params.append('page_size', '50')
		if (activityFilters.action) params.append('action', activityFilters.action)
		if (activityFilters.resource) params.append('resource', activityFilters.resource)
		if (activityFilters.start_date) params.append('start_date', activityFilters.start_date)
		if (activityFilters.end_date) params.append('end_date', activityFilters.end_date)

		const response = await apiClient.get(`/v1/activity-logs/?${params}`, {
			signal: controller.signal,
		})

		const data = response.data
		activityLogs.value = Array.isArray(data) ? data : data.results || []
	} catch (err) {
		if (err instanceof DOMException && err.name === 'AbortError') {
			return
		}
		console.error('Error loading activity logs:', err)
		activityLogs.value = []
	} finally {
		if (activityLogsAbortController === controller) {
			activityLogsAbortController = null
		}
		activityLoading.value = false
	}
}

const clearActivityFilters = () => {
	activityFilters.action = ''
	activityFilters.resource = ''
	activityFilters.start_date = ''
	activityFilters.end_date = ''
	loadActivityLogs()
}

const formatDateTime = (datetime: string) => {
	if (!datetime) return '-'
	return formatLocalDateTime(datetime)
}

const getActionBadgeClass = (action: string) => {
	const classes: Record<string, string> = {
		login: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
		logout: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
		page_view: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400',
		create: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
		update: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
		delete: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
		view: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
		export: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
		import: 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-400',
	}
	return classes[action] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

onMounted(async () => {
	await nextTick()
	flatpickrReady.value = true
	loadActivityLogs()
})

onUnmounted(() => {
	if (debounceTimer) {
		clearTimeout(debounceTimer)
	}
	if (activityLogsAbortController) {
		activityLogsAbortController.abort()
		activityLogsAbortController = null
	}
	destroyFlatpickrs()
})
</script>
