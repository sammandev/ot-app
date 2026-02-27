<!-- @vue/component -->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-semibold text-brand-500">{{ t('pages.otHistory.category') }}</p>
          <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.otHistory.title') }}</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.otHistory.subtitle') }}</p>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
        <div class="space-y-3">
          <!-- Date Selection Row -->
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                t('otHistory.dateSelection') }}</label>
              <select v-model="dateSelectionType"
                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                <option value="year-month">{{ t('otHistory.yearMonth') }}</option>
                <option value="custom">{{ t('otHistory.customDateRange') }}</option>
              </select>
            </div>
            <template v-if="dateSelectionType === 'year-month'">
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.year')
                }}</label>
                <select v-model.number="selectedYear"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                  <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.month')
                }}</label>
                <select v-model="selectedMonth"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                  <option value="all">{{ t('months.allMonths') }}</option>
                  <option v-for="month in months" :key="month.value" :value="month.value">{{
                    month.label }}</option>
                </select>
              </div>
              <div class="flex items-end">
                <button @click="resetToCurrentMonth"
                  class="h-11 w-full rounded-lg border border-brand-300 bg-brand-50 px-4 text-sm font-semibold text-brand-700 shadow-theme-xs transition hover:bg-brand-100 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-100">
                  {{ t('otHistory.currentMonth') }}
                </button>
              </div>
            </template>
            <template v-else>
              <div class="sm:col-span-2 lg:col-span-3">
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.customDateRange') }}</label>
                <div class="relative">
                  <flat-pickr v-model="customDateRange" :config="customDatePickerOptions"
                    class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 pr-11 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                    placeholder="Select custom date range" />
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
          </div>

          <!-- Filters Row -->
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <select v-model="statusFilter"
              class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
              <option value="">{{ t('otHistory.allStatus') }}</option>
              <option value="pending">{{ t('otHistory.pending') }}</option>
              <option value="approved">{{ t('otHistory.approved') }}</option>
              <option value="rejected">{{ t('otHistory.rejected') }}</option>
            </select>
            <select v-model="employeeFilter"
              class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:opacity-60 disabled:cursor-not-allowed"
              :disabled="!isAdmin">
              <option value="">{{ t('otHistory.allEmployees') }}</option>
              <option v-for="employee in employeeOptions" :key="employee" :value="employee">{{ employee }}
              </option>
            </select>
            <select v-model="projectFilter"
              class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
              <option value="">{{ t('otHistory.allProjects') }}</option>
              <option v-for="project in projectOptions" :key="project" :value="project">{{ project }}
              </option>
            </select>
            <select v-model="departmentFilter"
              class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
              <option value="">{{ t('otHistory.allDepartments') }}</option>
              <option v-for="dept in departmentOptions" :key="dept" :value="dept">{{ dept }}</option>
            </select>
          </div>

          <!-- Search and Reset Row -->
          <div class="flex gap-3">
            <input v-model="searchQuery" type="text" :placeholder="t('otHistory.searchPlaceholder')"
              class="dark:bg-dark-900 h-11 flex-1 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300" />
            <button @click="handleReset"
              class="h-11 whitespace-nowrap rounded-lg border border-gray-300 bg-white px-5 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.reset') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <TableSkeleton v-if="isLoading" :rows="10" :columns="8" />

      <!-- Empty State -->
      <div v-else-if="paginatedRequests.length === 0"
        class="rounded-2xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-white/[0.03]">
        <p class="text-gray-500 dark:text-gray-400">{{ t('otHistory.noRequests') }}</p>
      </div>

      <!-- Requests Table -->
      <div v-else
        class="flex flex-col rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
        style="max-height: calc(100vh - 200px)">

        <!-- Bulk Action Bar (visible only to PTB admins when items are selected) -->
        <div v-if="isAdmin && selectedRequests.length > 0"
          class="flex-none flex items-center justify-between gap-4 border-b border-gray-200 bg-brand-50 px-6 py-3 dark:border-gray-800 dark:bg-brand-500/10">
          <span class="text-sm font-medium text-brand-700 dark:text-brand-300">
            {{ t('otHistory.requestsSelected', { count: selectedRequests.length }) }}
          </span>
          <div class="flex gap-2">
            <button @click="handleBulkApprove" :disabled="isBulkUpdating"
              class="h-9 rounded-lg bg-emerald-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-emerald-700 focus:outline-hidden focus:ring-3 focus:ring-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-60">
              {{ isBulkUpdating ? t('common.processing') : t('otHistory.approveSelected') }}
            </button>
            <button @click="handleBulkReject" :disabled="isBulkUpdating"
              class="h-9 rounded-lg bg-rose-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-rose-700 focus:outline-hidden focus:ring-3 focus:ring-rose-500/20 disabled:cursor-not-allowed disabled:opacity-60">
              {{ isBulkUpdating ? t('common.processing') : t('otHistory.rejectSelected') }}
            </button>
            <button @click="clearSelection"
              class="h-9 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-700 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.clear') }}
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-auto min-h-0">
          <table class="w-full text-sm">
            <thead
              class="sticky top-0 z-10 border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900/90 backdrop-blur-sm">
              <tr>
                <!-- Checkbox column (PTB admin only) -->
                <th v-if="isAdmin" class="w-12 px-4 py-4">
                  <input type="checkbox" :checked="isAllCurrentPageSelected" :indeterminate="isPartiallySelected"
                    @change="toggleSelectAll"
                    class="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800" />
                </th>
                <th @click="toggleSort('request_date')" @keydown.enter="toggleSort('request_date')" tabindex="0"
                  :aria-sort="sortBy === 'request_date' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                  class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                  {{ t('otHistory.date') }}<span class="text-gray-400">{{ getSortIcon('request_date') }}</span></th>
                <th @click="toggleSort('employee_name')" @keydown.enter="toggleSort('employee_name')" tabindex="0"
                  :aria-sort="sortBy === 'employee_name' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                  class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                  {{ t('otHistory.employee') }}<span class="text-gray-400">{{ getSortIcon('employee_name') }}</span>
                </th>
                <th @click="toggleSort('project_name')" @keydown.enter="toggleSort('project_name')" tabindex="0"
                  :aria-sort="sortBy === 'project_name' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                  class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                  {{ t('otHistory.project') }}<span class="text-gray-400">{{ getSortIcon('project_name') }}</span></th>
                <th @click="toggleSort('time_start')" @keydown.enter="toggleSort('time_start')" tabindex="0"
                  :aria-sort="sortBy === 'time_start' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                  class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                  {{ t('otHistory.time') }}<span class="text-gray-400">{{ getSortIcon('time_start') }}</span></th>
                <th @click="toggleSort('total_hours')" @keydown.enter="toggleSort('total_hours')" tabindex="0"
                  :aria-sort="sortBy === 'total_hours' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                  class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                  {{ t('otHistory.hours') }}<span class="text-gray-400">{{ getSortIcon('total_hours') }}</span></th>
                <th @click="toggleSort('type')" @keydown.enter="toggleSort('type')" tabindex="0"
                  :aria-sort="sortBy === 'type' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                  class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                  {{ t('otHistory.type') }}<span class="text-gray-400">{{ getSortIcon('type') }}</span></th>
                <th @click="toggleSort('status')" @keydown.enter="toggleSort('status')" tabindex="0"
                  :aria-sort="sortBy === 'status' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'"
                  class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                  {{ t('otHistory.status') }}<span class="text-gray-400">{{ getSortIcon('status') }}</span></th>
                <th class="px-6 py-4 text-center font-semibold text-gray-900 dark:text-white">{{ t('otHistory.actions')
                }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
              <tr v-for="request in paginatedRequests" :key="request.id" class="hover:bg-gray-50 dark:hover:bg-white/5"
                :class="{ 'bg-brand-50/50 dark:bg-brand-500/5': isSelected(request.id) }">
                <!-- Checkbox column (PTB admin only) -->
                <td v-if="isAdmin" class="w-12 px-4 py-4">
                  <input type="checkbox" :checked="isSelected(request.id)" @change="toggleSelect(request.id)"
                    class="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800" />
                </td>
                <td class="px-6 py-4 text-gray-900 dark:text-white">
                  <span class="font-medium">{{ formatDate(request.request_date) }}</span>
                </td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">{{ request.employee_name }}</td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">{{ request.project_name }}</td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">
                  {{ formatTime(request.time_start) }} - {{ formatTime(request.time_end) }}
                </td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">
                  {{ formatHours(request.total_hours) }}h
                </td>
                <td class="px-6 py-4">
                  <span v-if="request.is_holiday === true"
                    class="rounded-full bg-purple-100 px-3 py-1 text-xs font-medium text-purple-800 dark:bg-purple-500/20 dark:text-purple-300">
                    {{ t('otHistory.holiday') }}
                  </span>
                  <span v-else-if="request.is_weekend === true"
                    class="rounded-full bg-orange-100 px-3 py-1 text-xs font-medium text-orange-800 dark:bg-orange-500/20 dark:text-orange-300">
                    {{ t('otHistory.weekend') }}
                  </span>
                  <span v-else
                    class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800 dark:bg-blue-500/20 dark:text-blue-300">
                    {{ t('otHistory.weekday') }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <button v-if="isAdmin" @click="handleStatusChange(request)" :disabled="isUpdatingStatus" :class="{
                    'bg-yellow-100 text-yellow-800 dark:bg-yellow-500/20 dark:text-yellow-300': request.status === 'pending',
                    'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300': request.status === 'approved',
                    'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300': request.status === 'rejected'
                  }"
                    class="rounded-full px-3 py-1 text-xs font-medium cursor-pointer hover:opacity-80 transition disabled:opacity-50 disabled:cursor-not-allowed">
                    {{ request.status ? request.status.charAt(0).toUpperCase() + request.status.slice(1)
                      : 'Pending' }}
                  </button>
                  <span v-else :class="{
                    'bg-yellow-100 text-yellow-800 dark:bg-yellow-500/20 dark:text-yellow-300': request.status === 'pending',
                    'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300': request.status === 'approved',
                    'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300': request.status === 'rejected'
                  }" class="rounded-full px-3 py-1 text-xs font-medium">
                    {{ request.status ? request.status.charAt(0).toUpperCase() + request.status.slice(1)
                      : 'Pending' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-center">
                  <div class="flex justify-center gap-2">
                    <button @click="handleView(request)"
                      class="h-9 rounded-lg border border-brand-300 px-3 text-sm font-medium text-brand-600 transition hover:bg-brand-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-brand-500/30 dark:text-brand-400 dark:hover:bg-brand-500/10">
                      {{ t('otHistory.view') }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          class="flex-none flex flex-col gap-3 border-t border-gray-200 px-6 py-4 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-3">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ t('otHistory.showingRange', { start: pageRangeStart, end: pageRangeEnd, total: totalCount }) }}
            </p>
            <select v-model.number="pageSize"
              class="h-9 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
              <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} {{ t('common.perPage') }}
              </option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1"
              class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.prev') }}
            </button>
            <div class="flex items-center gap-1.5 text-sm text-gray-700 dark:text-gray-300">
              <input type="number" :value="currentPage" @change="handlePageInputChange"
                @keydown.enter="($event.target as HTMLInputElement).blur()" :min="1" :max="totalPages"
                class="h-9 w-14 rounded-lg border border-gray-300 bg-white px-2 text-center text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" />
              <span>{{ t('otHistory.pageOf', { total: totalPages }) }}</span>
            </div>
            <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages"
              class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.next') }}
            </button>
          </div>
        </div>
      </div>

      <!-- View Modal -->
      <div v-if="showViewModal && viewingRequest" class="fixed inset-0 z-[100000] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showViewModal = false"></div>
        <div role="dialog" aria-modal="true" aria-labelledby="ot-history-modal-title"
          class="relative z-10 w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
          <!-- Sticky Header -->
          <div
            class="sticky top-0 z-10 flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-t-2xl">
            <h2 id="ot-history-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ t('otHistory.requestDetailsTitle') }}
            </h2>
            <button @click="showViewModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Scrollable Body -->
          <div class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.employee')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ viewingRequest.employee_name }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.employeeId')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ viewingRequest.employee_emp_id || '—' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.departmentCode') }}</label>
                <p class="text-gray-900 dark:text-white">{{ viewingRequest.department_code || '—' }}</p>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.date')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ formatDate(viewingRequest.request_date) }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.type')
                }}</label>
                <span v-if="viewingRequest.is_holiday"
                  class="rounded-full bg-purple-100 px-3 py-1 text-xs font-medium text-purple-800 dark:bg-purple-500/20 dark:text-purple-300">
                  {{ t('otHistory.holiday') }}
                </span>
                <span v-else-if="viewingRequest.is_weekend"
                  class="rounded-full bg-orange-100 px-3 py-1 text-xs font-medium text-orange-800 dark:bg-orange-500/20 dark:text-orange-300">
                  {{ t('otHistory.weekend') }}
                </span>
                <span v-else
                  class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800 dark:bg-blue-500/20 dark:text-blue-300">
                  {{ t('otHistory.weekday') }}
                </span>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.status')
                }}</label>
                <span :class="{
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-500/20 dark:text-yellow-300': viewingRequest.status === 'pending',
                  'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300': viewingRequest.status === 'approved',
                  'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300': viewingRequest.status === 'rejected'
                }" class="inline-block rounded-full px-3 py-1 text-xs font-medium">
                  {{ viewingRequest.status ? viewingRequest.status.charAt(0).toUpperCase() +
                    viewingRequest.status.slice(1) : 'Pending' }}
                </span>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.startTime')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ formatTime(viewingRequest.time_start) }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.endTime')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ formatTime(viewingRequest.time_end) }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.overtimeHours')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ formatHours(viewingRequest.total_hours) }}h
                </p>
              </div>
            </div>

            <div v-if="viewingRequest.has_break" class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.breakStart')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ formatTime(viewingRequest.break_start) || '—' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.breakEnd')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ formatTime(viewingRequest.break_end) || '—' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                  t('otHistory.breakHours')
                }}</label>
                <p class="text-gray-900 dark:text-white">{{ formatHours(viewingRequest.break_hours) }}h
                </p>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.project')
              }}</label>
              <p class="text-gray-900 dark:text-white">{{ viewingRequest.project_name }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.reason')
              }}</label>
              <p class="text-gray-900 dark:text-white whitespace-pre-wrap">{{ viewingRequest.reason }}</p>
            </div>

            <div v-if="viewingRequest.detail">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('otHistory.details')
              }}</label>
              <p class="text-gray-900 dark:text-white whitespace-pre-wrap">{{ viewingRequest.detail }}</p>
            </div>
          </div>

          <!-- Sticky Footer -->
          <div
            class="sticky bottom-0 z-10 flex gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-b-2xl">
            <button @click="showViewModal = false"
              class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.close') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
