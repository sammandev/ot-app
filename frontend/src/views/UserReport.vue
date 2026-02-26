<template>
    <admin-layout>
        <div class="space-y-6">
            <!-- Page Header -->
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.userReport.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.userReport.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.userReport.subtitle') }}</p>
                </div>
                <nav>
                    <ol class="flex items-center gap-2 text-sm">
                        <li><router-link
                                class="font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                                to="/">Home</router-link></li>
                        <li class="text-gray-400 dark:text-gray-500">/</li>
                        <li class="font-medium text-brand-500">Report</li>
                    </ol>
                </nav>
            </div>

            <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
                <!-- Submit / Edit Form -->
                <div class="lg:col-span-2">
                    <div
                        class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
                        <div class="flex items-center justify-between mb-5">
                            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                                {{ editingReport ? 'Edit Report' : 'New Report' }}
                            </h2>
                            <button v-if="editingReport" @click="cancelEdit" type="button"
                                class="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors">
                                Cancel editing
                            </button>
                        </div>

                        <!-- Success message -->
                        <div v-if="submitSuccess"
                            class="mb-5 flex items-center gap-3 rounded-xl bg-green-50 p-4 text-sm text-green-700 dark:bg-green-900/20 dark:text-green-400">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                                stroke="currentColor" class="h-5 w-5 shrink-0">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                            </svg>
                            <span>{{ editingReport ? 'Report updated successfully!' : 'Your report has been submitted successfully! We\'ll review it soon.' }}</span>
                        </div>

                        <form @submit.prevent="handleSubmit" class="space-y-5">
                            <!-- Report Type -->
                            <div>
                                <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Report Type <span class="text-red-500">*</span>
                                </label>
                                <div class="flex gap-3">
                                    <label v-for="opt in typeOptions" :key="opt.value"
                                        class="flex-1 cursor-pointer rounded-xl border-2 p-4 text-center transition-colors"
                                        :class="form.report_type === opt.value
                                            ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20 dark:border-brand-400'
                                            : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'">
                                        <input type="radio" v-model="form.report_type" :value="opt.value"
                                            class="sr-only" />
                                        <span class="text-2xl block mb-1">{{ opt.icon }}</span>
                                        <span class="text-sm font-medium text-gray-900 dark:text-white">{{ opt.label
                                            }}</span>
                                    </label>
                                </div>
                            </div>

                            <!-- Title -->
                            <div>
                                <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Title <span class="text-red-500">*</span>
                                </label>
                                <input v-model="form.title" type="text" required
                                    class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
                                    :placeholder="form.report_type === 'bug' ? 'e.g., Page crashes when clicking submit' : 'e.g., Add dark mode toggle'" />
                            </div>

                            <!-- Priority -->
                            <div>
                                <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Priority
                                </label>
                                <select v-model="form.priority"
                                    class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
                                </select>
                            </div>

                            <!-- Description -->
                            <div>
                                <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Description <span class="text-red-500">*</span>
                                </label>
                                <textarea v-model="form.description" rows="5" required
                                    class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
                                    :placeholder="form.report_type === 'bug'
                                        ? 'Describe the bug: what happened, what you expected, steps to reproduce...'
                                        : 'Describe the feature you\'d like to see and why it would be useful...'" />
                            </div>

                            <!-- Page URL (auto-filled for bugs) -->
                            <div v-if="form.report_type === 'bug'">
                                <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Page URL (where the issue occurred)
                                </label>
                                <input v-model="form.page_url" type="text"
                                    class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-500"
                                    placeholder="e.g., /ot/form" />
                            </div>

                            <!-- Submit / Update buttons -->
                            <div class="flex justify-end gap-3">
                                <button v-if="editingReport" type="button" @click="cancelEdit"
                                    class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                                    Cancel
                                </button>
                                <button type="submit" :disabled="submitting"
                                    class="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors dark:focus:ring-offset-gray-900">
                                    <svg v-if="submitting" class="animate-spin h-4 w-4"
                                        xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                            stroke-width="4" />
                                        <path class="opacity-75" fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    {{ submitting ? (editingReport ? 'Updating...' : 'Submitting...') : (editingReport ? 'Update Report' : 'Submit Report') }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- My Reports sidebar -->
                <div class="lg:col-span-1">
                    <div
                        class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
                        <div class="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
                            <h3 class="text-sm font-semibold text-gray-900 dark:text-white">My Reports</h3>
                        </div>

                        <div v-if="loadingReports" class="flex justify-center py-8">
                            <svg class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg"
                                fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4" />
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                        </div>

                        <div v-else-if="myReports.length === 0" class="px-5 py-8 text-center">
                            <p class="text-sm text-gray-400 dark:text-gray-500">No reports submitted yet.</p>
                        </div>

                        <div v-else class="divide-y divide-gray-100 dark:divide-gray-800 max-h-[500px] overflow-y-auto">
                            <div v-for="report in myReports" :key="report.id"
                                class="px-5 py-3.5 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                                :class="{ 'ring-2 ring-inset ring-brand-500/30 bg-brand-50/50 dark:bg-brand-900/10': editingReport?.id === report.id }">
                                <div class="flex items-start justify-between gap-2 mb-1">
                                    <span class="text-sm font-medium text-gray-900 dark:text-white line-clamp-1">
                                        {{ report.title }}
                                    </span>
                                    <span class="inline-flex whitespace-nowrap items-center rounded-full px-2 py-0.5 text-xs font-medium shrink-0"
                                        :class="getStatusBadgeClass(report.status || 'open')">
                                        {{ report.status_display }}
                                    </span>
                                </div>
                                <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                    <span class="inline-flex items-center rounded-full px-1.5 py-0.5 text-xs"
                                        :class="report.report_type === 'bug' ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400' : 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'">
                                        {{ report.report_type === 'bug' ? '🐛' : '💡' }}
                                    </span>
                                    <span>{{ formatTimeAgo(report.created_at!) }}</span>
                                </div>

                                <!-- Edit / Delete buttons (only for open reports) -->
                                <div v-if="report.status === 'open'" class="mt-2 flex items-center gap-2">
                                    <button @click="startEdit(report)" type="button"
                                        class="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-brand-600 hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-brand-900/20 transition-colors">
                                        <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Z" /></svg>
                                        Edit
                                    </button>
                                    <button @click="confirmDelete(report)" type="button"
                                        class="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 transition-colors">
                                        <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" /></svg>
                                        Delete
                                    </button>
                                </div>

                                <!-- Admin response -->
                                <div v-if="report.admin_notes"
                                    class="mt-2 rounded-lg bg-blue-50 dark:bg-blue-900/20 p-2.5 text-xs text-blue-700 dark:text-blue-400">
                                    <span class="font-medium">Admin:</span> {{ report.admin_notes }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </admin-layout>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToast } from '@/composables/useToast'
import { type UserReportData, userReportAPI } from '@/services/api'
import { timeAgo as formatTimeAgo } from '@/utils/dateTime'

const { confirm } = useConfirmDialog()
const { t } = useI18n()
const { showToast } = useToast()

const typeOptions = [
	{ value: 'bug', label: 'Bug Report', icon: '🐛' },
	{ value: 'feature', label: 'Feature Request', icon: '💡' },
]

const form = reactive({
	report_type: 'bug',
	title: '',
	description: '',
	page_url: '',
	priority: 'medium',
})

const submitting = ref(false)
const submitSuccess = ref(false)
const myReports = ref<UserReportData[]>([])
const loadingReports = ref(true)
const editingReport = ref<UserReportData | null>(null)

function getStatusBadgeClass(status: string) {
	switch (status) {
		case 'open':
			return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
		case 'in_progress':
			return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
		case 'resolved':
			return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
		case 'closed':
			return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
		case 'wont_fix':
			return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
		default:
			return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
	}
}

async function fetchMyReports() {
	loadingReports.value = true
	try {
		const data = await userReportAPI.list()
		myReports.value = data.results || (data as unknown as UserReportData[])
	} catch (err) {
		console.error('Failed to fetch reports:', err)
	} finally {
		loadingReports.value = false
	}
}

function resetForm() {
	form.report_type = 'bug'
	form.title = ''
	form.description = ''
	form.page_url = ''
	form.priority = 'medium'
	editingReport.value = null
}

function startEdit(report: UserReportData) {
	editingReport.value = report
	form.report_type = report.report_type
	form.title = report.title
	form.description = report.description
	form.page_url = report.page_url || ''
	form.priority = report.priority
	submitSuccess.value = false
	// Scroll to form
	window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelEdit() {
	resetForm()
	submitSuccess.value = false
}

async function confirmDelete(report: UserReportData) {
	const ok = await confirm({
		title: 'Delete Report',
		message: `Are you sure you want to delete "${report.title}"? This action cannot be undone.`,
		type: 'danger',
		confirmLabel: 'Delete',
	})
	if (!ok) return
	try {
		await userReportAPI.delete(report.id!)
		showToast('Report deleted successfully', 'success')
		fetchMyReports()
	} catch (err) {
		console.error('Failed to delete report:', err)
		showToast('Failed to delete report. Only open reports can be deleted.', 'error')
	}
}

async function handleSubmit() {
	submitting.value = true
	submitSuccess.value = false
	try {
		if (editingReport.value) {
			// Update existing report
			await userReportAPI.update(editingReport.value.id!, {
				report_type: form.report_type,
				title: form.title,
				description: form.description,
				page_url: form.page_url,
				priority: form.priority,
			})
			showToast('Report updated successfully', 'success')
		} else {
			// Create new report
			await userReportAPI.create({
				report_type: form.report_type,
				title: form.title,
				description: form.description,
				page_url: form.page_url,
				priority: form.priority,
			})
		}
		submitSuccess.value = true
		resetForm()
		fetchMyReports()
		setTimeout(() => {
			submitSuccess.value = false
		}, 5000)
	} catch (err) {
		console.error('Failed to submit report:', err)
		showToast('Failed to submit report', 'error')
	} finally {
		submitting.value = false
	}
}

onMounted(fetchMyReports)
</script>
