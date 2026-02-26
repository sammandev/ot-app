<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between gap-4 mb-6">
        <PageBreadcrumb :page-title="t('pages.projectDetail.title', { name: displayName })"
          :parent-label="t('pages.otSummary.parentLabel')" parent-to="/ot/summary" />
        <RouterLink to="/ot/summary"
          class="inline-flex items-center gap-2 rounded-lg border border-gray-200 dark:border-gray-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5 transition whitespace-nowrap">
          ← {{ t('pages.projectDetail.backToSummary') }}
        </RouterLink>
      </div>

      <!-- Loading State -->
      <template v-if="isLoading">
        <FilterSkeleton :filters="5" />
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCardSkeleton v-for="i in 4" :key="i" />
        </div>
        <div class="grid gap-4 lg:grid-cols-3">
          <ChartSkeleton :height="280" :bars="6" class="lg:col-span-2" />
          <ChartSkeleton :height="280" :bars="3" />
        </div>
        <ChartSkeleton :height="280" :bars="6" />
        <TableSkeleton :rows="8" :columns="4" />
        <TableSkeleton :rows="10" :columns="6" />
      </template>

      <!-- Main Content -->
      <template v-else>
        <!-- Filters -->
        <div ref="filtersRef" :class="[
          'transition-[max-height,opacity] duration-300 ease-in-out',
          isFilterSticky ? 'sticky top-16' : 'relative',
          isStickyBarActive && isFilterSticky
            ? 'z-50 -mx-4 md:-mx-6 lg:border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 shadow-theme-md px-3 py-3 sm:px-4 lg:px-6 lg:py-4'
            : 'rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]'
        ]">
          <div class="grid gap-4 lg:grid-cols-4">
            <!-- Row 1: Project, Date Selection, Year, Month -->
            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('detail.project') }}</label>
              <select v-model="selectedProjectId"
                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                <option v-for="proj in filteredProjectOptions" :key="proj.id" :value="String(proj.id)">
                  {{ proj.name }}
                </option>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('detail.dateSelection')
                }}</label>
              <select v-model="dateSelectionType"
                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                <option value="year-month">{{ t('detail.yearMonth') }}</option>
                <option value="custom">{{ t('detail.customDateRange') }}</option>
              </select>
            </div>

            <template v-if="dateSelectionType === 'year-month'">
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('detail.year') }}</label>
                <select v-model.number="selectedYear" @change="handleYearMonthChange"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                  <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('detail.month') }}</label>
                <select v-model="selectedMonth" @change="handleYearMonthChange"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                  <option value="all">{{ t('detail.allMonths') }}</option>
                  <option v-for="month in months" :key="month.value" :value="month.value">{{
                    month.label
                  }}</option>
                </select>
              </div>
            </template>

            <template v-else>
              <div class="lg:col-span-2 space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('detail.customDateRange')
                  }}</label>
                <div class="relative">
                  <flat-pickr v-if="flatpickrReady" v-model="customDateRange" :config="datePickerOptions"
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
            </template>

            <!-- Row 2: Active Period (col-span-2), Current Period, Stay/Sticky -->
            <div class="lg:col-span-2">
              <div
                class="h-11 flex items-center justify-between rounded-lg border border-brand-200 bg-gradient-to-r from-brand-50 to-blue-50 px-4 py-3 text-sm text-brand-900 shadow-theme-xs dark:border-brand-700/60 dark:from-brand-900/30 dark:to-blue-900/20 dark:text-white">
                <div class="font-semibold">{{ t('detail.activePeriod') }}:</div>
                <div class="font-semibold">{{ formattedPeriod }}</div>
              </div>
            </div>

            <div>
              <button @click="resetToCurrentPeriod"
                class="h-11 w-full rounded-lg border border-brand-300 bg-brand-50 px-4 text-sm font-semibold text-brand-700 shadow-theme-xs transition hover:bg-brand-100 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-100">
                {{ t('detail.currentPeriod') }}
              </button>
            </div>

            <div>
              <button @click="toggleFilterSticky" type="button"
                class="h-11 w-full relative inline-flex rounded-lg border border-gray-300 bg-gray-100 p-1 dark:border-gray-700 dark:bg-gray-800">
                <span :class="[
                  'absolute inset-y-1 w-[calc(50%-4px)] rounded-md shadow-sm transition-transform duration-200',
                  isFilterSticky ? 'left-[calc(50%+2px)] bg-brand-500' : 'left-1 bg-white dark:bg-gray-900'
                ]"></span>
                <span :class="[
                  'relative z-10 flex-1 flex items-center justify-center text-sm font-medium transition-colors duration-200',
                  !isFilterSticky ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'
                ]">
                  {{ t('detail.stay') }}
                </span>
                <span :class="[
                  'relative z-10 flex-1 flex items-center justify-center text-sm font-medium transition-colors duration-200',
                  isFilterSticky ? 'text-white' : 'text-gray-600 dark:text-gray-400'
                ]">
                  {{ t('detail.sticky') }}
                </span>
              </button>
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
              <span :class="card.trend >= 0 ? 'text-emerald-600' : 'text-rose-500'" class="text-sm font-semibold">
                {{ card.trend >= 0 ? '+' : '' }}{{ card.trend }}%
              </span>
            </div>
            <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">{{ t('detail.vsPreviousPeriod') }}</p>
          </div>
        </div>

        <!-- Charts -->
        <div class="grid gap-4 lg:grid-cols-3">
          <div
            class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900 lg:col-span-2">
            <div class="flex flex-col gap-3 pb-3 sm:flex-row sm:items-center sm:justify-between">
              <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('detail.overtimeTrend') }}</h3>
              <div class="inline-flex rounded-lg border border-gray-200 p-1 dark:border-gray-700">
                <button v-for="granularity in trendGranularities" :key="granularity"
                  @click="selectedTrendGranularity = granularity" :class="[
                    'rounded-md px-3 py-1 text-xs font-medium transition',
                    selectedTrendGranularity === granularity
                      ? 'bg-brand-500 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
                  ]">{{ t(`detail.${granularity.toLowerCase()}`) }}</button>
              </div>
            </div>
            <VueApexCharts type="bar" height="280" :options="trendChartOptions" :series="trendChartSeries" />
          </div>
          <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
            <div class="flex items-center justify-between pb-3">
              <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('detail.topEmployees') }}</h3>
            </div>
            <VueApexCharts type="donut" height="280" :options="contributorsChartOptions"
              :series="contributorsChartSeries" />
          </div>
        </div>

        <!-- Top Employees chart -->
        <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <div class="flex items-center justify-between pb-3">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('detail.topEmployees') }}</h3>
            <span class="text-xs text-gray-500 dark:text-gray-400">{{ t('detail.overtimeHoursByEmployee') }}</span>
          </div>
          <VueApexCharts type="bar" height="280" :options="employeesChartOptions" :series="employeesChartSeries" />
        </div>

        <!-- Top Employees table -->
        <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <div class="flex items-center justify-between pb-3">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('detail.totalEmployees') }}</h3>
            <span class="text-xs text-gray-500 dark:text-gray-400">{{ t('detail.basedOnCurrentFilters') }}</span>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead class="border-b border-gray-200 text-left text-gray-500 dark:border-gray-800 dark:text-gray-400">
                <tr>
                  <th class="px-3 py-2">{{ t('detail.employee') }}</th>
                  <th class="px-3 py-2">{{ t('detail.hours') }}</th>
                  <th class="px-3 py-2">{{ t('detail.requests') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                <tr v-for="row in tcPaginatedEmployees" :key="row.slug" class="hover:bg-gray-50 dark:hover:bg-white/5">
                  <td class="px-3 py-2 font-medium text-gray-900 dark:text-white">
                    <RouterLink :to="{ name: 'EmployeeOvertimeDetail', params: { id: row.id, slug: row.slug } }"
                      class="text-brand-600 hover:text-brand-700 dark:text-brand-300">{{ row.name
                      }}
                    </RouterLink>
                  </td>
                  <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{ row.hours.toFixed(1) }}h
                  </td>
                  <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{ row.requests }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div
            class="mt-3 flex flex-col gap-3 border-t border-gray-200 pt-3 text-sm text-gray-700 dark:border-gray-800 dark:text-gray-300 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-center gap-3">
              <p>{{ t('detail.showingRange', {
                start: tcPageRangeStart, end: tcPageRangeEnd, total: topEmployees.length
                }) }}
              </p>
              <select v-model.number="tcPageSize"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                <option v-for="size in tcPageSizeOptions" :key="size" :value="size">{{ size }} {{ t('detail.perPage') }}
                </option>
              </select>
            </div>
            <div class="flex items-center gap-2">
              <button @click="tcGoToPage(tcCurrentPage - 1)" :disabled="tcCurrentPage === 1"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                {{ t('common.prev') }}
              </button>
              <span>{{ t('detail.pageOf', { page: tcCurrentPage, total: tcTotalPages }) }}</span>
              <button @click="tcGoToPage(tcCurrentPage + 1)" :disabled="tcCurrentPage === tcTotalPages"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                {{ t('common.next') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Request History (Project) -->
        <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <div class="flex items-center justify-between pb-3">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('detail.requestHistory') }}</h3>
            <span class="text-xs text-gray-500 dark:text-gray-400">{{ t('detail.basedOnCurrentFilters') }}</span>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead class="border-b border-gray-200 text-left text-gray-500 dark:border-gray-800 dark:text-gray-400">
                <tr>
                  <th @click="phToggleSort('status')" :aria-sort="phSortBy === 'status' ? (phSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'" class="px-3 py-2 cursor-pointer select-none">
                    {{ t('detail.status') }}<span class="text-gray-400">{{ phGetSortIcon('status') }}</span>
                  </th>
                  <th @click="phToggleSort('request_date')" :aria-sort="phSortBy === 'request_date' ? (phSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'" class="px-3 py-2 cursor-pointer select-none">
                    {{ t('detail.date') }}<span class="text-gray-400">{{ phGetSortIcon('request_date') }}</span></th>
                  <th @click="phToggleSort('employee_name')" :aria-sort="phSortBy === 'employee_name' ? (phSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'" class="px-3 py-2 cursor-pointer select-none">
                    {{ t('detail.employee') }}<span class="text-gray-400">{{ phGetSortIcon('employee_name') }}</span>
                  </th>
                  <th @click="phToggleSort('time_in')" :aria-sort="phSortBy === 'time_in' ? (phSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'" class="px-3 py-2 cursor-pointer select-none">
                    {{ t('detail.time') }}<span class="text-gray-400">{{ phGetSortIcon('time_in') }}</span></th>
                  <th @click="phToggleSort('type')" :aria-sort="phSortBy === 'type' ? (phSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'" class="px-3 py-2 cursor-pointer select-none">
                    {{ t('detail.type') }}<span class="text-gray-400">{{ phGetSortIcon('type') }}</span></th>
                  <th @click="phToggleSort('reason')" :aria-sort="phSortBy === 'reason' ? (phSortOrder === 'asc' ? 'ascending' : 'descending') : 'none'" class="px-3 py-2 cursor-pointer select-none">
                    {{ t('detail.reason') }}<span class="text-gray-400">{{ phGetSortIcon('reason') }}</span></th>
                  <th class="px-3 py-2">{{ t('detail.details') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                <tr v-for="req in phPaginatedRequests" :key="req.id"
                  class="hover:bg-gray-50 dark:hover:bg-white/5 align-top">
                  <td class="px-3 py-2">
                    <span v-if="req.status === 'approved'"
                      class="rounded-full bg-green-100 px-2 py-0.5 text-[11px] font-medium text-green-800 dark:bg-green-500/20 dark:text-green-300">{{
                        t('detail.statusApproved') }}</span>
                    <span v-else-if="req.status === 'rejected'"
                      class="rounded-full bg-red-100 px-2 py-0.5 text-[11px] font-medium text-red-800 dark:bg-red-500/20 dark:text-red-300">{{
                        t('detail.statusRejected') }}</span>
                    <span v-else
                      class="rounded-full bg-yellow-100 px-2 py-0.5 text-[11px] font-medium text-yellow-800 dark:bg-yellow-500/20 dark:text-yellow-300">{{
                        t('detail.statusPending') }}</span>
                  </td>
                  <td class="px-3 py-2 whitespace-nowrap text-gray-900 dark:text-white">{{
                    phFormatDate(req.request_date) }}</td>
                  <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{ req.employee_name }}</td>
                  <td class="px-3 py-2 text-gray-700 dark:text-gray-300">
                    <div>{{ formatTime(req.time_in) }} - {{ formatTime(req.time_out) }}</div>
                    <div class="text-xs text-gray-500">({{ displayHours(req.total_hours) }}h)
                    </div>
                  </td>
                  <td class="px-3 py-2">
                    <span v-if="req.is_holiday"
                      class="rounded-full bg-purple-100 px-2 py-0.5 text-[11px] font-medium text-purple-800 dark:bg-purple-500/20 dark:text-purple-300">{{
                        t('detail.holiday') }}</span>
                    <span v-else-if="req.is_weekend"
                      class="rounded-full bg-orange-100 px-2 py-0.5 text-[11px] font-medium text-orange-800 dark:bg-orange-500/20 dark:text-orange-300">{{
                        t('detail.weekend') }}</span>
                    <span v-else
                      class="rounded-full bg-blue-100 px-2 py-0.5 text-[11px] font-medium text-blue-800 dark:bg-blue-500/20 dark:text-blue-300">{{
                        t('detail.weekday') }}</span>
                  </td>
                  <td class="px-3 py-2 text-gray-700 dark:text-gray-300">{{ req.reason }}</td>
                  <td class="px-3 py-2 text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{
                    req.detail
                    || '—' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div
            class="mt-3 flex flex-col gap-3 border-t border-gray-200 pt-3 text-sm text-gray-700 dark:border-gray-800 dark:text-gray-300 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-center gap-3">
              <p>{{ t('detail.showingRange', {
                start: phPageRangeStart, end: phPageRangeEnd, total:
                phSortedRequests.length })
                }}</p>
              <select v-model.number="phPageSize"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                <option v-for="size in phPageSizeOptions" :key="size" :value="size">{{ size }} {{ t('detail.perPage') }}
                </option>
              </select>
            </div>
            <div class="flex items-center gap-2">
              <button @click="phGoToPage(phCurrentPage - 1)" :disabled="phCurrentPage === 1"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                {{ t('common.prev') }}
              </button>
              <span>{{ t('detail.pageOf', { page: phCurrentPage, total: phTotalPages }) }}</span>
              <button @click="phGoToPage(phCurrentPage + 1)" :disabled="phCurrentPage === phTotalPages"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                {{ t('common.next') }}
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import type { ApexOptions } from 'apexcharts'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import ChartSkeleton from '@/components/skeletons/ChartSkeleton.vue'
import FilterSkeleton from '@/components/skeletons/FilterSkeleton.vue'
import StatCardSkeleton from '@/components/skeletons/StatCardSkeleton.vue'
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
import { useFlatpickrScroll } from '@/composables/useFlatpickrScroll'
import type { OvertimeRequest } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useEmployeeStore } from '@/stores/employee'
import { useOvertimeStore } from '@/stores/overtime'
import { useProjectStore } from '@/stores/project'
import { useUIStore } from '@/stores/ui'

const { t } = useI18n()

const normalizeHours = (value: OvertimeRequest['total_hours']) => {
	if (typeof value === 'string') {
		const parsed = parseFloat(value)
		return Number.isFinite(parsed) ? parsed : 0
	}
	if (typeof value === 'number') {
		return Number.isFinite(value) ? value : 0
	}
	return 0
}

const displayHours = (value: OvertimeRequest['total_hours']) => normalizeHours(value).toFixed(2)
const formatTime = (time: string | null | undefined) => {
	if (!time) return '—'
	return time.replace(/:\d{2}$/, '')
}

/**
 * Get the period label and index for a given date.
 * Periods run from 26th of previous month to 25th of current month.
 */
const getPeriodForDate = (date: Date): { month: number; year: number; label: string } => {
	const day = date.getDate()
	let month = date.getMonth()
	let year = date.getFullYear()

	if (day >= 26) {
		month = (month + 1) % 12
		if (month === 0) year += 1
	}

	const label = new Date(year, month, 1).toLocaleString('en-US', {
		month: 'short',
	})
	return { month, year, label }
}

/**
 * Generate period buckets between two dates.
 */
const generatePeriodBuckets = (
	start: Date,
	end: Date,
): Array<{ month: number; year: number; label: string }> => {
	const buckets: Array<{ month: number; year: number; label: string }> = []
	const startPeriod = getPeriodForDate(start)
	const endPeriod = getPeriodForDate(end)

	const current = { month: startPeriod.month, year: startPeriod.year }

	while (
		current.year < endPeriod.year ||
		(current.year === endPeriod.year && current.month <= endPeriod.month)
	) {
		const label = new Date(current.year, current.month, 1).toLocaleString('en-US', {
			month: 'short',
		})
		buckets.push({ month: current.month, year: current.year, label })

		current.month += 1
		if (current.month > 11) {
			current.month = 0
			current.year += 1
		}
	}

	return buckets
}

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

interface ProjectData {
	id: string
	name: string
	employees: Array<{
		id: string
		name: string
		hours: number
		requests: number
	}>
	trend: number[]
}

interface SummaryCard {
	title: string
	value: string
	trend: number
}

const router = useRouter()
const route = useRoute()
const overtimeStore = useOvertimeStore()
const projectStore = useProjectStore()
const employeeStore = useEmployeeStore()
const uiStore = useUIStore()
const authStore = useAuthStore()

// Filtered and sorted project options for dropdown
const filteredProjectOptions = computed(() => {
	let projects = projectStore.projects.filter((proj) => proj.is_enabled !== false)

	// For non-admin users, show only projects they have overtime requests for
	if (!authStore.isPtbAdmin) {
		const workerId = authStore.user?.worker_id
		if (workerId) {
			// Find employee by worker_id
			const userEmployee = employeeStore.employees.find((emp) => emp.emp_id === workerId)
			if (userEmployee) {
				// Get projects the user has OT requests for
				const userProjectIds = new Set(
					overtimeStore.requests
						.filter((req) => req.employee === userEmployee.id)
						.map((req) => req.project),
				)
				projects = projects.filter((proj) => userProjectIds.has(proj.id))
			}
		}
	}

	// Sort alphabetically by name
	return [...projects].sort((a, b) => a.name.localeCompare(b.name))
})

// Compute projectsData from API data instead of mock data
const projectsData = computed<ProjectData[]>(() => {
	const projects = projectStore.projects
	const employees = employeeStore.employees
	const requests = overtimeStore.requests
	const range = calculateDateRange()

	return projects.map((proj) => {
		// Filter requests for this project within the date range
		const projRequests = requests.filter((req) => {
			if (req.project !== proj.id) return false
			if (req.status === 'rejected') return false
			if (!req.request_date) return false
			if (!range) return true
			return isWithinRange(req.request_date, range)
		})

		// Calculate employee breakdown
		const employeeMap = new Map<
			number,
			{ id: string; name: string; hours: number; requests: number }
		>()
		projRequests.forEach((req) => {
			if (req.employee) {
				const existing = employeeMap.get(req.employee)
				const hours = normalizeHours(req.total_hours)

				if (existing) {
					existing.hours += hours
					existing.requests += 1
				} else {
					const emp = employees.find((e) => e.id === req.employee)
					employeeMap.set(req.employee, {
						id: String(req.employee),
						name: emp?.name || req.employee_name || `Employee ${req.employee}`,
						hours,
						requests: 1,
					})
				}
			}
		})

		// Calculate trend based on selected date range (group by period: 26th-25th)
		const trend: number[] = []
		if (range) {
			// Generate period buckets based on actual period boundaries
			const periodBuckets = generatePeriodBuckets(range.start, range.end)

			for (const bucket of periodBuckets) {
				const periodRequests = projRequests.filter((req) => {
					const reqPeriod = getPeriodForDate(new Date(req.request_date))
					return reqPeriod.month === bucket.month && reqPeriod.year === bucket.year
				})
				const periodHours = periodRequests.reduce(
					(sum, req) => sum + normalizeHours(req.total_hours),
					0,
				)
				trend.push(periodHours)
			}
		} else {
			// Fallback: last 6 periods from now
			const now = new Date()
			for (let i = 5; i >= 0; i--) {
				const targetPeriod = getPeriodForDate(new Date(now.getFullYear(), now.getMonth() - i, 15))
				const periodRequests = projRequests.filter((req) => {
					const reqPeriod = getPeriodForDate(new Date(req.request_date))
					return reqPeriod.month === targetPeriod.month && reqPeriod.year === targetPeriod.year
				})
				const periodHours = periodRequests.reduce(
					(sum, req) => sum + normalizeHours(req.total_hours),
					0,
				)
				trend.push(periodHours)
			}
		}

		return {
			id: String(proj.id),
			name: proj.name,
			employees: Array.from(employeeMap.values()).sort((a, b) => b.hours - a.hours),
			trend,
		}
	})
})

const toSlug = (name: string) =>
	name
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/(^-|-$)/g, '')