import { useFlatpickrScroll } from '@/composables/useFlatpickrScroll'
import { usePagePermission } from '@/composables/usePagePermission'
import { DEBOUNCE_SEARCH_MS } from '@/constants/ui'
import type { OvertimeRequest } from '@/services/api/overtime'
import { useAuthStore } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import { useEmployeeStore } from '@/stores/employee'
import { useOvertimeStore } from '@/stores/overtime'
import { useProjectStore } from '@/stores/project'
import { useUIStore } from '@/stores/ui'
import { getSortIcon as _getSortIcon } from '@/utils/getSortIcon'

// Pinia Stores
const overtimeStore = useOvertimeStore()
const authStore = useAuthStore()
const employeeStore = useEmployeeStore()
const projectStore = useProjectStore()
const departmentStore = useDepartmentStore()
const uiStore = useUIStore()
const { t } = useI18n()

const { canUpdate: canUpdateOT } = usePagePermission('ot_history')
const isAdmin = computed(() => authStore.isPtbAdmin && canUpdateOT.value)
const userWorkerId = computed(() => authStore.user?.worker_id || null)

// Data from store — this is the CURRENT PAGE of server-side paginated results
const isLoading = computed(() => overtimeStore.loading)

// Helper function to format hours (handles both string and number)
const formatHours = (value: string | number | null | undefined): string => {
	if (value === null || value === undefined) return '0.00'
	const num = typeof value === 'string' ? parseFloat(value) : value
	return Number.isNaN(num) ? '0.00' : num.toFixed(2)
}

