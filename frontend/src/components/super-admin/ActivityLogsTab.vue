<template>
    <div class="space-y-6">
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between gap-4 border-b border-gray-200 px-6 py-5 dark:border-gray-800">
                <div class="flex items-center gap-4">
                    <div class="rounded-xl bg-purple-100 p-3 dark:bg-purple-500/20">
                        <svg class="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">User Activity Logs</h3>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Track user logins and actions</p>
                    </div>
                </div>
                <button type="button" @click="showSettingsModal = true"
                    class="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 transition hover:border-purple-300 hover:text-purple-700 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:border-purple-500/40 dark:hover:text-purple-200">
                    <SettingsIcon class="h-4 w-4" />
                    Settings
                </button>
            </div>

            <div class="border-b border-gray-200 bg-purple-50/50 px-6 py-4 dark:border-gray-800 dark:bg-purple-900/10">
                <div class="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
                    <div class="flex flex-wrap items-center gap-3 text-sm text-gray-600 dark:text-gray-300">
                        <span class="inline-flex items-center rounded-full border border-purple-200 bg-white px-3 py-1 font-medium text-purple-700 dark:border-purple-500/30 dark:bg-purple-500/10 dark:text-purple-200">
                            {{ retentionSummary }}
                        </span>
                        <span class="inline-flex items-center rounded-full border border-gray-200 bg-white px-3 py-1 font-medium text-gray-600 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300">
                            Scheduled daily at {{ cleanupScheduleLabel }}
                        </span>
                    </div>
                    <div v-if="lastPurgeResult" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-200">
                        Deleted {{ lastPurgeResult.deleted_count }} log{{ lastPurgeResult.deleted_count === 1 ? '' : 's' }} older than {{ lastPurgeResult.days }} day{{ lastPurgeResult.days === 1 ? '' : 's' }}.
                        <span class="block pt-1 text-xs text-emerald-700/80 dark:text-emerald-200/80">Cutoff used: {{ formatDateTime(lastPurgeResult.cutoff) }}</span>
                    </div>
                </div>
            </div>

            <div class="border-b border-gray-200 bg-gray-50 px-6 py-4 dark:border-gray-800 dark:bg-gray-900/50">
                <div class="grid grid-cols-1 gap-4 md:grid-cols-5">
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Employee</label>
                        <FilterDropdown v-model="activityFilters.user_id" :options="userFilterOptions" placeholder="All Employees" />
                    </div>
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Action Type</label>
                        <FilterDropdown v-model="activityFilters.action" :options="actionFilterOptions" placeholder="All Actions" :searchable="false" />
                    </div>
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Resource</label>
                        <input v-model="activityFilters.resource" @input="debounceLoadLogs" type="text" placeholder="e.g. employees, assets..."
                            class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-brand-500 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
                    </div>
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Date Range</label>
                        <div class="relative">
                            <flat-pickr v-if="flatpickrReady" v-model="dateRange" :config="dateRangePickerOptions"
                                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 pr-10 text-sm text-gray-900 shadow-theme-xs transition focus:border-brand-500 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                                placeholder="Select date range" />
                            <input v-else type="text" readonly
                                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                                placeholder="Loading..." />
                            <span class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
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
                                        <path class="opacity-75" fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Loading activity logs...
                                </div>
                            </td>
                        </tr>
                        <tr v-else-if="activityLogs.length === 0">
                            <td colspan="6" class="px-5 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                                <div class="flex flex-col items-center gap-2">
                                    <svg class="h-12 w-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                    </svg>
                                    No activity logs found
                                </div>
                            </td>
                        </tr>
                        <tr v-else v-for="log in validLogs" :key="log.id" class="transition hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td class="whitespace-nowrap px-5 py-4 text-sm text-gray-900 dark:text-gray-100">
                                {{ formatDateTime(log.timestamp) }}
                            </td>
                            <td class="whitespace-nowrap px-5 py-4 text-sm">
                                <div class="font-medium text-gray-900 dark:text-gray-100">{{ log.username }}</div>
                                <div class="text-gray-500 dark:text-gray-400">{{ log.worker_id }}</div>
                            </td>
                            <td class="whitespace-nowrap px-5 py-4 text-sm">
                                <span :class="getActionBadgeClass(log.action)" class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold leading-5">
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
                                <div v-if="log._detailsJson" class="max-w-md whitespace-pre-wrap break-words rounded-lg bg-gray-50 px-3 py-2 font-mono text-xs dark:bg-gray-900/50">
                                    {{ log._detailsJson }}
                                </div>
                                <span v-else>-</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div v-if="!activityLoading && totalCount > 0" class="border-t border-gray-200 px-6 py-4 dark:border-gray-800">
                <div class="flex items-center justify-between">
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                        Showing <span class="font-medium">{{ activityLogs.length }}</span> of
                        <span class="font-medium">{{ totalCount }}</span> log{{ totalCount !== 1 ? 's' : '' }}
                    </p>
                    <div v-if="totalPages > 1" class="flex items-center gap-2">
                        <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1"
                            class="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                            Previous
                        </button>
                        <span class="text-sm text-gray-600 dark:text-gray-400">
                            Page {{ currentPage }} of {{ totalPages }}
                        </span>
                        <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages"
                            class="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                            Next
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="showSettingsModal" class="fixed inset-0 z-[100000] flex items-center justify-center bg-gray-950/70 p-4" @click.self="showSettingsModal = false">
            <div class="flex max-h-[90vh] w-full max-w-xl flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl dark:border-gray-800 dark:bg-gray-950">
                <!-- Header -->
                <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-800">
                    <h4 class="text-base font-semibold text-gray-900 dark:text-white">Activity Log Settings</h4>
                    <button type="button" @click="showSettingsModal = false" class="rounded-lg p-1.5 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-200">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div class="flex-1 space-y-5 overflow-y-auto px-6 py-5">
                    <!-- Automatic Cleanup Section -->
                    <section>
                        <div class="flex items-center gap-2">
                            <div class="h-2 w-2 rounded-full bg-purple-500"></div>
                            <h5 class="text-sm font-semibold text-gray-900 dark:text-white">Automatic Cleanup</h5>
                        </div>
                        <p class="mt-1.5 text-xs text-gray-500 dark:text-gray-400">Logs older than the retention period are removed daily. Clear to keep indefinitely.</p>

                        <div class="mt-4 grid grid-cols-[1fr_140px] gap-3">
                            <div>
                                <label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Retention (days)</label>
                                <div class="relative">
                                    <input v-model="retentionDaysInput" type="number" min="1" step="1" inputmode="numeric" placeholder="30"
                                        class="block h-10 w-full rounded-lg border border-gray-300 bg-white px-3 pr-14 text-sm text-gray-900 transition focus:border-purple-500 focus:outline-hidden focus:ring-2 focus:ring-purple-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
                                    <span class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[11px] font-medium text-gray-400">days</span>
                                </div>
                            </div>
                            <div>
                                <label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Run at</label>
                                <input v-model="cleanupScheduleInput" type="time" step="60"
                                    class="block h-10 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-900 transition focus:border-purple-500 focus:outline-hidden focus:ring-2 focus:ring-purple-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
                            </div>
                        </div>

                        <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">{{ retentionHintText }}</p>

                        <div v-if="retentionError" class="mt-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700 dark:bg-red-500/10 dark:text-red-300">
                            {{ retentionError }}
                        </div>

                        <div class="mt-3 flex items-center gap-2">
                            <button type="button" @click="saveRetentionSettings" :disabled="!canSaveRetentionSettings"
                                class="h-9 rounded-lg bg-purple-600 px-4 text-xs font-semibold text-white transition hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50">
                                {{ retentionSaving ? 'Saving...' : 'Save' }}
                            </button>
                            <button type="button" @click="clearRetentionPolicy" :disabled="retentionSaving"
                                class="h-9 rounded-lg border border-gray-300 bg-white px-4 text-xs font-medium text-gray-600 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:hover:bg-gray-800">
                                Keep Indefinitely
                            </button>
                        </div>
                    </section>

                    <!-- Divider -->
                    <div class="border-t border-gray-200 dark:border-gray-800"></div>

                    <!-- Immediate Deletion Section -->
                    <section>
                        <div class="flex items-center gap-2">
                            <div class="h-2 w-2 rounded-full bg-rose-500"></div>
                            <h5 class="text-sm font-semibold text-gray-900 dark:text-white">Delete Old Logs</h5>
                            <span class="rounded-full bg-rose-100 px-2 py-0.5 text-[10px] font-semibold text-rose-700 dark:bg-rose-500/15 dark:text-rose-300">Permanent</span>
                        </div>
                        <p class="mt-1.5 text-xs text-gray-500 dark:text-gray-400">Remove logs older than a given threshold immediately.</p>

                        <div class="mt-4 flex items-end gap-3">
                            <div class="flex-1">
                                <label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Older than</label>
                                <div class="relative">
                                    <input v-model="purgeDaysInput" type="number" min="1" step="1" inputmode="numeric" placeholder="30"
                                        class="block h-10 w-full rounded-lg border border-gray-300 bg-white px-3 pr-14 text-sm text-gray-900 transition focus:border-rose-500 focus:outline-hidden focus:ring-2 focus:ring-rose-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
                                    <span class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[11px] font-medium text-gray-400">days</span>
                                </div>
                            </div>
                            <button @click="purgeOldLogs" :disabled="!canPurgeActivityLogs" type="button"
                                class="h-10 rounded-lg bg-rose-600 px-4 text-xs font-semibold text-white transition hover:bg-rose-700 disabled:cursor-not-allowed disabled:opacity-50">
                                {{ purgeSubmitting ? 'Deleting...' : 'Delete Now' }}
                            </button>
                        </div>

                        <label class="mt-3 flex items-center gap-2.5 text-xs text-gray-600 dark:text-gray-300">
                            <input v-model="purgeConfirmed" type="checkbox" class="h-3.5 w-3.5 rounded border-gray-300 text-rose-600 focus:ring-rose-500/30 dark:border-gray-600 dark:bg-gray-900" />
                            <span>I confirm this permanently deletes matching logs.</span>
                        </label>

                        <p v-if="parsedPurgeDays" class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                            {{ purgeHintText }}
                            <span v-if="configStore.userActivityLogRetentionDays" class="text-gray-400 dark:text-gray-500"> &middot; Policy: {{ configStore.userActivityLogRetentionDays }}d</span>
                        </p>

                        <div v-if="purgeError" class="mt-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700 dark:bg-red-500/10 dark:text-red-300">
                            {{ purgeError }}
                        </div>

                        <div v-if="lastPurgeResult" class="mt-2 rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-200">
                            Deleted {{ lastPurgeResult.deleted_count }} log{{ lastPurgeResult.deleted_count === 1 ? '' : 's' }} older than {{ lastPurgeResult.days }}d.
                            <span class="text-emerald-600 dark:text-emerald-300">Cutoff: {{ formatDateTime(lastPurgeResult.cutoff) }}</span>
                        </div>
                    </section>
                </div>

                <div class="flex items-center justify-end border-t border-gray-200 px-6 py-3 dark:border-gray-800">
                    <button type="button" @click="showSettingsModal = false"
                        class="h-9 rounded-lg border border-gray-300 bg-white px-4 text-xs font-semibold text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800">
                        Close
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import FilterDropdown from '@/components/ui/FilterDropdown.vue'
import { SettingsIcon } from '@/icons'
import { useFlatpickrScroll } from '@/composables/useFlatpickrScroll'
import type { UserAccessControl } from '@/services/api/auth'
import { apiClient } from '@/services/api/client'
import { type ActivityLogCleanupTime, useConfigStore } from '@/stores/config'
import { formatLocalDateTime } from '@/utils/dateTime'
import { extractApiError } from '@/utils/extractApiError'

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

