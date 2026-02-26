<template>
    <div class="space-y-6">
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between border-b border-gray-200 px-6 py-5 dark:border-gray-800">
                <div class="flex items-center gap-4">
                    <div class="rounded-xl bg-orange-100 p-3 dark:bg-orange-500/20">
                        <svg class="h-6 w-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">User Reports</h3>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Bug reports and feature requests from users</p>
                    </div>
                </div>
                <!-- Stats badges -->
                <div v-if="reportStats" class="hidden md:flex items-center gap-3">
                    <span class="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                        Open: {{ reportStats.by_status?.open || 0 }}
                    </span>
                    <span class="inline-flex items-center rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
                        In Progress: {{ reportStats.by_status?.in_progress || 0 }}
                    </span>
                    <span class="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
                        Resolved: {{ reportStats.by_status?.resolved || 0 }}
                    </span>
                </div>
            </div>

            <!-- Filters -->
            <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <select v-model="reportFilters.report_type" @change="loadReports"
                        class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
                        <option value="">All Types</option>
                        <option value="bug">Bug Reports</option>
                        <option value="feature">Feature Requests</option>
                    </select>
                    <select v-model="reportFilters.status" @change="loadReports"
                        class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
                        <option value="">All Statuses</option>
                        <option value="open">Open</option>
                        <option value="in_progress">In Progress</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                        <option value="wont_fix">Won't Fix</option>
                    </select>
                    <select v-model="reportFilters.priority" @change="loadReports"
                        class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
                        <option value="">All Priorities</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="reportsLoading" class="flex justify-center py-12">
                <svg class="animate-spin h-6 w-6 text-brand-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
            </div>

            <!-- Reports List -->
            <div v-else-if="reports.length === 0" class="px-6 py-12 text-center">
                <p class="text-sm text-gray-400 dark:text-gray-500">No reports found.</p>
            </div>

            <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
                <div v-for="report in reports" :key="report.id"
                    class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <div class="flex items-start justify-between gap-4">
                        <div class="min-w-0 flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-base">{{ report.report_type === 'bug' ? '🐛' : '💡' }}</span>
                                <h4 class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ report.title }}</h4>
                            </div>
                            <p class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">{{ report.description }}</p>
                            <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
                                <span class="font-medium text-gray-700 dark:text-gray-300" :title="report.reporter_email || ''">
                                    {{ report.reporter_name || report.reporter_username }}
                                </span>
                                <span v-if="report.reporter_worker_id" class="inline-flex items-center rounded bg-gray-100 px-1.5 py-0.5 text-xs font-mono text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                                    {{ report.reporter_worker_id }}
                                </span>
                                <span v-if="report.reporter_email" class="text-gray-400 dark:text-gray-500">{{ report.reporter_email }}</span>
                                <span class="text-gray-400 dark:text-gray-500">&middot;</span>
                                <span>{{ formatReportDate(report.created_at!) }}</span>
                            </div>
                        </div>
                        <div class="flex items-center gap-2 shrink-0">
                            <!-- Priority badge -->
                            <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                                :class="getReportPriorityClass(report.priority)">
                                {{ report.priority_display }}
                            </span>
                            <!-- Status select -->
                            <select :value="report.status"
                                @change="updateReportStatus(report.id!, ($event.target as HTMLSelectElement).value)"
                                class="rounded-lg border border-gray-300 bg-white px-2 py-1 text-xs text-gray-900 focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
                                <option value="open">Open</option>
                                <option value="in_progress">In Progress</option>
                                <option value="resolved">Resolved</option>
                                <option value="closed">Closed</option>
                                <option value="wont_fix">Won't Fix</option>
                            </select>
                        </div>
                    </div>

                    <!-- Admin Notes (inline edit) -->
                    <div class="mt-3">
                        <textarea v-model="report.admin_notes" rows="1" @blur="saveAdminNotes(report)"
                            placeholder="Add admin notes..."
                            class="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs text-gray-700 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-300" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { type UserReportData, userReportAPI } from '@/services/api'

const reportsLoading = ref(false)
const reports = ref<UserReportData[]>([])
const reportStats = ref<{
	total: number
	by_status: Record<string, number>
	by_type: Record<string, number>
} | null>(null)
const reportFilters = reactive({
	report_type: '',
	status: '',
	priority: '',
})

const loadReports = async () => {
	reportsLoading.value = true
	try {
		const params: Record<string, string> = {}
		if (reportFilters.report_type) params.report_type = reportFilters.report_type
		if (reportFilters.status) params.status = reportFilters.status
		if (reportFilters.priority) params.priority = reportFilters.priority
		const data = await userReportAPI.list(params)
		reports.value = data.results || (data as unknown as UserReportData[])
	} catch (err) {
		console.error('Failed to load reports:', err)
	} finally {
		reportsLoading.value = false
	}
}

const loadReportStats = async () => {
	try {
		reportStats.value = await userReportAPI.stats()
	} catch (err) {
		console.error('Failed to load report stats:', err)
	}
}

const updateReportStatus = async (id: number, newStatus: string) => {
	try {
		await userReportAPI.update(id, { status: newStatus })
		const r = reports.value.find((r) => r.id === id)
		if (r) r.status = newStatus
		loadReportStats()
	} catch (err) {
		console.error('Failed to update report:', err)
	}
}

const saveAdminNotes = async (report: UserReportData) => {
	if (!report.id) return
	try {
		await userReportAPI.update(report.id, { admin_notes: report.admin_notes })
	} catch (err) {
		console.error('Failed to save admin notes:', err)
	}
}

const getReportPriorityClass = (priority: string) => {
	switch (priority) {
		case 'critical':
			return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
		case 'high':
			return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
		case 'medium':
			return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
		default:
			return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
	}
}

const formatReportDate = (dateStr: string) => {
	const d = new Date(dateStr)
	return d.toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
	})
}

defineExpose({ loadReports, loadReportStats })

onMounted(() => {
	loadReports()
	loadReportStats()
})
</script>