// Helper function to format time as HH:MM (strip seconds)
const formatTime = (value: string | null | undefined): string => {
	if (!value) return '—'
	// Handle HH:MM:SS → HH:MM
	const parts = value.split(':')
	if (parts.length >= 2) return `${parts[0]}:${parts[1]}`
	return value
}

const searchQuery = ref('')
const statusFilter = ref('')
const employeeFilter = ref('')
const projectFilter = ref('')
const departmentFilter = ref('')

// Date selection state - load from UI store (persisted in localStorage)
const dateSelectionType = ref<'year-month' | 'custom'>(uiStore.dateFilter.selectionType)
const selectedYear = ref(uiStore.dateFilter.selectedYear)
const selectedMonth = ref<string | number>(uiStore.dateFilter.selectedMonth)
const customDateRange = ref<string>(uiStore.dateFilter.customDateRange || '')

const { flatpickrInstances, attachMonthScroll, destroyFlatpickrs } = useFlatpickrScroll()

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

// Month options
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

// Helper function to format date as YYYY-MM-DD
const formatYMD = (d: Date) => {
	const y = d.getFullYear()
	const m = String(d.getMonth() + 1).padStart(2, '0')
	const day = String(d.getDate()).padStart(2, '0')
	return `${y}-${m}-${day}`
}