const isLoading = ref(false)
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

const { flatpickrInstances, attachMonthScroll, destroyFlatpickrs } = useFlatpickrScroll()

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

// Control flatpickr mounting to prevent "Element not found" error
const flatpickrReady = ref(false)

const selectedProjectId = ref<string>(String(route.params.id || (projectsData.value[0]?.id ?? '')))
// Initialize date filter from UI store (persisted state)
const dateSelectionType = ref<'year-month' | 'custom'>(uiStore.dateFilter.selectionType)
const selectedYear = ref(uiStore.dateFilter.selectedYear)
const selectedMonth = ref<string | number>(uiStore.dateFilter.selectedMonth)
const customDateRange = ref<string>(
	uiStore.dateFilter.customDateRange || getCurrentPeriodRange().rangeString,
)
const isFilterSticky = ref(true)

// Watch and persist date filter changes to UI store
watch(
	[dateSelectionType, selectedYear, selectedMonth, customDateRange],
	() => {
		uiStore.setDateFilter({
			selectionType: dateSelectionType.value,
			selectedYear: selectedYear.value,
			selectedMonth: selectedMonth.value,
			customDateRange: customDateRange.value,
		})
	},
	{ deep: true },
)

const toggleFilterSticky = () => {
	isFilterSticky.value = !isFilterSticky.value
}

