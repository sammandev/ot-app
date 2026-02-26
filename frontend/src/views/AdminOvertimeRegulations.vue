<!-- @vue/component -->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-semibold text-brand-500">{{ t('pages.adminRegulations.category') }}</p>
          <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.adminRegulations.title') }}</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.adminRegulations.subtitle') }}</p>
        </div>
        <button v-if="canCreate" @click="openCreateModal"
          class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20">
          {{ t('admin.reg.addRegulation') }}
        </button>
      </div>

      <!-- Overtime Limits Configuration -->
      <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div v-if="limitSaveSuccess"
          class="mb-4 flex items-start justify-between gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800 dark:border-emerald-900/40 dark:bg-emerald-900/30 dark:text-emerald-100">
          <span>{{ t('admin.reg.limitsSaved') }}</span>
          <button @click="limitSaveSuccess = false" type="button"
            class="text-emerald-700 transition hover:text-emerald-900 dark:text-emerald-200 dark:hover:text-emerald-100">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div v-if="limitSaveError"
          class="mb-4 flex items-start justify-between gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-800 dark:border-rose-900/40 dark:bg-rose-900/30 dark:text-rose-100">
          <span>{{ limitSaveError }}</span>
          <button @click="limitSaveError = ''" type="button"
            class="text-rose-700 transition hover:text-rose-900 dark:text-rose-200 dark:hover:text-rose-100">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="mb-4 flex items-center gap-3">
          <div class="rounded-lg bg-amber-100 p-2 dark:bg-amber-900/30">
            <svg class="h-6 w-6 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor"
              viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ t('admin.reg.overtimeLimitsTitle') }}
            </h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('admin.reg.overtimeLimitsDesc') }}</p>
          </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
          <div class="space-y-1.5">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.reg.maxWeeklyHours')
              }}</label>
            <input v-model.number="limitForm.max_weekly_hours" type="number" step="0.5" min="0" max="168"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
              :disabled="!canUpdate" />
            <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('admin.reg.weeklyHoursDesc') }}</p>
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.reg.maxMonthlyHours')
              }}</label>
            <input v-model.number="limitForm.max_monthly_hours" type="number" step="0.5" min="0" max="744"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
              :disabled="!canUpdate" />
            <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('admin.reg.monthlyHoursDesc') }}</p>
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.reg.tpeWeeklyHours')
              }}</label>
            <input v-model.number="limitForm.recommended_weekly_hours" type="number" step="0.5" min="0" max="168"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
              :disabled="!canUpdate" />
            <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('admin.reg.tpeWeeklyDesc') }}</p>
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.reg.tpeMonthlyHours')
              }}</label>
            <input v-model.number="limitForm.recommended_monthly_hours" type="number" step="0.5" min="0" max="744"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
              :disabled="!canUpdate" />
            <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('admin.reg.tpeMonthlyDesc') }}</p>
          </div>
          <div v-if="canUpdate" class="flex items-end">
            <button @click="saveLimits" :disabled="isSavingLimits"
              class="h-11 w-full rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 disabled:opacity-50">
              {{ isSavingLimits ? t('common.saving') : t('admin.reg.saveLimits') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Policy Document Management -->
      <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div v-if="pdfSuccessMessage"
          class="mb-4 flex items-start justify-between gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800 dark:border-emerald-900/40 dark:bg-emerald-900/30 dark:text-emerald-100">
          <span>{{ pdfSuccessMessage }}</span>
          <button @click="pdfSuccessMessage = ''" type="button"
            class="text-emerald-700 transition hover:text-emerald-900 dark:text-emerald-200 dark:hover:text-emerald-100">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="mb-4 flex items-center gap-3">
          <div class="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/30">
            <svg class="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ t('admin.reg.policyDocument') }}</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('admin.reg.policyDescription') }}</p>
          </div>
        </div>

        <div v-if="pdfDocument"
          class="mb-4 rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
            <div class="flex items-start gap-3">
              <div class="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/30">
                <svg class="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-900 dark:text-white break-all max-w-full">{{
                  pdfDocument.title }}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('admin.reg.uploaded') }} {{
                  formatDate(pdfDocument.created_at) }}</p>
                <button @click="handlePreviewPdf(pdfDocument.file)"
                  class="mt-1 inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  {{ t('admin.reg.previewDocument') }}
                </button>
              </div>
            </div>
            <button v-if="canDelete" @click="showDeletePdfModal = true"
              class="rounded-lg border border-error-300 px-3 py-2 text-sm font-medium text-error-600 transition hover:bg-error-50 dark:border-error-500/30 dark:text-error-400 dark:hover:bg-error-500/10 w-full sm:w-auto sm:self-start">
              {{ t('common.delete') }}
            </button>
          </div>
        </div>

        <div v-else
          class="mb-4 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-6 text-center dark:border-gray-700 dark:bg-gray-800/50">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">{{ t('admin.reg.noDocumentUploaded') }}</p>
        </div>

        <div v-if="canCreate">
          <input ref="fileInput" type="file" accept=".pdf" @change="handleFileChange" class="hidden" />
          <div
            class="rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-6 text-center transition hover:border-brand-500 dark:border-gray-700 dark:bg-gray-800/50 dark:hover:border-brand-400 cursor-pointer"
            :class="{ 'border-brand-500 bg-brand-50/50 dark:bg-brand-900/10': isDragOver }" @click="fileInput?.click()"
            @dragover.prevent="onDragOver" @dragleave.prevent="onDragLeave" @drop.prevent="onDrop">
            <div
              class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p class="text-sm font-semibold text-gray-800 dark:text-white">{{ t('admin.reg.dropPdfOrClick') }}
            </p>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ t('admin.reg.maxSize10mb') }}</p>
            <p class="mt-2 text-xs text-brand-600 dark:text-brand-400">{{ isUploading ? t('admin.reg.uploadingDoc') :
              t('admin.reg.uploadDocument') }}</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <TableSkeleton v-if="isLoading" :rows="8" :columns="4" />

      <!-- Empty State -->
      <div v-else-if="regulations.length === 0"
        class="rounded-2xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-white/[0.03]">
        <p class="text-gray-500 dark:text-gray-400">{{ t('admin.reg.noRegulations') }}</p>
      </div>

      <!-- Regulations Table -->
      <div v-else
        class="overflow-x-auto rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
        <div
          class="flex flex-col gap-3 border-b border-gray-200 px-6 py-4 sm:flex-row sm:items-center sm:justify-between dark:border-gray-800">
          <div>
            <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t('admin.reg.regulations') }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('admin.reg.searchAppliesInstantly') }}</p>
          </div>
          <div class="w-full sm:w-128">
            <input v-model="searchQuery" type="text" :placeholder="t('admin.reg.searchPlaceholder')"
              class="dark:bg-dark-900 h-10 w-full rounded-lg border border-gray-300 bg-transparent px-3 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300" />
          </div>
        </div>
        <table class="w-full text-sm">
          <thead class="border-b border-gray-200 dark:border-gray-800">
            <tr>
              <th @click="toggleSort('order')"
                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                {{ t('admin.reg.order') }}<span class="text-gray-400">{{ getSortIcon('order') }}</span></th>
              <th @click="toggleSort('title')"
                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                {{ t('common.name') }}<span class="text-gray-400">{{ getSortIcon('title') }}</span></th>
              <th @click="toggleSort('description')"
                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                {{ t('common.description') }}<span class="text-gray-400">{{ getSortIcon('description') }}</span></th>
              <th @click="toggleSort('is_active')"
                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                {{ t('common.status') }}<span class="text-gray-400">{{ getSortIcon('is_active') }}</span></th>
              <th class="px-6 py-4 text-center font-semibold text-gray-900 dark:text-white">{{ t('common.actions') }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
            <tr v-for="reg in paginatedRegulations" :key="reg.id" class="hover:bg-gray-50 dark:hover:bg-white/5">
              <td class="px-6 py-4 text-gray-900 dark:text-white">
                <span class="font-medium">{{ reg.order }}</span>
              </td>
              <td class="px-6 py-4 text-gray-900 dark:text-white">
                <span class="font-medium">{{ reg.title }}</span>
              </td>
              <td class="px-6 py-4 text-gray-700 dark:text-gray-300">
                <p class="line-clamp-2">{{ reg.description }}</p>
              </td>
              <td class="px-6 py-4">
                <button v-if="canUpdate" @click="handleToggleEnabled(reg.id, reg.is_active)"
                  :class="reg.is_active ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                  class="rounded-full px-3 py-1 text-xs font-medium transition hover:opacity-80">
                  {{ reg.is_active ? t('admin.active') : t('admin.inactive') }}
                </button>
                <span v-else
                  :class="reg.is_active ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                  class="rounded-full px-3 py-1 text-xs font-medium">
                  {{ reg.is_active ? t('admin.active') : t('admin.inactive') }}
                </span>
              </td>
              <td class="px-6 py-4 text-center">
                <div class="flex justify-center gap-2">
                  <button v-if="canUpdate" @click="handleEdit(reg)"
                    class="h-9 rounded-lg border border-brand-300 px-3 text-sm font-medium text-brand-600 transition hover:bg-brand-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-brand-500/30 dark:text-brand-400 dark:hover:bg-brand-500/10">
                    {{ t('common.edit') }}
                  </button>
                  <button v-if="canDelete" @click="handleDelete(reg.id)"
                    class="h-9 rounded-lg border border-error-300 px-3 text-sm font-medium text-error-600 transition hover:bg-error-50 focus:outline-hidden focus:ring-3 focus:ring-error-500/10 dark:border-error-500/30 dark:text-error-400 dark:hover:bg-error-500/10">
                    {{ t('common.delete') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div
          class="flex flex-col gap-3 border-t border-gray-200 px-6 py-4 text-sm text-gray-700 dark:border-gray-800 dark:text-gray-300 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-3">
            <p>{{ t('common.showing') }} {{ pageRangeStart }}-{{ pageRangeEnd }} {{ t('common.of') }} {{
              sortedRegulations.length }}</p>
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
            <span>{{ t('common.page') }} {{ currentPage }} {{ t('common.of') }} {{ totalPages }}</span>
            <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages"
              class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.next') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Create/Edit Modal -->
      <div v-if="showCreateModal || showEditModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="showCreateModal = false; showEditModal = false"></div>
        <div
          class="rounded-2xl border border-gray-200 bg-white w-full max-w-2xl max-h-[90vh] flex flex-col dark:border-gray-800 dark:bg-gray-900 relative z-10">
          <!-- Sticky Header -->
          <div
            class="sticky top-0 z-10 px-6 pt-5 pb-4 bg-white dark:bg-gray-900 rounded-t-2xl border-b border-gray-200 dark:border-gray-800">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ editingReg ? t('admin.reg.editRegulation') : t('admin.reg.addRegulationTitle') }}
            </h2>
          </div>
          <!-- Scrollable Body -->
          <div class="flex-1 overflow-y-auto px-6 py-4">
            <form @submit.prevent="handleSave" id="regulationForm" class="space-y-4">
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.reg.regulationTitle')
                  }}</label>
                <input v-model="formData.title" type="text"
                  class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                  :class="errors.title ? 'border-error-300 dark:border-error-700' : ''"
                  :placeholder="t('admin.reg.enterTitle')" required />
                <p v-if="errors.title" class="text-xs text-error-500">{{ errors.title }}</p>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('common.description')
                  }}</label>
                <textarea v-model="formData.description" rows="4"
                  class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300 resize-none"
                  :class="errors.description ? 'border-error-300 dark:border-error-700' : ''"
                  :placeholder="t('admin.reg.enterDescription')" required></textarea>
                <p v-if="errors.description" class="text-xs text-error-500">{{ errors.description }}</p>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.reg.displayOrder')
                  }}</label>
                <input v-model.number="formData.order" type="number" min="1"
                  class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                  :class="errors.order ? 'border-error-300 dark:border-error-700' : ''"
                  :placeholder="t('admin.reg.egOrder')" required />
                <p v-if="errors.order" class="text-xs text-error-500">{{ errors.order }}</p>
              </div>
              <div class="flex items-center gap-2">
                <input v-model="formData.is_active" type="checkbox" id="enabled" class="sr-only" />
                <div @click="formData.is_active = !formData.is_active"
                  :class="formData.is_active ? 'border-brand-500 bg-brand-500' : 'bg-transparent border-gray-300 dark:border-gray-700'"
                  class="mr-2 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] hover:border-brand-500 dark:hover:border-brand-500 cursor-pointer">
                  <span :class="formData.is_active ? '' : 'opacity-0'">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M11.6666 3.5L5.24992 9.91667L2.33325 7" stroke="white" stroke-width="1.94437"
                        stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                  </span>
                </div>
                <label for="enabled" class="text-sm font-medium text-gray-700 dark:text-gray-200 cursor-pointer"
                  @click="formData.is_active = !formData.is_active">
                  {{ t('admin.active') }}
                </label>
              </div>
            </form>
          </div>
          <!-- Sticky Footer -->
          <div
            class="sticky bottom-0 z-10 flex gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 rounded-b-2xl">
            <button type="button" @click="showCreateModal = false; showEditModal = false"
              class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.cancel') }}
            </button>
            <button type="submit" form="regulationForm" :disabled="isSaving"
              class="h-11 flex-1 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 disabled:opacity-60 disabled:cursor-not-allowed">
              {{ isSaving ? t('common.saving') : t('common.save') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="cancelDelete"></div>
        <div
          class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            {{ t('admin.confirmDelete') }}
          </h2>
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            {{ t('admin.reg.deleteMsg') }}
          </p>
          <div class="flex gap-3">
            <button @click="cancelDelete" type="button"
              class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.cancel') }}
            </button>
            <button @click="confirmDelete"
              class="h-11 flex-1 rounded-lg bg-error-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 focus:outline-hidden focus:ring-3 focus:ring-error-500/20">
              {{ t('common.delete') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Delete PDF Confirmation Modal -->
      <div v-if="showDeletePdfModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="showDeletePdfModal = false"></div>
        <div
          class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            {{ t('admin.reg.deletePolicyDocument') }}
          </h2>
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            {{ t('admin.reg.deletePolicyMsg') }}
          </p>
          <div class="flex gap-3">
            <button @click="showDeletePdfModal = false" type="button"
              class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.cancel') }}
            </button>
            <button @click="confirmDeletePdf"
              class="h-11 flex-1 rounded-lg bg-error-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 focus:outline-hidden focus:ring-3 focus:ring-error-500/20">
              {{ t('common.delete') }}
            </button>
          </div>
        </div>
      </div>

      <!-- PDF Preview Modal - Teleported to body to escape overflow-x-clip -->
      <Teleport to="body">
        <div v-if="showPdfPreviewModal"
          class="fixed inset-0 z-[100000] flex items-center justify-center overflow-hidden"
          :class="isPdfFullscreen ? '' : 'p-4'" @click.self="closePdfPreview">
          <!-- Backdrop covers full viewport -->
          <div class="fixed inset-0 bg-black/60" aria-hidden="true"></div>

          <!-- Modal Container -->
          <div :class="[
            'relative z-10 flex flex-col bg-white dark:bg-gray-900 transition-[width,height,border-radius] duration-300',
            isPdfFullscreen
              ? 'fixed inset-0 h-full w-full'
              : 'h-[95vh] w-[95vw] max-w-[1400px] rounded-2xl border border-gray-200 shadow-2xl dark:border-gray-800'
          ]">
            <!-- Modal Header -->
            <div
              class="flex flex-shrink-0 items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-800">
              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/30">
                  <svg class="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ pdfDocument?.title ||
                    t('admin.reg.policyDocumentTitle') }}</h2>
                  <p v-if="pdfDocument?.created_at" class="text-xs text-gray-500 dark:text-gray-400">{{
                    t('admin.reg.updatedLabel') }} {{ formatDate(pdfDocument.created_at) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button @click="togglePdfFullscreen"
                  class="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                  :title="isPdfFullscreen ? t('admin.reg.exitFullscreen') : t('admin.reg.enterFullscreen')">
                  <svg v-if="!isPdfFullscreen" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                  <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                  </svg>
                </button>
                <button @click="closePdfPreview"
                  class="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                  :title="t('admin.reg.closeEsc')">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Modal Body - PDF Viewer with overflow control -->
            <div class="flex-1 overflow-hidden bg-gray-100 dark:bg-gray-950 min-h-0">
              <embed :src="pdfPreviewUrl" type="application/pdf" class="h-full w-full min-h-[600px]" />
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
import { usePagePermission } from '@/composables/usePagePermission'
import {
	type OvertimeLimitConfig,
	type OvertimeRegulationContent,
	type OvertimeRegulationDocument,
	overtimeLimitAPI,
	regulationAPI,
	regulationDocumentAPI,
} from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatLocalDateTime } from '@/utils/dateTime'

const authStore = useAuthStore()
const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = usePagePermission('admin_regulations')

// State
const regulations = ref<OvertimeRegulationContent[]>([])
const isLoading = ref(false)
const isSaving = ref(false)
const searchQuery = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const showDeletePdfModal = ref(false)
const showPdfPreviewModal = ref(false)
const isPdfFullscreen = ref(false)
const pdfPreviewUrl = ref('')
const editingReg = ref<OvertimeRegulationContent | null>(null)
const deletingRegId = ref<number | null>(null)
const isUploading = ref(false)
const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)
const pdfSuccessMessage = ref('')
let pdfMessageTimeout: ReturnType<typeof setTimeout> | null = null

const pdfDocument = ref<OvertimeRegulationDocument | null>(null)

// Overtime Limits state
const limitForm = reactive({
	max_weekly_hours: 18,
	max_monthly_hours: 72,
	recommended_weekly_hours: 15,
	recommended_monthly_hours: 60,
})
const isSavingLimits = ref(false)
const limitSaveSuccess = ref(false)
const limitSaveError = ref('')

const getLatestDocument = (docs: OvertimeRegulationDocument[]) =>
	[...docs].sort((a, b) => {
		const createdDiff = new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
		if (createdDiff !== 0) return createdDiff
		return (b.version ?? 0) - (a.version ?? 0)
	})[0]

const formData = reactive({
	title: '',
	description: '',
	order: 1,
	is_active: true,
	category: 'general',
})

const errors = reactive({
	title: '',
	description: '',
	order: '',
})

import { getSortIcon as _getSortIcon } from '@/utils/getSortIcon'

const sortBy = ref<'order' | 'title' | 'description' | 'is_active' | null>('order')
const sortOrder = ref<'asc' | 'desc'>('asc')
const pageSizeOptions = [5, 10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)

const resetForm = () => {
	formData.title = ''
	formData.description = ''
	// Auto-increment order from latest regulation
	const maxOrder =
		regulations.value.length > 0 ? Math.max(...regulations.value.map((r) => r.order || 0)) : 0
	formData.order = maxOrder + 1
	formData.is_active = true
	formData.category = 'general'
	errors.title = ''
	errors.description = ''
	errors.order = ''
	editingReg.value = null
}

const filteredRegulations = computed(() => {
	if (!searchQuery.value.trim()) return regulations.value
	const query = searchQuery.value.toLowerCase()
	return regulations.value.filter(
		(reg) => reg.title.toLowerCase().includes(query) || reg.description.toLowerCase().includes(query),
	)
})

const sortedRegulations = computed(() => {
	// If no sort applied, return filtered data as-is
	if (!sortBy.value) return filteredRegulations.value

	const sorted = [...filteredRegulations.value].sort((a, b) => {
		let aVal: string | boolean | number = a[sortBy.value!]
		let bVal: string | boolean | number = b[sortBy.value!]

		if (typeof aVal === 'string' && typeof bVal === 'string') {
			aVal = aVal.toLowerCase()
			bVal = bVal.toLowerCase()
		}

		if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
		if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
		return 0
	})
	return sorted
})

const totalPages = computed(() =>
	Math.max(1, Math.ceil(sortedRegulations.value.length / pageSize.value)),
)
const paginatedRegulations = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value
	const end = start + pageSize.value
	return sortedRegulations.value.slice(start, end)
})
const pageRangeStart = computed(() =>
	sortedRegulations.value.length === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1,
)
const pageRangeEnd = computed(() =>
	Math.min(sortedRegulations.value.length, currentPage.value * pageSize.value),
)