// Get current period range (26th to 25th calculation)
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
	return { start, end }
}

const resetToCurrentMonth = () => {
	const period = getCurrentPeriodRange()
	const periodMonth = period.end.getMonth() + 1
	selectedYear.value = period.end.getFullYear()
	selectedMonth.value = periodMonth
}

const pageSize = ref(25)
const currentPage = ref(1)
const showViewModal = ref(false)
const viewingRequest = ref<OvertimeRequest | null>(null)
const pageSizeOptions = [10, 25, 50, 100, 250, 500, 1000]

const customDatePickerOptions = {
	mode: 'range' as const,
	dateFormat: 'Y-m-d',
	altInput: true,
	altFormat: 'M j, Y',
	onReady: (
		_selected: unknown,
		_dateStr: string,
		instance: Parameters<typeof attachMonthScroll>[0],
	) => {
		flatpickrInstances.value.push(instance)
		attachMonthScroll(instance)
	},
}

// Helper to calculate date range based on selection type
// Month calculation: 26th of previous month to 25th of selected month
const calculateDateRange = (): { start: string; end: string } | null => {
	if (dateSelectionType.value === 'custom' && customDateRange.value) {
		const dates = customDateRange.value.split(' to ')
		if (dates.length === 2 && dates[0] && dates[1]) {
			return { start: dates[0], end: dates[1] }
		} else if (dates.length === 1 && dates[0]) {
			return { start: dates[0], end: dates[0] }
		}
	} else if (dateSelectionType.value === 'year-month') {
		if (selectedMonth.value === 'all') {
			const startDate = new Date(selectedYear.value - 1, 11, 26)
			const endDate = new Date(selectedYear.value, 11, 25)
			return { start: formatYMD(startDate), end: formatYMD(endDate) }
		} else {
			const year = selectedYear.value
			const month = Number(selectedMonth.value)

			const startDate = new Date(year, month - 1, 26)
			if (month === 1) {
				startDate.setFullYear(year - 1, 11, 26)
			} else {
				startDate.setMonth(month - 2, 26)
			}

			const endDate = new Date(year, month - 1, 25)

			return { start: formatYMD(startDate), end: formatYMD(endDate) }
		}
	}
	return null
}

