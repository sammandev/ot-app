<template>
    <AdminLayout>
        <div class="space-y-6">
            <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.otSummary.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.otSummary.title') }}
                    </h1>
                    <span
                        class="rounded-md bg-brand-100 px-2 py-1 text-xs font-medium text-brand-700 dark:bg-brand-900/30 dark:text-brand-200">{{ t('otSummary.monthCalculation') }}</span>
                </div>
            </div>

            <!-- Loading State -->
            <template v-if="isLoading">
                <FilterSkeleton :filters="4" />
                <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                    <StatCardSkeleton v-for="i in 4" :key="i" />
                </div>
                <ChartSkeleton :height="350" :bars="12" :show-controls="true" />
                <TableSkeleton :rows="10" :columns="5" />
                <TableSkeleton :rows="10" :columns="5" />
            </template>

            <!-- Main Content -->
            <template v-else>
                <!-- Filters -->
                <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                    <div class="grid gap-4 lg:grid-cols-12">
                        <div class="lg:col-span-3 space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('otSummary.dateSelection') }}</label>
                            <select v-model="dateSelectionType"
                                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                                <option value="year-month">{{ t('otSummary.yearMonth') }}</option>
                                <option value="custom">{{ t('otSummary.customDateRange') }}</option>
                            </select>
                        </div>

                        <template v-if="dateSelectionType === 'year-month'">
                            <div class="lg:col-span-3 space-y-2">
                                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('otSummary.year') }}</label>
                                <select v-model.number="selectedYear" @change="handleYearMonthChange"
                                    class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                                    <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
                                </select>
                            </div>
                            <div class="lg:col-span-3 space-y-2">
                                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('otSummary.month') }}</label>
                                <select v-model="selectedMonth" @change="handleYearMonthChange"
                                    class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                                    <option value="all">{{ t('months.allMonths') }}</option>
                                    <option v-for="month in months" :key="month.value" :value="month.value">{{
                                        month.label
                                    }}</option>
                                </select>
                            </div>
                            <div class="lg:col-span-3 flex items-end">
                                <button @click="resetToCurrentPeriod"
                                    class="h-11 w-full rounded-lg border border-brand-300 bg-brand-50 px-4 text-sm font-semibold text-brand-700 shadow-theme-xs transition hover:bg-brand-100 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-100">
                                    {{ t('otSummary.currentPeriod') }}
                                </button>
                            </div>
                        </template>

                        <template v-if="dateSelectionType === 'custom'">
                            <div class="lg:col-span-6 space-y-2">
                                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('otSummary.customDateRange') }}</label>
                                <div class="relative">
                                    <flat-pickr v-if="flatpickrReady" v-model="customDateRange"
                                        :config="datePickerOptions"
                                        class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 pr-11 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                                        placeholder="Select date range" />
                                    <input v-else type="text" :value="customDateRange" readonly
                                        class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 pr-11 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                                        placeholder="Loading date picker..." />
                                    <span
                                        class="absolute text-gray-500 -translate-y-1/2 pointer-events-none right-3 top-1/2 dark:text-gray-400">
                                        <svg class="fill-current" width="20" height="20" viewBox="0 0 20 20" fill="none"
                                            xmlns="http://www.w3.org/2000/svg">
                                            <path fill-rule="evenodd" clip-rule="evenodd"
                                                d="M6.66659 1.5415C7.0808 1.5415 7.41658 1.87729 7.41658 2.2915V2.99984H12.5833V2.2915C12.5833 1.87729 12.919 1.5415 13.3333 1.5415C13.7475 1.5415 14.0833 1.87729 14.0833 2.2915V2.99984L15.4166 2.99984C16.5212 2.99984 17.4166 3.89527 17.4166 4.99984V7.49984V15.8332C17.4166 16.9377 16.5212 17.8332 15.4166 17.8332H4.58325C3.47868 17.8332 2.58325 16.9377 2.58325 15.8332V7.49984V4.99984C2.58325 3.89527 3.47868 2.99984 4.58325 2.99984L5.91659 2.99984V2.2915C5.91659 1.87729 6.25237 1.5415 6.66659 1.5415ZM6.66659 4.49984H4.58325C4.30711 4.49984 4.08325 4.7237 4.08325 4.99984V6.74984H15.9166V4.99984C15.9166 4.7237 15.6927 4.49984 15.4166 4.49984H13.3333H6.66659ZM15.9166 8.24984H4.08325V15.8332C4.08325 16.1093 4.30711 16.3332 4.58325 16.3332H15.4166C15.6927 16.3332 15.9166 16.1093 15.9166 15.8332V8.24984Z"
                                                fill="" />
                                        </svg>
                                    </span>
                                </div>
                            </div>
                            <div class="lg:col-span-3 flex items-end">
                                <button @click="clearCustomRange" :disabled="!customDateRange"
                                    class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:opacity-60 disabled:cursor-not-allowed dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                    {{ t('common.clear') }}
                                </button>
                            </div>
                        </template>

                        <div class="lg:col-span-12">
                            <div
                                class="flex items-center justify-between rounded-lg border border-brand-200 bg-gradient-to-r from-brand-50 to-blue-50 px-4 py-3 text-sm text-brand-900 shadow-theme-xs dark:border-brand-700/60 dark:from-brand-900/30 dark:to-blue-900/20 dark:text-white">
                                <div class="font-semibold">{{ t('otSummary.activePeriod') }}</div>
                                <div class="flex items-center gap-3">
                                    <div class="font-semibold">{{ formattedPeriod }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Summary cards -->
                <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                    <div v-for="card in summaryCards" :key="card.title"
                        class="rounded-2xl border border-gray-200 bg-white p-4 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900">
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ card.title }}</p>
                        <div class="mt-2 flex items-baseline justify-between">
                            <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ card.value }}</p>
                            <span :class="card.trend >= 0 ? 'text-emerald-600' : 'text-rose-500'"
                                class="text-sm font-semibold">
                                {{ card.trend >= 0 ? '+' : '' }}{{ card.trend }}%
                            </span>
                        </div>
                        <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">{{ t('otSummary.vsPreviousPeriod') }}</p>
                    </div>
                </div>

                <!-- Charts and leaderboard -->
                <div class="grid gap-4 lg:grid-cols-3">
                    <div
                        class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900 lg:col-span-2">
                        <div class="flex items-center justify-between pb-3">
                            <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('otSummary.overtimeByProject') }}
                            </h3>
                            <span class="text-xs text-gray-500 dark:text-gray-400">{{ t('otSummary.topProjects') }}</span>
                        </div>
                        <VueApexCharts v-if="!isLoading && projectStats.length > 0" type="bar" height="280"
                            :options="projectChartOptions" :series="projectChartSeries" />
                        <div v-else class="flex items-center justify-center h-[280px] text-gray-500 dark:text-gray-400">
                            <span v-if="isLoading">{{ t('otSummary.loadingChart') }}</span>
                            <span v-else>{{ t('otSummary.noDataAvailable') }}</span>
                        </div>
                    </div>
                    <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
                        <div class="flex items-center justify-between pb-3">
                            <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('otSummary.topContributors') }}
                            </h3>
                            <span class="text-xs text-gray-500 dark:text-gray-400">{{ t('otSummary.top5') }}</span>
                        </div>
                        <VueApexCharts v-if="!isLoading && employeeStats.length > 0" type="donut" height="280"
                            :options="employeeChartOptions" :series="employeeChartSeries" />
                        <div v-else class="flex items-center justify-center h-[280px] text-gray-500 dark:text-gray-400">
                            <span v-if="isLoading">{{ t('otSummary.loadingChart') }}</span>
                            <span v-else>{{ t('otSummary.noDataAvailable') }}</span>
                        </div>
                    </div>
                </div>

                <!-- Tables -->
                <div class="grid gap-4 lg:grid-cols-2">
                    <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
                        <div class="flex items-center justify-between pb-3">
                            <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('otSummary.employeeStats') }}</h3>
                            <select v-model.number="employeePageSize"
                                class="h-9 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                                <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} {{ t('common.perPage') }}
                                </option>
                            </select>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="min-w-full text-sm">
                                <thead
                                    class="border-b border-gray-200 text-left text-gray-500 dark:border-gray-800 dark:text-gray-400">
                                    <tr>
                                        <th @click="toggleEmployeeSort('name')"
                                            :aria-sort="employeeSortBy === 'name' ? (employeeSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                                            class="px-3 py-2 cursor-pointer select-none">
                                            {{ t('otSummary.employee') }}<span class="text-gray-400">{{ getSortIcon(employeeSortBy, 'name',
                                                employeeSortOrder) }}</span></th>
                                        <th @click="toggleEmployeeSort('hours')"
                                            :aria-sort="employeeSortBy === 'hours' ? (employeeSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                                            class="px-3 py-2 cursor-pointer select-none">{{ t('otSummary.hours') }}<span
                                                class="text-gray-400">{{
                                                    getSortIcon(employeeSortBy, 'hours', employeeSortOrder)
                                                }}</span></th>
                                        <th @click="toggleEmployeeSort('requests')"
                                            :aria-sort="employeeSortBy === 'requests' ? (employeeSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                                            class="px-3 py-2 cursor-pointer select-none">
                                            {{ t('otSummary.requests') }}<span class="text-gray-400">{{ getSortIcon(employeeSortBy,
                                                'requests',
                                                employeeSortOrder) }}</span></th>
                                        <th @click="toggleEmployeeSort('avgHours')"
                                            :aria-sort="employeeSortBy === 'avgHours' ? (employeeSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                                            class="px-3 py-2 cursor-pointer select-none">{{ t('otSummary.avgHour') }}<span class="text-gray-400">{{ getSortIcon(employeeSortBy, 'avgHours',
                                                employeeSortOrder) }}</span></th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                                    <tr v-for="row in pagedEmployeeStats" :key="row.id"
                                        class="hover:bg-gray-50 dark:hover:bg-white/5">
                                        <td class="px-3 py-2 font-medium text-gray-900 dark:text-white">
                                            <RouterLink :to="employeeDetailRoute(row)"
                                                class="text-brand-600 hover:text-brand-700 dark:text-brand-300">
                                                {{ row.name }}
                                            </RouterLink>
                                        </td>
                                        <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{ row.hours.toFixed(1)
                                        }}h
                                        </td>
                                        <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{ row.requests }}</td>
                                        <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{
                                            row.avgHours.toFixed(2)
                                        }}h</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="mt-3 flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                            <span>{{ t('otSummary.showingRange', { start: employeeRangeStart, end: employeeRangeEnd, total: employeeStats.length }) }}</span>
                            <div class="flex items-center gap-2">
                                <button @click="setEmployeePage(employeePage - 1)" :disabled="employeePage === 1"
                                    class="h-8 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                    {{ t('common.prev') }}
                                </button>
                                <span>{{ t('otSummary.pageOf', { page: employeePage, total: employeeTotalPages }) }}</span>
                                <button @click="setEmployeePage(employeePage + 1)"
                                    :disabled="employeePage === employeeTotalPages"
                                    class="h-8 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                    {{ t('common.next') }}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
                        <div class="flex items-center justify-between pb-3">
                            <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('otSummary.projectStats') }}</h3>
                            <select v-model.number="projectPageSize"
                                class="h-9 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                                <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} {{ t('common.perPage') }}
                                </option>
                            </select>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="min-w-full text-sm">
                                <thead
                                    class="border-b border-gray-200 text-left text-gray-500 dark:border-gray-800 dark:text-gray-400">
                                    <tr>
                                        <th @click="toggleProjectSort('name')"
                                            :aria-sort="projectSortBy === 'name' ? (projectSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                                            class="px-3 py-2 cursor-pointer select-none">
                                            {{ t('otSummary.project') }}<span class="text-gray-400">{{ getSortIcon(projectSortBy, 'name',
                                                projectSortOrder) }}</span>
                                        </th>
                                        <th @click="toggleProjectSort('hours')"
                                            :aria-sort="projectSortBy === 'hours' ? (projectSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                                            class="px-3 py-2 cursor-pointer select-none">{{ t('otSummary.hours') }}<span
                                                class="text-gray-400">{{
                                                    getSortIcon(projectSortBy, 'hours', projectSortOrder) }}</span>
                                        </th>
                                        <th @click="toggleProjectSort('requests')"
                                            :aria-sort="projectSortBy === 'requests' ? (projectSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                                            class="px-3 py-2 cursor-pointer select-none">
                                            {{ t('otSummary.requests') }}<span class="text-gray-400">{{ getSortIcon(projectSortBy,
                                                'requests',
                                                projectSortOrder) }}</span></th>
                                        <th @click="toggleProjectSort('avgHours')"
                                            :aria-sort="projectSortBy === 'avgHours' ? (projectSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                                            class="px-3 py-2 cursor-pointer select-none">{{ t('otSummary.avgHour') }}<span class="text-gray-400">{{ getSortIcon(projectSortBy, 'avgHours',
                                                projectSortOrder)
                                            }}</span></th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                                    <tr v-for="row in pagedProjectStats" :key="row.id"
                                        class="hover:bg-gray-50 dark:hover:bg-white/5">
                                        <td class="px-3 py-2 font-medium text-gray-900 dark:text-white">
                                            <RouterLink :to="projectDetailRoute(row)"
                                                class="text-brand-600 hover:text-brand-700 dark:text-brand-300">
                                                {{ row.name }}
                                            </RouterLink>
                                        </td>
                                        <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{ row.hours.toFixed(1)
                                        }}h
                                        </td>
                                        <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{ row.requests }}</td>
                                        <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{
                                            row.avgHours.toFixed(2)
                                        }}h</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="mt-3 flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                            <span>{{ t('otSummary.showingRange', { start: projectRangeStart, end: projectRangeEnd, total: projectStats.length }) }}</span>
                            <div class="flex items-center gap-2">
                                <button @click="setProjectPage(projectPage - 1)" :disabled="projectPage === 1"
                                    class="h-8 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                    {{ t('common.prev') }}
                                </button>
                                <span>{{ t('otSummary.pageOf', { page: projectPage, total: projectTotalPages }) }}</span>
                                <button @click="setProjectPage(projectPage + 1)"
                                    :disabled="projectPage === projectTotalPages"
                                    class="h-8 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                    {{ t('common.next') }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