interface ActivityLogPurgeResult {
    status: string
    deleted_count: number
    days: number
    cutoff: string
}

const props = defineProps<{
	users: UserAccessControl[]
}>()

const configStore = useConfigStore()

const activityLogs = ref<ActivityLog[]>([])
const activityLoading = ref(false)
const currentPage = ref(1)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / 50))
const validLogs = computed(() =>
	activityLogs.value
        .filter((log: ActivityLog) => log?.id)
        .map((log: ActivityLog) => ({
            ...log,
            _detailsJson: log.details && Object.keys(log.details).length > 0 ? JSON.stringify(log.details) : '',
		})),
)
const activityFilters = reactive({
	user_id: [] as string[],
	action: [] as string[],
	resource: '',
})
const dateRange = ref('')
let debounceTimer: ReturnType<typeof setTimeout> | null = null
let activityLogsAbortController: AbortController | null = null
const debounceLoadLogs = () => {
	if (debounceTimer) clearTimeout(debounceTimer)
	debounceTimer = setTimeout(() => {
		currentPage.value = 1
		loadActivityLogs()
	}, 400)
}

const userOptions = computed(() =>
	props.users
        .filter((user: UserAccessControl) => user.is_active)
		.slice()
        .sort((left: UserAccessControl, right: UserAccessControl) => {
            const nameA = `${left.first_name} ${left.last_name}`.trim() || left.username
            const nameB = `${right.first_name} ${right.last_name}`.trim() || right.username
			return nameA.localeCompare(nameB)
		}),
)