const selectedProject = computed<ProjectData>(() => {
	const found = projectsData.value.find((proj) => proj.id === selectedProjectId.value)
	if (found) return found
	if (projectsData.value.length > 0) return projectsData.value[0]!
	// Return a default empty project to prevent undefined errors
	return {
		id: '',
		name: '',
		employees: [],
		trend: [],
	}
})

watch(selectedProjectId, async (newId) => {
	const proj = projectsData.value.find((p) => p.id === newId)
	if (proj && (route.params.id !== proj.id || route.params.slug !== toSlug(proj.name))) {
		const scrollY = window.scrollY
		router
			.replace({
				name: 'ProjectOvertimeDetail',
				params: { id: proj.id, slug: toSlug(proj.name) },
			})
			.then(() => {
				window.scrollTo(0, scrollY)
			})
		// Show loading skeleton when project changes
		isLoading.value = true
		try {
			await fetchOvertimeData()
		} finally {
			isLoading.value = false
		}
	}
})

const toTitle = (slug: string) => slug.replace(/-/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase())
const displayName = computed(
	() => selectedProject.value?.name || toTitle(String(route.params.slug || 'Project')),
)

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

const isWithinRange = (dateStr: string, range: { start: Date; end: Date } | null) => {
	if (!range) return true
	const d = new Date(dateStr)
	return d >= range.start && d <= range.end
}