import type { ApexOptions } from 'apexcharts'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useI18n } from 'vue-i18n'
import VueApexCharts from 'vue3-apexcharts'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import ChartSkeleton from '@/components/skeletons/ChartSkeleton.vue'
import FilterSkeleton from '@/components/skeletons/FilterSkeleton.vue'
import StatCardSkeleton from '@/components/skeletons/StatCardSkeleton.vue'
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
import { useFlatpickrScroll } from '@/composables/useFlatpickrScroll'
import { useEmployeeStore } from '@/stores/employee'
import { useOvertimeStore } from '@/stores/overtime'
import { useProjectStore } from '@/stores/project'
import { useUIStore } from '@/stores/ui'
import { getSortIcon as _getSortIcon } from '@/utils/getSortIcon'

const employeeStore = useEmployeeStore()
const projectStore = useProjectStore()
const uiStore = useUIStore()
const { t } = useI18n()

interface StatRow {
	id: string | number
	name: string
	hours: number
	requests: number
	avgHours: number
}

interface SummaryCard {
	title: string
	value: string
	trend: number
}

const isLoading = ref(false)

const formatYMD = (d: Date) => {
	const y = d.getFullYear()
	const m = String(d.getMonth() + 1).padStart(2, '0')
	const day = String(d.getDate()).padStart(2, '0')
	return `${y}-${m}-${day}`
}