const toggleSort = (field: 'order' | 'title' | 'description' | 'is_active') => {
	// If clicking the same field that's currently sorted
	if (sortBy.value === field) {
		// Cycle: asc -> desc -> unsorted
		if (sortOrder.value === 'asc') {
			sortOrder.value = 'desc'
		} else {
			// Reset to unsorted
			sortBy.value = null
		}
	} else {
		// Clicking a different field, start with ascending
		sortBy.value = field
		sortOrder.value = 'asc'
	}
}

const getSortIcon = (field: 'order' | 'title' | 'description' | 'is_active') =>
	_getSortIcon(field, sortBy, sortOrder)

const goToPage = (page: number) => {
	if (page < 1 || page > totalPages.value) return
	currentPage.value = page
}

watch([pageSize, () => sortedRegulations.value.length], () => {
	currentPage.value = 1
})

// Manage body scroll lock and provide console hint when PDF modal opens
watch(showPdfPreviewModal, (newValue) => {
	document.body.style.overflow = newValue ? 'hidden' : ''
})

const handleEdit = (reg: OvertimeRegulationContent) => {
	editingReg.value = reg
	formData.title = reg.title
	formData.description = reg.description
	formData.order = reg.order
	formData.is_active = reg.is_active
	formData.category = reg.category
	showEditModal.value = true
}