const handleYearMonthChange = () => {
	customDateRange.value = ''
}

const resetToCurrentPeriod = () => {
	const current = getCurrentPeriodRange()
	// Stay on Year & Month selection mode (don't change to custom)
	dateSelectionType.value = 'year-month'
	customDateRange.value = ''
	// Use end date (25th) to determine the current period month/year
	// because the period ends on the 25th of the target month
	selectedYear.value = current.end.getFullYear()
	selectedMonth.value = current.end.getMonth() + 1
}

const fetchOvertimeData = async () => {
	const range = calculateDateRange() || getCurrentPeriodRange()
	const projId = Number(selectedProjectId.value)
	await overtimeStore.fetchRequests(
		{
			start_date: formatYMD(range.start),
			end_date: formatYMD(range.end),
			page_size: 500,
			ordering: '-request_date',
			...(projId ? { project: projId } : {}),
		},
		true,
	)
}

watch([dateSelectionType, customDateRange, selectedYear, selectedMonth], async () => {
	isLoading.value = true
	try {
		await fetchOvertimeData()
	} finally {
		isLoading.value = false
	}
})

// Sticky state for filters: header-like style only when stuck
const isStickyBarActive = ref(false)
const filtersRef = ref<HTMLElement | null>(null)
let stickyTopPx = 0
const updateStickyState = () => {
	const el = filtersRef.value
	if (!el) return
	if (!stickyTopPx) {
		const topStr = getComputedStyle(el).top
		const parsed = Number.parseFloat(topStr)
		stickyTopPx = Number.isFinite(parsed) ? parsed : 64
	}
	const rect = el.getBoundingClientRect()
	isStickyBarActive.value = rect.top <= stickyTopPx + 0.5
}