const userFilterOptions = computed(() =>
	userOptions.value.map((user) => ({
		value: String(user.id),
		label: `${`${user.first_name} ${user.last_name}`.trim() || user.username} (${user.worker_id || user.username})`,
	})),
)

const actionFilterOptions = computed(() => [
	{ value: 'login', label: 'Login' },
	{ value: 'logout', label: 'Logout' },
	{ value: 'page_view', label: 'Page View' },
	{ value: 'create', label: 'Create' },
	{ value: 'update', label: 'Update' },
	{ value: 'delete', label: 'Delete' },
	{ value: 'view', label: 'View' },
	{ value: 'export', label: 'Export' },
	{ value: 'import', label: 'Import' },
])

// Flatpickr configuration for scrollable date range selection
const { flatpickrInstances, attachMonthScroll, destroyFlatpickrs } = useFlatpickrScroll()
const flatpickrReady = ref(false)
const showSettingsModal = ref(false)
const retentionDaysInput = ref<string | number>('')
const retentionSaving = ref(false)
const retentionError = ref('')
const cleanupScheduleInput = ref<ActivityLogCleanupTime>('00:15')
const purgeDaysInput = ref<string | number>('')
const purgeConfirmed = ref(false)
const purgeSubmitting = ref(false)
const purgeError = ref('')
const lastPurgeResult = ref<ActivityLogPurgeResult | null>(null)