const getCurrentPeriodRange = () => {
	const today = new Date()
	const start = new Date(today)
	const end = new Date(today)
	if (today.getDate() >= 26) {
		start.setDate(26)
		start.setHours(0, 0, 0, 0)
		end.setMonth(end.getMonth() + 1, 25)
	} else {
		start.setMonth(start.getMonth() - 1, 26)
		start.setHours(0, 0, 0, 0)
		end.setDate(25)
	}
	end.setHours(23, 59, 59, 999)
	return {
		start,
		end,
		rangeString: `${formatYMD(start)} to ${formatYMD(end)}`,
	}
}

// Initialize date filter from UI store (persisted state)
const dateSelectionType = ref<'year-month' | 'custom'>(uiStore.dateFilter.selectionType)
const selectedYear = ref(uiStore.dateFilter.selectedYear)
const selectedMonth = ref<string | number>(uiStore.dateFilter.selectedMonth)
const customDateRange = ref<string>(
	uiStore.dateFilter.customDateRange || getCurrentPeriodRange().rangeString,
)

const overtimeStore = useOvertimeStore()

// Watch and persist date filter changes to UI store + refetch data
watch(
	[dateSelectionType, selectedYear, selectedMonth, customDateRange],
	async () => {
		uiStore.setDateFilter({
			selectionType: dateSelectionType.value,
			selectedYear: selectedYear.value,
			selectedMonth: selectedMonth.value,
			customDateRange: customDateRange.value,
		})

		isLoading.value = true
		try {
			await fetchSummaryData()
		} finally {
			isLoading.value = false
		}
	},
	{ deep: true },
)