const openCreateModal = () => {
	resetForm()
	showCreateModal.value = true
}

const handleDelete = (id: number) => {
	deletingRegId.value = id
	showDeleteModal.value = true
}

const confirmDelete = async () => {
	if (deletingRegId.value !== null) {
		try {
			await regulationAPI.delete(deletingRegId.value)
			regulations.value = regulations.value.filter((r) => r.id !== deletingRegId.value)
			showDeleteModal.value = false
			deletingRegId.value = null
		} catch (error) {
			console.error('Failed to delete regulation:', error)
		}
	}
}

const cancelDelete = () => {
	showDeleteModal.value = false
	deletingRegId.value = null
}

const handleToggleEnabled = async (id: number, currentStatus: boolean) => {
	try {
		const updated = await regulationAPI.update(id, {
			is_active: !currentStatus,
		})
		const idx = regulations.value.findIndex((r) => r.id === id)
		if (idx >= 0) {
			regulations.value[idx] = updated
		}
	} catch (error) {
		console.error('Failed to toggle status:', error)
	}
}

const handleSave = async () => {
	errors.title = ''
	errors.description = ''
	errors.order = ''

	if (!formData.title.trim()) {
		errors.title = t('admin.reg.titleRequired')
		return
	}
	if (!formData.description.trim()) {
		errors.description = t('admin.reg.descriptionRequired')
		return
	}
	if (!formData.order || formData.order < 1) {
		errors.order = t('admin.reg.orderPositive')
		return
	}

	isSaving.value = true
	try {
		const payload: Partial<OvertimeRegulationContent> = {
			title: formData.title,
			description: formData.description,
			order: formData.order,
			is_active: formData.is_active,
			category: formData.category,
		}

		if (editingReg.value) {
			// Update existing regulation
			const updated = await regulationAPI.update(editingReg.value.id, payload)
			const idx = regulations.value.findIndex((r) => r.id === editingReg.value!.id)
			if (idx >= 0) {
				regulations.value[idx] = updated
			}
		} else {
			// Create new regulation
			const newReg = await regulationAPI.create(
				payload as Omit<OvertimeRegulationContent, 'id' | 'created_at' | 'updated_at'>,
			)
			regulations.value.push(newReg)
		}
		showCreateModal.value = false
		showEditModal.value = false
		resetForm()
	} catch (error) {
		console.error('Failed to save regulation:', error)
		if (typeof error === 'object' && error !== null && 'response' in error) {
			const err = error as {
				response?: {
					data?: { title?: string | string[]; description?: string | string[] }
				}
			}
			if (err.response?.data?.title) {
				const titleError = Array.isArray(err.response.data.title)
					? err.response.data.title[0]
					: err.response.data.title
				errors.title = titleError ?? ''
			}
			if (err.response?.data?.description) {
				const descError = Array.isArray(err.response.data.description)
					? err.response.data.description[0]
					: err.response.data.description
				errors.description = descError ?? ''
			}
		}
	} finally {
		isSaving.value = false
	}
}