type SortField =
	| 'request_date'
	| 'employee_name'
	| 'project_name'
	| 'time_start'
	| 'total_hours'
	| 'status'
	| 'type'
const sortBy = ref<SortField | null>(null)
const sortOrder = ref<'asc' | 'desc'>('asc')

// ── Dropdown options from stores (independent of current page data) ─────
const employeeOptions = computed(() => {
	if (isAdmin.value) {
		return employeeStore.employees
			.filter((emp) => emp.is_enabled !== false)
			.map((emp) => emp.name)
			.sort()
	}
	// Non-admin: only show current user's name
	const currentUserEmployee = employeeStore.employees.find(
		(emp) => emp.emp_id.toLowerCase() === userWorkerId.value?.toLowerCase(),
	)
	return currentUserEmployee ? [currentUserEmployee.name] : []
})

const projectOptions = computed(() =>
	projectStore.projects
		.filter((p) => p.is_enabled)
		.map((p) => p.name)
		.sort(),
)

const departmentOptions = computed(() =>
	departmentStore.departments
		.filter((d) => d.is_enabled)
		.map((d) => d.code)
		.sort(),
)

// ── Server-side data: table rows are already the correct page ───────────
const paginatedRequests = computed(() => overtimeStore.requests)
const totalCount = computed(() => overtimeStore.paginationMeta.count)
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