const months = computed(() => [
	{ value: 1, label: t('months.january') },
	{ value: 2, label: t('months.february') },
	{ value: 3, label: t('months.march') },
	{ value: 4, label: t('months.april') },
	{ value: 5, label: t('months.may') },
	{ value: 6, label: t('months.june') },
	{ value: 7, label: t('months.july') },
	{ value: 8, label: t('months.august') },
	{ value: 9, label: t('months.september') },
	{ value: 10, label: t('months.october') },
	{ value: 11, label: t('months.november') },
	{ value: 12, label: t('months.december') },
])

const availableYears = computed(() => {
	const current = new Date().getFullYear()
	return Array.from({ length: 5 }, (_v, i) => current - 2 + i)
})

const { flatpickrInstances, attachMonthScroll } = useFlatpickrScroll()
const flatpickrReady = ref(false)

const datePickerOptions = {
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
}

// Helper to safely parse hours (decimal string or number from backend)
const parseHours = (value: string | number | null | undefined): number => {
	if (value === null || value === undefined) return 0
	const num = typeof value === 'string' ? parseFloat(value) : value
	return Number.isNaN(num) ? 0 : num
}

// ── Server-side stats data (replaces client-side aggregation) ──────────
const employeeStatsData = ref<StatRow[]>([])
const projectStatsData = ref<StatRow[]>([])
const summaryCardsData = ref<SummaryCard[]>([
	{ title: t('otSummary.totalOvertimeHours'), value: '0h', trend: 0 },
	{ title: t('otSummary.avgHoursPerRequest'), value: '0h', trend: 0 },
	{ title: t('otSummary.totalRequests'), value: '0', trend: 0 },
	{ title: t('otSummary.totalProjects'), value: '0', trend: 0 },
])