onMounted(async () => {
	isLoading.value = true

	updateStickyState()
	window.addEventListener('scroll', updateStickyState, { passive: true })
	window.addEventListener('resize', updateStickyState)

	// Enable flatpickr after DOM is ready
	await nextTick()
	flatpickrReady.value = true

	// Load API data with error handling
	try {
		await Promise.all([
			employeeStore.fetchEmployees(),
			projectStore.fetchProjects(),
			fetchOvertimeData(),
		])
	} catch (error) {
		console.error('Failed to load data:', error)
	} finally {
		isLoading.value = false
	}
})

onUnmounted(() => {
	window.removeEventListener('scroll', updateStickyState)
	window.removeEventListener('resize', updateStickyState)
	destroyFlatpickrs()
})

const summaryCards = computed<SummaryCard[]>(() => {
	const proj = selectedProject.value
	if (!proj || !proj.id) {
		return [
			{ title: t('detail.totalOvertimeHours'), value: '0h', trend: 0 },
			{ title: t('detail.avgHoursPerRequest'), value: '0h', trend: 0 },
			{ title: t('detail.totalRequests'), value: '0', trend: 0 },
			{ title: t('detail.activeEmployees'), value: '0', trend: 0 },
		]
	}
	// Use actual trend data from real requests (not interpolated)
	const realTrend = proj.trend || []
	const totalHours = realTrend.reduce((sum, val) => sum + val, 0)
	const totalRequests = proj.employees.reduce((sum, emp) => sum + emp.requests, 0)
	const avgHoursPerRequest = totalRequests ? totalHours / totalRequests : 0

	// Calculate previous period for trend
	const midPoint = Math.floor(realTrend.length / 2)
	const currentPeriodHours = realTrend.slice(midPoint).reduce((s, v) => s + v, 0)
	const previousPeriodHours = realTrend.slice(0, midPoint).reduce((s, v) => s + v, 0)
	const hoursTrend =
		previousPeriodHours === 0
			? currentPeriodHours > 0
				? 100
				: 0
			: ((currentPeriodHours - previousPeriodHours) / previousPeriodHours) * 100

	return [
		{
			title: t('detail.totalOvertimeHours'),
			value: `${totalHours.toFixed(1)}h`,
			trend: Math.round(hoursTrend * 10) / 10,
		},
		{
			title: t('detail.avgHoursPerRequest'),
			value: `${avgHoursPerRequest.toFixed(1)}h`,
			trend: 0,
		},
		{ title: t('detail.totalRequests'), value: `${totalRequests}`, trend: 0 },
		{
			title: t('detail.activeEmployees'),
			value: `${proj.employees.length}`,
			trend: 0,
		},
	]
})