const loadPdfDocument = async () => {
	try {
		const response = await regulationDocumentAPI.list({
			is_active: true,
			page_size: 100,
		})
		if (response.results && response.results.length > 0) {
			pdfDocument.value = getLatestDocument(response.results) ?? null
		}
	} catch (error) {
		console.error('Failed to load PDF document:', error)
	}
}

const formatDate = (dateStr: string) => {
	return formatLocalDateTime(dateStr)
}

const handleFileChange = async (event: Event) => {
	const target = event.target as HTMLInputElement
	const file = target.files?.[0]

	if (!file) return

	await processFile(file)

	if (fileInput.value) {
		fileInput.value.value = ''
	}
}

const processFile = async (file: File) => {
	if (file.type !== 'application/pdf') {
		alert(t('admin.reg.pleaseUploadPdf'))
		return
	}

	if (file.size > 10 * 1024 * 1024) {
		alert(t('admin.reg.fileSizeLimit'))
		return
	}

	isUploading.value = true

	try {
		const formData = new FormData()
		formData.append('file', file)
		formData.append('title', file.name)
		formData.append('description', t('admin.reg.defaultDocDescription'))
		formData.append('is_active', 'true')

		// Set uploaded_by if user is authenticated
		if (authStore.user?.id) {
			formData.append('uploaded_by', String(authStore.user.id))
		}

		const doc = await regulationDocumentAPI.upload(formData)
		pdfDocument.value = doc

		showPdfSuccess(t('admin.reg.docUploaded'))
	} catch (error) {
		console.error('Failed to upload document:', error)
		alert(t('admin.reg.docUploadFailed'))
	} finally {
		isUploading.value = false
	}
}