const pageRangeStart = computed(() =>
	totalCount.value === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1,
)
const pageRangeEnd = computed(() => Math.min(totalCount.value, currentPage.value * pageSize.value))

// ── Map UI sort fields to backend ordering param ────────────────────────
const serverOrdering = computed<string | undefined>(() => {
	if (!sortBy.value) return '-request_date'
	// 'type' is computed on the frontend, no backend equivalent — fallback
	const fieldMap: Record<SortField, string | null> = {
		request_date: 'request_date',
		employee_name: 'employee_name',
		project_name: 'project_name',
		total_hours: 'total_hours',
		status: 'status',
		time_start: 'request_date', // no direct backend field; approximate with request_date
		type: null,
	}
	const field = fieldMap[sortBy.value]
	if (!field) return '-request_date'
	return sortOrder.value === 'desc' ? `-${field}` : field
})

// ── Core data-fetching function (all filters → server) ─────────────────
let fetchTimer: ReturnType<typeof setTimeout> | null = null
let overtimeFetchAbortController: AbortController | null = null

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

const fetchServerData = async (resetPage = false) => {
	if (overtimeFetchAbortController) {
		overtimeFetchAbortController.abort()
	}
	const controller = new AbortController()
	overtimeFetchAbortController = controller

	if (resetPage) currentPage.value = 1
	const dateRange = calculateDateRange()

	// Map employee name → ID
	let employeeId: number | undefined
	if (employeeFilter.value) {
		const emp = employeeStore.employees.find((e) => e.name === employeeFilter.value)
		if (emp) employeeId = emp.id
	}

	// Map project name → ID
	let projectId: number | undefined
	if (projectFilter.value) {
		const proj = projectStore.projects.find((p) => p.name === projectFilter.value)
		if (proj) projectId = proj.id
	}

	const params: Record<string, unknown> = {
		page: currentPage.value,
		page_size: pageSize.value,
		ordering: serverOrdering.value,
	}

	if (dateRange) {
		params.start_date = dateRange.start
		params.end_date = dateRange.end
	}
	if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
	if (statusFilter.value) params.status = statusFilter.value
	if (employeeId) params.employee = employeeId
	if (projectId) params.project = projectId
	if (departmentFilter.value) params.department_code = departmentFilter.value

	try {
		await overtimeStore.fetchRequests(
			params as Parameters<typeof overtimeStore.fetchRequests>[0],
			true,
			{ signal: controller.signal },
		)
	} catch (err) {
		if (isAbortError(err)) {
			return
		}
		throw err
	} finally {
		if (overtimeFetchAbortController === controller) {
			overtimeFetchAbortController = null
		}
	}
}