// Expose as computed for template binding
const employeeStats = computed(() => employeeStatsData.value)
const projectStats = computed(() => projectStatsData.value)
const summaryCards = computed(() => summaryCardsData.value)

const formattedPeriod = computed(() => {
	const range = calculateDateRange()
	if (!range) return 'No date range selected'
	const format = (d: Date) =>
		d.toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
		})
	return `${format(range.start)} - ${format(range.end)}`
})

function calculateDateRange(): { start: Date; end: Date } | null {
	if (dateSelectionType.value === 'custom') {
		if (!customDateRange.value) return null
		const dates = customDateRange.value.split(' to ')
		if (dates.length === 2 && dates[0] && dates[1]) {
			return { start: new Date(dates[0]), end: new Date(dates[1]) }
		}
		return null
	}

	const year = Number(selectedYear.value)

	if (selectedMonth.value === 'all') {
		const start = new Date(year - 1, 11, 26)
		const end = new Date(year, 11, 25)
		return { start, end }
	}

	const monthIndex = Number(selectedMonth.value) - 1
	let startMonth: number
	let startYear: number
	let endMonth: number
	let endYear: number

	if (monthIndex === 0) {
		startMonth = 11
		startYear = year - 1
		endMonth = 0
		endYear = year
	} else {
		startMonth = monthIndex - 1
		startYear = year
		endMonth = monthIndex
		endYear = year
	}

	const start = new Date(startYear, startMonth, 26)
	const end = new Date(endYear, endMonth, 25)
	return { start, end }
}