const onDragOver = () => {
	isDragOver.value = true
}

const onDragLeave = () => {
	isDragOver.value = false
}

const onDrop = async (event: DragEvent) => {
	isDragOver.value = false
	const file = event.dataTransfer?.files?.[0]
	if (!file) return
	await processFile(file)
}

const confirmDeletePdf = async () => {
	try {
		if (pdfDocument.value?.id) {
			await regulationDocumentAPI.delete(pdfDocument.value.id)
		}
		pdfDocument.value = null
		localStorage.removeItem('ot_policy_document')
		showPdfSuccess(t('admin.reg.docDeleted'))
	} catch (error) {
		console.error('Failed to delete policy document:', error)
		showPdfSuccess(t('admin.reg.docDeleteFailed'))
	} finally {
		showDeletePdfModal.value = false
	}
}

const showPdfSuccess = (message: string) => {
	pdfSuccessMessage.value = message
	if (pdfMessageTimeout) {
		clearTimeout(pdfMessageTimeout)
	}
	pdfMessageTimeout = setTimeout(() => {
		pdfSuccessMessage.value = ''
	}, 4000)
}

const handleEscKey = (event: KeyboardEvent) => {
	if (showPdfPreviewModal.value) {
		if (event.key === ' ' || event.code === 'Space') {
			event.preventDefault()
			togglePdfFullscreen()
		} else if (event.key === 'Escape' || event.code === 'Escape') {
			closePdfPreview()
		}
		return
	}
	if (event.key === 'Escape') {
		if (showDeletePdfModal.value) {
			showDeletePdfModal.value = false
		} else if (showDeleteModal.value) {
			cancelDelete()
		} else if (showCreateModal.value || showEditModal.value) {
			showCreateModal.value = false
			showEditModal.value = false
		}
	}
}