const normalizeTextInput = (value: string | number | null | undefined) => String(value ?? '').trim()

const normalizeCleanupScheduleInput = (value: string | null | undefined): ActivityLogCleanupTime => {
	const normalized = String(value ?? '').trim()
    return /^\d{2}:\d{2}$/.test(normalized) ? (normalized as ActivityLogCleanupTime) : '00:15'
}

const cleanupScheduleLabel = computed(() => normalizeCleanupScheduleInput(configStore.userActivityLogCleanupTime))

const parsedRetentionDays = computed(() => {
	const rawValue = normalizeTextInput(retentionDaysInput.value)
    if (!rawValue) return null
    const parsed = Number(rawValue)
    if (!Number.isInteger(parsed) || parsed < 1) return undefined
    return parsed
})

const canSaveRetentionSettings = computed(() => !retentionSaving.value && parsedRetentionDays.value !== undefined)

const retentionSummary = computed(() => {
    if (!configStore.userActivityLogRetentionDays) {
        return 'Automatic cleanup disabled'
    }
    return `Automatic cleanup after ${configStore.userActivityLogRetentionDays} day${configStore.userActivityLogRetentionDays === 1 ? '' : 's'}`
})

const retentionHintText = computed(() => {
    if (!normalizeTextInput(retentionDaysInput.value)) {
        return 'Leaving this empty disables scheduled cleanup and keeps logs indefinitely.'
    }
    if (parsedRetentionDays.value === undefined) {
        return 'Enter a whole number greater than zero to enable scheduled cleanup.'
    }
	return `Logs older than ${parsedRetentionDays.value} day${parsedRetentionDays.value === 1 ? '' : 's'} will be removed by the daily cleanup job at ${cleanupScheduleLabel.value}.`
})

const parsedPurgeDays = computed(() => {
	const rawValue = normalizeTextInput(purgeDaysInput.value)
	if (!rawValue) return null
	const parsed = Number(rawValue)
	if (!Number.isInteger(parsed) || parsed < 1) return null
	return parsed
})

const canPurgeActivityLogs = computed(() => parsedPurgeDays.value !== null && purgeConfirmed.value && !purgeSubmitting.value)