/** Calculate the previous period range (same duration, directly before current) */
function calculatePreviousRange(currentRange: { start: Date; end: Date }): {
	start: string
	end: string
} {
	const duration = currentRange.end.getTime() - currentRange.start.getTime()
	const prevEnd = new Date(currentRange.start.getTime() - 1)
	const prevStart = new Date(prevEnd.getTime() - duration)
	return { start: formatYMD(prevStart), end: formatYMD(prevEnd) }
}

const handleYearMonthChange = () => {
	customDateRange.value = ''
}

const resetToCurrentPeriod = () => {
	const current = getCurrentPeriodRange()
	dateSelectionType.value = 'year-month'
	customDateRange.value = ''
	selectedYear.value = current.end.getFullYear()
	selectedMonth.value = current.end.getMonth() + 1
}

const clearCustomRange = () => {
	customDateRange.value = ''
}

const pageSizeOptions = [5, 10, 20]
const employeePage = ref(1)
const employeePageSize = ref(5)
const projectPage = ref(1)
const projectPageSize = ref(5)

const employeeSortBy = ref<'name' | 'hours' | 'requests' | 'avgHours' | null>(null)
const employeeSortOrder = ref<'asc' | 'desc'>('asc')
const projectSortBy = ref<'name' | 'hours' | 'requests' | 'avgHours' | null>(null)
const projectSortOrder = ref<'asc' | 'desc'>('asc')

const sortedEmployeeStats = computed(() => {
	if (!employeeSortBy.value) return employeeStats.value
	const sorted = [...employeeStats.value].sort((a, b) => {
		let aVal = a[employeeSortBy.value!]
		let bVal = b[employeeSortBy.value!]

		if (typeof aVal === 'string') {
			aVal = aVal.toLowerCase()
			bVal = (bVal as string).toLowerCase()
		}

		if (aVal < bVal) return employeeSortOrder.value === 'asc' ? -1 : 1
		if (aVal > bVal) return employeeSortOrder.value === 'asc' ? 1 : -1
		return 0
	})
	return sorted
})

const sortedProjectStats = computed(() => {
	if (!projectSortBy.value) return projectStats.value
	const sorted = [...projectStats.value].sort((a, b) => {
		let aVal = a[projectSortBy.value!]
		let bVal = b[projectSortBy.value!]

		if (typeof aVal === 'string') {
			aVal = aVal.toLowerCase()
			bVal = (bVal as string).toLowerCase()
		}

		if (aVal < bVal) return projectSortOrder.value === 'asc' ? -1 : 1
		if (aVal > bVal) return projectSortOrder.value === 'asc' ? 1 : -1
		return 0
	})
	return sorted
})

const employeeTotalPages = computed(() =>
	Math.max(1, Math.ceil(employeeStats.value.length / employeePageSize.value)),
)
const projectTotalPages = computed(() =>
	Math.max(1, Math.ceil(projectStats.value.length / projectPageSize.value)),
)

const pagedEmployeeStats = computed(() => {
	const start = (employeePage.value - 1) * employeePageSize.value
	return sortedEmployeeStats.value.slice(start, start + employeePageSize.value)
})

const pagedProjectStats = computed(() => {
	const start = (projectPage.value - 1) * projectPageSize.value
	return sortedProjectStats.value.slice(start, start + projectPageSize.value)
})

const employeeRangeStart = computed(() =>
	employeeStats.value.length === 0 ? 0 : (employeePage.value - 1) * employeePageSize.value + 1,
)
const employeeRangeEnd = computed(() =>
	Math.min(employeeStats.value.length, employeePage.value * employeePageSize.value),
)
const projectRangeStart = computed(() =>
	projectStats.value.length === 0 ? 0 : (projectPage.value - 1) * projectPageSize.value + 1,
)
const projectRangeEnd = computed(() =>
	Math.min(projectStats.value.length, projectPage.value * projectPageSize.value),
)

const setEmployeePage = (page: number) => {
	if (page < 1 || page > employeeTotalPages.value) return
	employeePage.value = page
}

const setProjectPage = (page: number) => {
	if (page < 1 || page > projectTotalPages.value) return
	projectPage.value = page
}