const debouncedFetch = (resetPage = true) => {
	if (fetchTimer) clearTimeout(fetchTimer)
	fetchTimer = setTimeout(() => {
		void fetchServerData(resetPage)
	}, DEBOUNCE_SEARCH_MS)
}

const toggleSort = (field: SortField) => {
	if (sortBy.value === field) {
		if (sortOrder.value === 'asc') {
			sortOrder.value = 'desc'
		} else {
			sortBy.value = null
		}
	} else {
		sortBy.value = field
		sortOrder.value = 'asc'
	}
	// Sort change → refetch from page 1
	fetchServerData(true)
}

const getSortIcon = (field: SortField) => _getSortIcon(field, sortBy, sortOrder)

const handleReset = () => {
	searchQuery.value = ''
	statusFilter.value = ''
	employeeFilter.value = ''
	projectFilter.value = ''
	departmentFilter.value = ''
	dateSelectionType.value = 'year-month'
	const now = new Date()
	selectedYear.value = now.getFullYear()
	selectedMonth.value = now.getMonth() + 1
	customDateRange.value = ''
	sortBy.value = null
	sortOrder.value = 'asc'
	// No direct fetchServerData() call — the unified watcher below
	// will fire once after all refs settle in the same tick.
}

const goToPage = (page: number) => {
	if (page < 1 || page > totalPages.value) return
	currentPage.value = page
	fetchServerData()
}

const handlePageInputChange = (event: Event) => {
	const input = event.target as HTMLInputElement
	const value = parseInt(input.value, 10)
	if (!Number.isNaN(value) && value >= 1 && value <= totalPages.value) {
		currentPage.value = value
		fetchServerData()
	} else {
		input.value = String(currentPage.value)
	}
}

const handleView = (request: OvertimeRequest) => {
	viewingRequest.value = request
	showViewModal.value = true
}

const isUpdatingStatus = ref(false)
const isBulkUpdating = ref(false)
type RequestStatus = 'pending' | 'approved' | 'rejected' | 'cancelled'

// Bulk selection state
const selectedRequests = ref<number[]>([])

const isSelected = (id: number | undefined) => {
	return id !== undefined && selectedRequests.value.includes(id)
}

const toggleSelect = (id: number | undefined) => {
	if (id === undefined) return
	const index = selectedRequests.value.indexOf(id)
	if (index === -1) {
		selectedRequests.value.push(id)
	} else {
		selectedRequests.value.splice(index, 1)
	}
}

const isAllCurrentPageSelected = computed(() => {
	const pageIds = paginatedRequests.value
		.map((r) => r.id)
		.filter((id): id is number => id !== undefined)
	return pageIds.length > 0 && pageIds.every((id) => selectedRequests.value.includes(id))
})

const isPartiallySelected = computed(() => {
	const pageIds = paginatedRequests.value
		.map((r) => r.id)
		.filter((id): id is number => id !== undefined)
	const selectedCount = pageIds.filter((id) => selectedRequests.value.includes(id)).length
	return selectedCount > 0 && selectedCount < pageIds.length
})

const toggleSelectAll = () => {
	const pageIds = paginatedRequests.value
		.map((r) => r.id)
		.filter((id): id is number => id !== undefined)
	if (isAllCurrentPageSelected.value) {
		selectedRequests.value = selectedRequests.value.filter((id) => !pageIds.includes(id))
	} else {
		pageIds.forEach((id) => {
			if (!selectedRequests.value.includes(id)) {
				selectedRequests.value.push(id)
			}
		})
	}
}

const clearSelection = () => {
	selectedRequests.value = []
}