const trendGranularities = ['Days', 'Weeks', 'Months'] as const
type TrendGranularity = (typeof trendGranularities)[number]
const selectedTrendGranularity = ref<TrendGranularity>('Months')

const getTrendData = computed(() => {
	const range = calculateDateRange()
	const requests = overtimeStore.requests
	const projectId = selectedProject.value?.id

	// Filter requests for this project within the date range
	const projRequests = requests.filter((req) => {
		if (String(req.project) !== projectId) return false
		if (req.status === 'rejected') return false
		if (!req.request_date) return false
		if (!range) return true
		const d = new Date(req.request_date)
		return d >= range.start && d <= range.end
	})

	if (selectedTrendGranularity.value === 'Days') {
		// Group by day
		const labels: string[] = []
		const data: number[] = []

		if (range) {
			const dayMs = 24 * 60 * 60 * 1000
			const days = Math.max(1, Math.floor((range.end.getTime() - range.start.getTime()) / dayMs) + 1)

			for (let i = 0; i < days; i++) {
				const dayStart = new Date(range.start.getTime() + i * dayMs)
				dayStart.setHours(0, 0, 0, 0)
				const dayEnd = new Date(dayStart)
				dayEnd.setHours(23, 59, 59, 999)

				const dayRequests = projRequests.filter((r) => {
					const d = new Date(r.request_date)
					return d >= dayStart && d <= dayEnd
				})
				const dayHours = dayRequests.reduce((sum, r) => sum + normalizeHours(r.total_hours), 0)

				labels.push(`${dayStart.getMonth() + 1}/${dayStart.getDate()}`)
				data.push(Number(dayHours.toFixed(2)))
			}
		}
		return { data, categories: labels }
	} else if (selectedTrendGranularity.value === 'Weeks') {
		// Group by week
		const labels: string[] = []
		const data: number[] = []

		if (range) {
			const weekMs = 7 * 24 * 60 * 60 * 1000
			const weeks = Math.max(1, Math.ceil((range.end.getTime() - range.start.getTime()) / weekMs))

			for (let i = 0; i < weeks; i++) {
				const weekStart = new Date(range.start.getTime() + i * weekMs)
				weekStart.setHours(0, 0, 0, 0)
				const weekEnd = new Date(weekStart.getTime() + weekMs - 1)

				const weekRequests = projRequests.filter((r) => {
					const d = new Date(r.request_date)
					return d >= weekStart && d <= weekEnd
				})
				const weekHours = weekRequests.reduce((sum, r) => sum + normalizeHours(r.total_hours), 0)

				labels.push(`Week ${i + 1}`)
				data.push(Number(weekHours.toFixed(2)))
			}
		}
		return { data, categories: labels }
	} else {
		// Group by period (26th-25th) for accurate overtime tracking
		const labels: string[] = []
		const data: number[] = []

		if (range) {
			const periodBuckets = generatePeriodBuckets(range.start, range.end)

			for (const bucket of periodBuckets) {
				const periodRequests = projRequests.filter((r) => {
					const reqPeriod = getPeriodForDate(new Date(r.request_date))
					return reqPeriod.month === bucket.month && reqPeriod.year === bucket.year
				})
				const periodHours = periodRequests.reduce((sum, r) => sum + normalizeHours(r.total_hours), 0)

				labels.push(bucket.label)
				data.push(Number(periodHours.toFixed(2)))
			}
		}
		return { data, categories: labels }
	}
})