watch([employeePageSize], () => {
	employeePage.value = 1
})

watch([projectPageSize], () => {
	projectPage.value = 1
})

const toggleEmployeeSort = (field: 'name' | 'hours' | 'requests' | 'avgHours') => {
	if (employeeSortBy.value === field) {
		employeeSortOrder.value = employeeSortOrder.value === 'asc' ? 'desc' : 'asc'
	} else {
		employeeSortBy.value = field
		employeeSortOrder.value = 'asc'
	}
}

const toggleProjectSort = (field: 'name' | 'hours' | 'requests' | 'avgHours') => {
	if (projectSortBy.value === field) {
		projectSortOrder.value = projectSortOrder.value === 'asc' ? 'desc' : 'asc'
	} else {
		projectSortBy.value = field
		projectSortOrder.value = 'asc'
	}
}

const getSortIcon = (
	current: 'name' | 'hours' | 'requests' | 'avgHours' | null,
	field: 'name' | 'hours' | 'requests' | 'avgHours',
	order: 'asc' | 'desc',
) => _getSortIcon(field, current, order)

// ── Charts (driven by the server-side stats data) ──────────────────────

const projectChartSeries = computed(() => [
	{ name: 'Hours', data: projectStats.value.map((p) => p.hours) },
])
const projectChartOptions = computed<ApexOptions>(() => ({
	chart: {
		fontFamily: 'Outfit, sans-serif',
		toolbar: {
			show: true,
			tools: {
				download: true,
				selection: false,
				zoom: false,
				zoomin: false,
				zoomout: false,
				pan: false,
				reset: false,
			},
			export: {
				csv: {
					filename: 'overtime-summary-projects',
					headerCategory: 'Project',
				},
				svg: { filename: 'overtime-summary-projects' },
				png: { filename: 'overtime-summary-projects' },
			},
		},
	},
	colors: ['#465fff'],
	plotOptions: { bar: { borderRadius: 6, columnWidth: '45%' } },
	dataLabels: { enabled: false },
	xaxis: {
		categories: projectStats.value.map((p) => p.name),
		labels: { rotateAlways: true, rotate: -20 },
		title: { text: 'Project Name', style: { fontWeight: 600 } },
	},
	yaxis: { title: { text: 'Hours (h)', style: { fontWeight: 600 } } },
	grid: { borderColor: 'rgba(148,163,184,0.2)' },
	legend: { show: false },
	tooltip: { y: { formatter: (val: number) => `${val.toFixed(1)}h` } },
}))

const employeeChartSeries = computed(() => employeeStats.value.slice(0, 5).map((e) => e.hours))
const employeeChartOptions = computed<ApexOptions>(() => ({
	chart: {
		fontFamily: 'Outfit, sans-serif',
		toolbar: {
			show: true,
			tools: {
				download: true,
				selection: false,
				zoom: false,
				zoomin: false,
				zoomout: false,
				pan: false,
				reset: false,
			},
			export: {
				csv: {
					filename: 'overtime-summary-top-employees',
					headerCategory: 'Employee',
				},
				svg: { filename: 'overtime-summary-top-employees' },
				png: { filename: 'overtime-summary-top-employees' },
			},
		},
	},
	labels: employeeStats.value
		.slice(0, 5)
		.map((e, idx) => `#${idx + 1} ${e.name} (${e.hours.toFixed(1)}h)`),
	colors: ['#6366f1', '#22c55e', '#f97316', '#3b82f6', '#a855f7'],
	legend: { position: 'bottom', fontSize: '12px', fontWeight: 500 },
	dataLabels: { enabled: false },
	tooltip: { y: { formatter: (val: number) => `${val.toFixed(1)}h` } },
}))

const toSlug = (name: string) =>
	name
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/(^-|-$)/g, '')

const employeeDetailRoute = (row: StatRow) => ({
	name: 'EmployeeOvertimeDetail',
	params: { id: String(row.id), slug: toSlug(row.name) },
})

const projectDetailRoute = (row: StatRow) => ({
	name: 'ProjectOvertimeDetail',
	params: { id: String(row.id), slug: toSlug(row.name) },
})

// ── Core data-fetching function (uses server-side stats) ────────────────