const handleBulkApprove = async () => {
	if (selectedRequests.value.length === 0 || isBulkUpdating.value) return
	isBulkUpdating.value = true
	try {
		const idsToApprove = selectedRequests.value.filter((id) => {
			const request = paginatedRequests.value.find((r) => r.id === id)
			return request && request.status !== 'approved'
		})
		if (idsToApprove.length > 0) {
			await overtimeStore.bulkUpdateStatus(idsToApprove, 'approved')
			// Refetch current page to reflect updated status and counts
			await fetchServerData()
		}
		clearSelection()
	} catch (error) {
		console.error('Bulk approve error:', error)
	} finally {
		isBulkUpdating.value = false
	}
}

const handleBulkReject = async () => {
	if (selectedRequests.value.length === 0 || isBulkUpdating.value) return
	isBulkUpdating.value = true
	try {
		const idsToReject = selectedRequests.value.filter((id) => {
			const request = paginatedRequests.value.find((r) => r.id === id)
			return request && request.status !== 'rejected'
		})
		if (idsToReject.length > 0) {
			await overtimeStore.bulkUpdateStatus(idsToReject, 'rejected')
			await fetchServerData()
		}
		clearSelection()
	} catch (error) {
		console.error('Bulk reject error:', error)
	} finally {
		isBulkUpdating.value = false
	}
}

const handleStatusChange = async (request: OvertimeRequest) => {
	if (isUpdatingStatus.value || !isAdmin.value || !request.id) return

	const statusCycle: Record<RequestStatus, 'pending' | 'approved' | 'rejected'> = {
		pending: 'approved',
		approved: 'rejected',
		rejected: 'pending',
		cancelled: 'pending',
	}

	const currentStatus = (request.status ?? 'pending') as RequestStatus
	const newStatus = statusCycle[currentStatus]

	isUpdatingStatus.value = true
	const previousStatus = request.status
	request.status = newStatus

	try {
		await overtimeStore.bulkUpdateStatus([request.id], newStatus)
	} catch (error) {
		console.error('Failed to update status:', error)
		request.status = previousStatus
	} finally {
		isUpdatingStatus.value = false
	}
}

const formatDate = (dateStr: string) => {
	const date = new Date(dateStr)
	return date.toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
	})
}

const handleEscKey = (event: KeyboardEvent) => {
	if (event.key === 'Escape' && showViewModal.value) {
		showViewModal.value = false
	}
}

// ── Lifecycle ───────────────────────────────────────────────────────────
onMounted(async () => {
	// Load reference data (employees, projects, departments) in parallel with first page
	await Promise.all([
		employeeStore.fetchEmployees(),
		projectStore.fetchProjects(),
		departmentStore.fetchDepartments(),
		fetchServerData(),
	])

	// Auto-select employee for non-admin users
	if (!isAdmin.value && userWorkerId.value) {
		const currentUserEmployee = employeeStore.employees.find(
			(emp) => emp.emp_id.toLowerCase() === userWorkerId.value?.toLowerCase(),
		)
		if (currentUserEmployee) {
			employeeFilter.value = currentUserEmployee.name
			// Refetch with employee filter applied
			await fetchServerData(true)
		}
	}

	window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', handleEscKey)
	if (fetchTimer) clearTimeout(fetchTimer)
	if (overtimeFetchAbortController) {
		overtimeFetchAbortController.abort()
		overtimeFetchAbortController = null
	}
	destroyFlatpickrs()
})

// ── Watchers — any filter/date/pageSize change triggers server refetch ──
// Search uses debounce so user can type without firing requests per keystroke
watch(searchQuery, () => debouncedFetch(true))

// Unified watcher: Vue batches synchronous changes into a single invocation,
// so handleReset() changing multiple refs only fires one refetch.
watch(
	[
		statusFilter,
		employeeFilter,
		projectFilter,
		departmentFilter,
		pageSize,
		dateSelectionType,
		selectedYear,
		selectedMonth,
		customDateRange,
	],
	() => {
		fetchServerData(true)
	},
)
</script>