const trendChartSeries = computed(() => [{ name: 'Hours', data: getTrendData.value.data }])
const trendChartOptions = computed<ApexOptions>(() => ({
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
					filename: `project-${(selectedProject.value?.name || 'unknown').replace(/\s+/g, '-')}-trend-${selectedTrendGranularity.value.toLowerCase()}`,
					headerCategory:
						selectedTrendGranularity.value === 'Months'
							? 'Month'
							: selectedTrendGranularity.value.slice(0, -1),
				},
				svg: {
					filename: `project-trend-${selectedTrendGranularity.value.toLowerCase()}`,
				},
				png: {
					filename: `project-trend-${selectedTrendGranularity.value.toLowerCase()}`,
				},
			},
		},
	},
	colors: ['#465fff'],
	plotOptions: { bar: { borderRadius: 6, columnWidth: '45%' } },
	dataLabels: { enabled: false },
	xaxis: {
		categories: getTrendData.value.categories,
		title: {
			text:
				selectedTrendGranularity.value === 'Months'
					? 'Month'
					: selectedTrendGranularity.value.slice(0, -1),
			style: { fontWeight: 600 },
		},
	},
	yaxis: { title: { text: 'Overtime Hours (h)', style: { fontWeight: 600 } } },
	grid: { borderColor: 'rgba(148,163,184,0.2)' },
	tooltip: { y: { formatter: (val: number) => `${val.toFixed(1)}h` } },
}))

const phFilteredRequests = computed(() => {
	const range = calculateDateRange()
	if (!range) return phRequests.value
	return phRequests.value.filter((r) => {
		const d = new Date(r.request_date)
		return d >= range.start && d <= range.end
	})
})

const contributorsChartSeries = computed(() => {
	if (!selectedProject.value || !selectedProject.value.id) return []
	const fullHours = selectedProject.value.employees.reduce((s, e) => s + e.hours, 0)
	const filteredHours = getTrendData.value.data.reduce((s, v) => s + v, 0)
	const ratio = fullHours > 0 ? filteredHours / fullHours : 1
	return selectedProject.value.employees.map((e) => e.hours * ratio)
})
const contributorsChartOptions = computed<ApexOptions>(() => ({
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
					filename: `project-${(selectedProject.value?.name || 'unknown').replace(/\s+/g, '-')}-contributors`,
					headerCategory: 'Employee',
				},
				svg: { filename: `project-contributors` },
				png: { filename: `project-contributors` },
			},
		},
	},
	labels: (selectedProject.value?.employees || []).map((e) => e.name),
	colors: ['#6366f1', '#22c55e', '#f97316', '#3b82f6', '#a855f7'],
	legend: { position: 'bottom' },
	dataLabels: { enabled: false },
	tooltip: { y: { formatter: (val: number) => `${val.toFixed(1)}h` } },
}))

const topEmployees = computed(() => {
	if (!selectedProject.value || !selectedProject.value.id) return []
	const fullHours = selectedProject.value.employees.reduce((s, e) => s + e.hours, 0)
	const filteredHours = getTrendData.value.data.reduce((s, v) => s + v, 0)
	const ratio = fullHours > 0 ? filteredHours / fullHours : 1
	return selectedProject.value.employees.map((emp) => ({
		...emp,
		hours: emp.hours * ratio,
		slug: toSlug(emp.name),
	}))
})
const tcPageSizeOptions = [5, 10, 20, 50]
const tcPageSize = ref(5)
const tcCurrentPage = ref(1)
const tcTotalPages = computed(() =>
	Math.max(1, Math.ceil(topEmployees.value.length / tcPageSize.value)),
)
const tcPaginatedEmployees = computed(() => {
	const start = (tcCurrentPage.value - 1) * tcPageSize.value
	const end = start + tcPageSize.value
	return topEmployees.value.slice(start, end)
})
const tcPageRangeStart = computed(() =>
	topEmployees.value.length === 0 ? 0 : (tcCurrentPage.value - 1) * tcPageSize.value + 1,
)
const tcPageRangeEnd = computed(() =>
	Math.min(topEmployees.value.length, tcCurrentPage.value * tcPageSize.value),
)
const tcGoToPage = (page: number) => {
	if (page < 1 || page > tcTotalPages.value) return
	tcCurrentPage.value = page
}
watch([tcPageSize, () => topEmployees.value.length], () => {
	tcCurrentPage.value = 1
})