const togglePdfFullscreen = () => {
	isPdfFullscreen.value = !isPdfFullscreen.value
}

const closePdfPreview = () => {
	showPdfPreviewModal.value = false
	isPdfFullscreen.value = false
}

const handlePreviewPdf = (fileUrl: string) => {
	const isAbsolute = /^https?:\/\//i.test(fileUrl)
	const normalized = fileUrl.startsWith('/') ? fileUrl : `/${fileUrl}`
	const resolvedUrl = isAbsolute ? fileUrl : `${window.location.origin}${normalized}`
	pdfPreviewUrl.value = resolvedUrl
	showPdfPreviewModal.value = true
}

// Load initial data from API
async function loadLimits() {
	try {
		const data = await overtimeLimitAPI.getActive()
		limitForm.max_weekly_hours = Number(data.max_weekly_hours)
		limitForm.max_monthly_hours = Number(data.max_monthly_hours)
		limitForm.recommended_weekly_hours = Number(data.recommended_weekly_hours)
		limitForm.recommended_monthly_hours = Number(data.recommended_monthly_hours)
	} catch (error) {
		console.warn('Failed to load overtime limits:', error)
	}
}

async function saveLimits() {
	isSavingLimits.value = true
	limitSaveSuccess.value = false
	limitSaveError.value = ''
	try {
		await overtimeLimitAPI.updateLimits({
			max_weekly_hours: limitForm.max_weekly_hours,
			max_monthly_hours: limitForm.max_monthly_hours,
			recommended_weekly_hours: limitForm.recommended_weekly_hours,
			recommended_monthly_hours: limitForm.recommended_monthly_hours,
		})
		limitSaveSuccess.value = true
		setTimeout(() => {
			limitSaveSuccess.value = false
		}, 3000)
	} catch (error) {
		limitSaveError.value = t('admin.reg.limitsSaveError')
		console.error('Failed to save overtime limits:', error)
	} finally {
		isSavingLimits.value = false
	}
}

onMounted(async () => {
	isLoading.value = true
	try {
		const data = await regulationAPI.list({ page_size: 100 })
		regulations.value = Array.isArray(data) ? data : data.results || []
		resetForm()
	} catch (error) {
		console.error('Failed to load regulations:', error)
	} finally {
		isLoading.value = false
	}

	loadPdfDocument()
	loadLimits()
	window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', handleEscKey)
	// Ensure body overflow is restored
	document.body.style.overflow = ''
	if (pdfMessageTimeout) {
		clearTimeout(pdfMessageTimeout)
	}
})
</script>