const fetchSummaryData = async () => {
	const range = calculateDateRange() || getCurrentPeriodRange()
	const start_date = formatYMD(range.start)
	const end_date = formatYMD(range.end)

	// Previous period for trend calculations
	const prevRange = calculatePreviousRange(range)

	// Fetch all three server-side stats endpoints in parallel, with individual error handling
	const [empResult, projResult, summaryResultRaw] = await Promise.allSettled([
		overtimeStore.fetchEmployeeStats({ start_date, end_date }),
		overtimeStore.fetchProjectStats({ start_date, end_date }),
		overtimeStore.fetchSummaryStats({
			start_date,
			end_date,
			prev_start_date: prevRange.start,
			prev_end_date: prevRange.end,
		}),
	])

	const empStats = empResult.status === 'fulfilled' ? empResult.value : []
	const projStats = projResult.status === 'fulfilled' ? projResult.value : []
	const summaryResult = summaryResultRaw.status === 'fulfilled' ? summaryResultRaw.value : null

	if (empResult.status === 'rejected')
		console.error('Employee stats fetch failed:', empResult.reason)
	if (projResult.status === 'rejected')
		console.error('Project stats fetch failed:', projResult.reason)
	if (summaryResultRaw.status === 'rejected')
		console.error('Summary stats fetch failed:', summaryResultRaw.reason)

	// Transform employee stats
	employeeStatsData.value = (empStats || []).map((row) => ({
		id: row.employee,
		name: row.employee_name || `Employee ${row.employee}`,
		hours: parseHours(row.total_hours),
		requests: row.total_requests,
		avgHours: row.total_requests > 0 ? parseHours(row.total_hours) / row.total_requests : 0,
	}))

	// Transform project stats
	projectStatsData.value = (projStats || []).map((row) => ({
		id: row.project,
		name: row.project_name || `Project ${row.project}`,
		hours: parseHours(row.total_hours),
		requests: row.total_requests,
		avgHours: row.total_requests > 0 ? parseHours(row.total_hours) / row.total_requests : 0,
	}))

	// Build summary cards with trend from previous period
	const totalHours = summaryResult ? parseHours(summaryResult.total_hours) : 0
	const totalRequests = summaryResult ? summaryResult.total_requests || 0 : 0
	const avgHours = totalRequests > 0 ? totalHours / totalRequests : 0
	const uniqueProjects = summaryResult ? summaryResult.unique_projects || 0 : 0

	const prev = summaryResult?.previous
	const prevHours = prev ? parseHours(prev.total_hours) : 0
	const prevRequests = prev ? prev.total_requests || 0 : 0
	const prevAvg = prevRequests > 0 ? prevHours / prevRequests : 0

	const calcTrend = (current: number, previous: number) => {
		if (previous === 0) return current > 0 ? 100 : 0
		return Math.round(((current - previous) / previous) * 1000) / 10
	}

	summaryCardsData.value = [
		{
			title: t('otSummary.totalOvertimeHours'),
			value: `${totalHours.toFixed(1)}h`,
			trend: calcTrend(totalHours, prevHours),
		},
		{
			title: t('otSummary.avgHoursPerRequest'),
			value: `${avgHours.toFixed(1)}h`,
			trend: calcTrend(avgHours, prevAvg),
		},
		{
			title: t('otSummary.totalRequests'),
			value: `${totalRequests}`,
			trend: calcTrend(totalRequests, prevRequests),
		},
		{ title: t('otSummary.totalProjects'), value: `${uniqueProjects}`, trend: 0 },
	]

	// Reset table pages
	employeePage.value = 1
	projectPage.value = 1
}

// Fetch data on mount
onMounted(async () => {
	setTimeout(() => {
		flatpickrReady.value = true
	}, 50)

	isLoading.value = true
	try {
		await Promise.all([
			employeeStore.fetchEmployees(),
			projectStore.fetchProjects(),
			fetchSummaryData(),
		])
	} catch (error) {
		console.error('Failed to fetch summary data:', error)
	} finally {
		isLoading.value = false
	}
})

onUnmounted(() => {
	// Cleanup handled by useFlatpickrScroll composable
})
</script>