const employeesChartSeries = computed(() => [
	{ name: 'Hours', data: topEmployees.value.map((e) => e.hours) },
])
const employeesChartOptions = computed<ApexOptions>(() => ({
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
					filename: `project-${(selectedProject.value?.name || 'unknown').replace(/\s+/g, '-')}-top-employees`,
					headerCategory: 'Employee',
				},
				svg: { filename: `project-top-employees` },
				png: { filename: `project-top-employees` },
			},
		},
	},
	colors: ['#465fff'],
	plotOptions: {
		bar: { borderRadius: 6, columnWidth: '45%', horizontal: false },
	},
	dataLabels: { enabled: false },
	xaxis: {
		categories: topEmployees.value.map((e) => e.name),
		labels: { rotateAlways: true, rotate: -20 },
		title: { text: 'Employee Name', style: { fontWeight: 600 } },
	},
	yaxis: {
		title: { text: 'Overtime Hours (h)', style: { fontWeight: 600 } },
		labels: { formatter: (val: number) => Math.floor(val).toString() },
		forceNiceScale: true,
		decimalsInFloat: 0,
	},
	grid: { borderColor: 'rgba(148,163,184,0.2)' },
	tooltip: { y: { formatter: (val: number) => `${val.toFixed(1)}h` } },
}))

// Use API data from stores already initialized above
const phRequests = computed(() => {
	const projectId = selectedProject.value?.id
	if (!projectId) return []
	return overtimeStore.requests.filter((r) => String(r.project) === projectId)
})

import { getSortIcon as _getSortIcon } from '@/utils/getSortIcon'

const phSortBy = ref<
	'request_date' | 'employee_name' | 'time_in' | 'type' | 'reason' | 'status' | null
>(null)
const phSortOrder = ref<'asc' | 'desc'>('asc')
const phPageSizeOptions = [5, 10, 20, 50]
const phPageSize = ref(10)
const phCurrentPage = ref(1)
const phTypeOf = (r: OvertimeRequest) =>
	r.is_holiday ? 'Holiday' : r.is_weekend ? 'Weekend' : 'Weekday'
const phFieldOf = (
	r: OvertimeRequest,
	key: 'request_date' | 'employee_name' | 'time_in' | 'reason' | 'status',
): string => {
	switch (key) {
		case 'request_date':
			return r.request_date
		case 'employee_name':
			return r.employee_name || ''
		case 'time_in':
			return r.time_in
		case 'reason':
			return r.reason || ''
		case 'status':
			return r.status || 'pending'
	}
}
const phSortedRequests = computed(() => {
	if (!phSortBy.value) return phFilteredRequests.value
	const key = phSortBy.value
	const sorted = [...phFilteredRequests.value].sort((a, b) => {
		let aVal: string
		let bVal: string
		if (key === 'type') {
			aVal = phTypeOf(a)
			bVal = phTypeOf(b)
		} else {
			aVal = phFieldOf(a, key)
			bVal = phFieldOf(b, key)
		}
		aVal = aVal.toLowerCase()
		bVal = bVal.toLowerCase()
		if (aVal < bVal) return phSortOrder.value === 'asc' ? -1 : 1
		if (aVal > bVal) return phSortOrder.value === 'asc' ? 1 : -1
		return 0
	})
	return sorted
})
const phTotalPages = computed(() =>
	Math.max(1, Math.ceil(phSortedRequests.value.length / phPageSize.value)),
)
const phPaginatedRequests = computed(() => {
	const start = (phCurrentPage.value - 1) * phPageSize.value
	const end = start + phPageSize.value
	return phSortedRequests.value.slice(start, end)
})
const phPageRangeStart = computed(() =>
	phSortedRequests.value.length === 0 ? 0 : (phCurrentPage.value - 1) * phPageSize.value + 1,
)
const phPageRangeEnd = computed(() =>
	Math.min(phSortedRequests.value.length, phCurrentPage.value * phPageSize.value),
)
const phToggleSort = (
	field: 'request_date' | 'employee_name' | 'time_in' | 'type' | 'reason' | 'status',
) => {
	if (phSortBy.value === field) {
		if (phSortOrder.value === 'asc') phSortOrder.value = 'desc'
		else phSortBy.value = null
	} else {
		phSortBy.value = field
		phSortOrder.value = 'asc'
	}
}
const phGetSortIcon = (
	field: 'request_date' | 'employee_name' | 'time_in' | 'type' | 'reason' | 'status',
) => _getSortIcon(field, phSortBy, phSortOrder)
const phGoToPage = (page: number) => {
	if (page < 1 || page > phTotalPages.value) return
	phCurrentPage.value = page
}
watch([phPageSize, () => phSortedRequests.value.length], () => {
	phCurrentPage.value = 1
})
const phFormatDate = (ds: string) =>
	new Date(ds).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
	})
</script>

<style scoped></style>