const purgeHintText = computed(() => {
	if (parsedPurgeDays.value === null) {
		return 'Enter a positive day value, then confirm before deleting.'
	}
	return `Logs with a timestamp older than ${parsedPurgeDays.value} day${parsedPurgeDays.value === 1 ? '' : 's'} will be removed immediately.`
})

const resetPageAndLoad = () => {
	currentPage.value = 1
	loadActivityLogs()
}

const dateRangePickerOptions = {
	mode: 'range' as const,
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
		resetPageAndLoad()
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
		params.append('page', String(currentPage.value))
		if (activityFilters.user_id.length > 0) params.append('user_id', activityFilters.user_id.join(','))
		if (activityFilters.action.length > 0) params.append('action', activityFilters.action.join(','))
		if (activityFilters.resource) params.append('resource', activityFilters.resource)

		// Parse date range "YYYY-MM-DD to YYYY-MM-DD"
		if (dateRange.value) {
			const dates = dateRange.value.split(' to ')
			if (dates[0]) params.append('start_date', dates[0])
			if (dates[1]) params.append('end_date', dates[1])
			else if (dates[0]) params.append('end_date', dates[0])
		}

		const response = await apiClient.get(`/v1/activity-logs/?${params}`, {
			signal: controller.signal,
		})

		const data = response.data
		if (Array.isArray(data)) {
			activityLogs.value = data
			totalCount.value = data.length
		} else {
			activityLogs.value = data.results || []
			totalCount.value = data.count || 0
		}
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
	activityFilters.user_id = []
	activityFilters.action = []
	activityFilters.resource = ''
	dateRange.value = ''
	currentPage.value = 1
	loadActivityLogs()
}

watch(
	[() => activityFilters.user_id, () => activityFilters.action],
	() => resetPageAndLoad(),
)

const saveRetentionSettings = async () => {
    if (parsedRetentionDays.value === undefined) {
        retentionError.value = 'Enter a positive whole number of days, or clear the field to disable scheduled cleanup.'
        return
    }

	retentionSaving.value = true
    retentionError.value = ''
	try {
		await configStore.updateConfig({
			user_activity_log_retention_days: parsedRetentionDays.value ?? null,
			user_activity_log_cleanup_time: normalizeCleanupScheduleInput(cleanupScheduleInput.value),
		})
		await configStore.fetchConfig(true)
        retentionDaysInput.value = configStore.userActivityLogRetentionDays
            ? String(configStore.userActivityLogRetentionDays)
            : ''
		cleanupScheduleInput.value = normalizeCleanupScheduleInput(configStore.userActivityLogCleanupTime)
        if (!normalizeTextInput(purgeDaysInput.value)) {
            purgeDaysInput.value = String(configStore.userActivityLogRetentionDays ?? 30)
        }
	} catch (error) {
		console.error('Failed to save activity log retention settings:', error)
        retentionError.value = extractApiError(error, 'Failed to save cleanup policy')
	} finally {
		retentionSaving.value = false
	}
}

const clearRetentionPolicy = () => {
    retentionDaysInput.value = ''
    retentionError.value = ''
}

const purgeOldLogs = async () => {
	if (!canPurgeActivityLogs.value || parsedPurgeDays.value === null) {
		purgeError.value = 'Enter a valid day value and confirm the permanent delete action.'
		return
	}

	purgeSubmitting.value = true
	purgeError.value = ''
	lastPurgeResult.value = null
	try {
		const response = await apiClient.post<ActivityLogPurgeResult>('/v1/activity-logs/purge/', {
			days: parsedPurgeDays.value,
		})
		lastPurgeResult.value = response.data
		purgeConfirmed.value = false
		currentPage.value = 1
		await loadActivityLogs()
	} catch (error) {
		console.error('Failed to purge activity logs:', error)
		purgeError.value = extractApiError(error, 'Failed to delete old activity logs')
	} finally {
		purgeSubmitting.value = false
	}
}

const goToPage = (page: number) => {
	if (page < 1 || page > totalPages.value) return
	currentPage.value = page
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
    retentionDaysInput.value = configStore.userActivityLogRetentionDays
        ? String(configStore.userActivityLogRetentionDays)
        : ''
	cleanupScheduleInput.value = normalizeCleanupScheduleInput(configStore.userActivityLogCleanupTime)
    purgeDaysInput.value = String(configStore.userActivityLogRetentionDays ?? 30)
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
