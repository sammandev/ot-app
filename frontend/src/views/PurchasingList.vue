<!-- @vue/component -->
<template>
    <AdminLayout>
        <div class="space-y-6 overflow-x-hidden">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.purchasingList.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.purchasingList.title')
                        }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.purchasingList.subtitle') }}</p>
                </div>
                <div class="flex gap-2">
                    <button @click="showImportModal = true"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                        {{ t('purchasing.import') }}
                    </button>
                    <button @click="showExportMenu = !showExportMenu"
                        class="relative h-11 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                        {{ t('purchasing.exportMenu') }}
                        <div v-if="showExportMenu"
                            class="absolute top-full right-0 mt-1 w-36 rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900 z-50">
                            <button @click="exportData('csv')"
                                class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">{{
                                t('common.csv') }}</button>
                            <button @click="exportData('xlsx')"
                                class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">{{
                                t('common.xlsx') }}</button>
                        </div>
                    </button>
                    <router-link v-if="canCreate" to="/purchasing/request"
                        class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 flex items-center">
                        {{ t('purchasing.newRequest') }}
                    </router-link>
                </div>
            </div>

            <!-- Search -->
            <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
                    <input v-model="searchQuery" type="text" :placeholder="t('purchasing.searchPlaceholder')"
                        class="dark:bg-dark-900 h-11 flex-1 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                        @keyup.enter="handleSearch" />
                    <button @click="handleSearch"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                        {{ t('common.search') }}
                    </button>
                </div>
            </div>

            <!-- Tabs -->
            <div class="border-b border-gray-200 dark:border-gray-800">
                <nav class="flex -mb-px gap-6" aria-label="Tabs">
                    <button v-for="tab in tabs" :key="tab.key" @click="switchTab(tab.key)" :class="[
                        'py-3 px-1 text-sm font-medium border-b-2 transition whitespace-nowrap',
                        activeTab === tab.key
                            ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
                    ]">
                        {{ t(tab.label) }}
                        <span class="ml-2 rounded-full bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">{{ tab.count
                            }}</span>
                    </button>
                </nav>
            </div>

            <!-- Loading State -->
            <TableSkeleton v-if="isLoading" :rows="8" :columns="9" />

            <!-- Empty State -->
            <div v-else-if="purchaseRequests.length === 0"
                class="rounded-2xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-white/[0.03]">
                <p class="text-gray-500 dark:text-gray-400">{{ t('purchasing.noRequestsFound') }}</p>
                <router-link to="/purchasing/request" class="mt-2 inline-block text-brand-600 hover:underline">{{
                    t('purchasing.createNewRequest') }}</router-link>
            </div>

            <!-- Purchase Requests Table -->
            <div v-else
                class="flex flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
                style="max-height: calc(100vh - 200px)">

                <!-- Bulk Actions Bar -->
                <div v-if="selectedIds.length > 0"
                    class="flex-none flex items-center gap-3 border-b border-gray-200 bg-brand-50 px-4 py-3 dark:border-gray-800 dark:bg-brand-500/10">
                    <span class="text-sm font-medium text-brand-700 dark:text-brand-300">
                        {{ selectedIds.length }} {{ t('purchasing.selected') }}
                    </span>
                    <div class="flex gap-2 ml-auto">
                        <select v-if="canUpdate" v-model="bulkStatusTarget"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                            <option value="">{{ t('purchasing.changeStatus') }}</option>
                            <option value="pending">{{ t('purchasing.pending') }}</option>
                            <option value="done">{{ t('purchasing.doneStat') }}</option>
                            <option value="canceled">{{ t('purchasing.canceled') }}</option>
                        </select>
                        <button v-if="canUpdate && bulkStatusTarget" @click="handleBulkStatusUpdate"
                            class="h-9 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700">
                            {{ t('purchasing.applyStatus') }}
                        </button>
                        <button v-if="canDelete" @click="handleBulkDelete"
                            class="h-9 rounded-lg bg-error-600 px-4 text-sm font-medium text-white hover:bg-error-700">
                            {{ t('purchasing.deleteSelected') }}
                        </button>
                        <button @click="clearSelection"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                            {{ t('common.clear') }}
                        </button>
                    </div>
                </div>

                <div class="flex-1 overflow-auto min-h-0">
                    <table class="w-full text-sm">
                        <thead
                            class="sticky top-0 z-10 border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900/80 backdrop-blur-sm">
                            <tr>
                                <th class="px-4 py-4 text-left w-10">
                                    <input type="checkbox" :checked="isAllSelected" :indeterminate="isIndeterminate"
                                        @change="toggleSelectAll"
                                        class="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800" />
                                </th>
                                <th v-for="col in currentColumns" :key="col.key"
                                    class="px-4 py-4 text-left font-semibold text-gray-900 dark:text-white whitespace-nowrap cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-800/50 transition"
                                    :class="{ 'max-w-xs': col.key === 'description_spec' }"
                                    :aria-sort="sortField === col.key ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'"
                                    @click="toggleSort(col.key)">
                                    <div class="flex items-center gap-1">
                                        {{ t(col.label) }}
                                        <span v-if="sortField === col.key" class="text-brand-500">
                                            {{ sortDirection === 'asc' ? '▲' : '▼' }}
                                        </span>
                                        <span v-else class="text-gray-300 dark:text-gray-600">⇅</span>
                                    </div>
                                </th>
                                <th
                                    class="px-4 py-4 text-center font-semibold text-gray-900 dark:text-white whitespace-nowrap">
                                    {{ t('common.actions') }}</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                            <tr v-for="pr in purchaseRequests" :key="pr.id"
                                class="hover:bg-gray-50 dark:hover:bg-white/5"
                                :class="{ 'bg-brand-50/50 dark:bg-brand-500/5': selectedIds.includes(pr.id) }">
                                <td class="px-4 py-4">
                                    <input type="checkbox" :checked="selectedIds.includes(pr.id)"
                                        @change="toggleSelect(pr.id)"
                                        class="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800" />
                                </td>
                                <td class="px-4 py-4 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                    {{ formatDate(pr.request_date) }}
                                </td>
                                <td class="px-4 py-4 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                    {{ pr.owner_employee_details?.name || pr.owner || '-' }}
                                </td>
                                <td class="px-4 py-4 text-gray-900 dark:text-white font-medium whitespace-nowrap">
                                    {{ pr.doc_id || '-' }}
                                </td>
                                <td class="px-4 py-4 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                    {{ pr.part_no || '-' }}
                                </td>
                                <td class="px-4 py-4 text-gray-700 dark:text-gray-300 max-w-xs truncate"
                                    :title="pr.description_spec ?? undefined">
                                    {{ pr.description_spec || '-' }}
                                </td>
                                <!-- PR No. column - shown in pending/done tabs -->
                                <td v-if="activeTab !== 'canceled'"
                                    class="px-4 py-4 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                    {{ pr.pr_no || '-' }}
                                </td>
                                <!-- Remarks column - shown in canceled tab -->
                                <td v-if="activeTab === 'canceled'"
                                    class="px-4 py-4 text-gray-700 dark:text-gray-300 max-w-xs truncate"
                                    :title="pr.remarks ?? undefined">
                                    {{ pr.remarks || '-' }}
                                </td>
                                <td class="px-4 py-4">
                                    <span :class="getStatusClass(pr.status)"
                                        class="rounded-full px-3 py-1 text-xs font-medium">
                                        {{ formatStatus(pr.status) }}
                                    </span>
                                </td>
                                <td class="px-4 py-4 text-center">
                                    <div class="flex justify-center gap-2">
                                        <button @click="viewDetails(pr)"
                                            class="h-8 rounded-lg border border-gray-300 px-3 text-xs font-medium text-gray-600 transition hover:bg-gray-50 focus:outline-hidden dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800">
                                            {{ t('common.view') }}
                                        </button>
                                        <button v-if="canUpdate" @click="editRequest(pr)"
                                            class="h-8 rounded-lg border border-brand-300 px-3 text-xs font-medium text-brand-600 transition hover:bg-brand-50 focus:outline-hidden dark:border-brand-500/30 dark:text-brand-400 dark:hover:bg-brand-500/10">
                                            {{ t('common.edit') }}
                                        </button>
                                        <button v-if="canDelete" @click="deleteRequest(pr.id)"
                                            class="h-8 rounded-lg border border-error-300 px-3 text-xs font-medium text-error-600 transition hover:bg-error-50 focus:outline-hidden dark:border-error-500/30 dark:text-error-400 dark:hover:bg-error-500/10">
                                            {{ t('common.delete') }}
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div
                    class="flex-none flex flex-col gap-3 border-t border-gray-200 px-6 py-4 text-sm text-gray-700 dark:border-gray-800 dark:text-gray-300 sm:flex-row sm:items-center sm:justify-between">
                    <div class="flex items-center gap-3">
                        <p>{{ t('common.showing') }} {{ pageRangeStart }}-{{ pageRangeEnd }} {{ t('common.of') }} {{
                            totalCount }}</p>
                        <select v-model.number="pageSize" @change="handleSearch"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                            <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} / {{
                                t('common.page') }}</option>
                        </select>
                    </div>
                    <div class="flex items-center gap-2">
                        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.prev') }}
                        </button>
                        <span>{{ t('common.page') }} {{ currentPage }} {{ t('common.of') }} {{ totalPages }}</span>
                        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.next') }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- View/Edit Modal -->
            <div v-if="showDetailModal || showEditModal"
                class="fixed inset-0 z-[100000] flex items-center justify-center" role="dialog" aria-modal="true"
                aria-labelledby="purchase-detail-modal-title">
                <div class="absolute inset-0 bg-black/50" @click="closeModals"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white w-full max-w-2xl max-h-[90vh] flex flex-col dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <!-- Sticky Header -->
                    <div
                        class="sticky top-0 z-10 flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-t-2xl">
                        <h2 id="purchase-detail-modal-title"
                            class="text-xl font-semibold text-gray-900 dark:text-white">
                            {{ showEditModal ? t('purchasing.editPurchaseRequest') :
                                t('purchasing.purchaseRequestDetails') }}
                        </h2>
                        <button @click="closeModals" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                            <XIcon class="w-6 h-6" />
                        </button>
                    </div>

                    <!-- Scrollable Body -->
                    <div class="flex-1 overflow-y-auto px-6 py-4">
                        <form v-if="showEditModal" @submit.prevent="saveRequest" class="space-y-4" id="editForm">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.requestDate') }}</label>
                                    <input ref="requestDateInput" type="text" v-model="editForm.request_date"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.selectDate')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.owner') }}</label>
                                    <input v-model="editForm.owner" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.ownerName')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.docId') }}</label>
                                    <input v-model="editForm.doc_id" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.documentId')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.partNo') }}</label>
                                    <input v-model="editForm.part_no" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.partNumber')" />
                                </div>
                                <div class="space-y-2 md:col-span-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.descriptionSpec') }}</label>
                                    <textarea v-model="editForm.description_spec" rows="2"
                                        class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('common.description')"></textarea>
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.materialCategory') }}</label>
                                    <input v-model="editForm.material_category" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.materialCategory')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.purposeDesc') }}</label>
                                    <input v-model="editForm.purpose_desc" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.purpose')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.qty') }}</label>
                                    <input v-model.number="editForm.qty" type="number" min="1"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        placeholder="1" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.plant') }}</label>
                                    <input v-model="editForm.plant" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.plant')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.projectCode') }}</label>
                                    <input v-model="editForm.project_code" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.projectCode')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.prType') }}</label>
                                    <input v-model="editForm.pr_type" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.prType')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.mrpid') }}</label>
                                    <input v-model="editForm.mrp_id" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.mrpid')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.purchOrg') }}</label>
                                    <input v-model="editForm.purch_org" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.purchOrg')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.sourcerPrice') }}</label>
                                    <input v-model="editForm.sourcer_price" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.sourcerPrice')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.prNo') }}</label>
                                    <input v-model="editForm.pr_no" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.prNo')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.status') }}</label>
                                    <select v-model="editForm.status"
                                        class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                                        <option value="pending">{{ t('purchasing.pending') }}</option>
                                        <option value="done">{{ t('purchasing.doneStat') }}</option>
                                        <option value="canceled">{{ t('purchasing.canceled') }}</option>
                                    </select>
                                </div>
                                <div class="space-y-2 md:col-span-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                        t('purchasing.remarks') }}</label>
                                    <textarea v-model="editForm.remarks" rows="2"
                                        class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('purchasing.remarks')"></textarea>
                                </div>
                            </div>
                        </form>

                        <!-- View Mode -->
                        <div v-else class="space-y-4">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.requestDate')
                                        }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        formatDate(selectedRequest?.request_date ?? null) || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.owner') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.owner_employee_details?.name || selectedRequest?.owner || '-'
                                        }}
                                    </p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.docId') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.doc_id || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.partNo') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.part_no || '-' }}</p>
                                </div>
                                <div class="md:col-span-2">
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{
                                        t('purchasing.descriptionSpec') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.description_spec || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{
                                        t('purchasing.materialCategory') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.material_category || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.purpose') }}
                                    </p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.purpose_desc || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.qty') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        formatNumber(selectedRequest?.qty) }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.plant') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.plant || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.projectCode')
                                        }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.project_code || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.prType') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.pr_type || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.mrpid') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.mrp_id || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.purchOrg') }}
                                    </p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.purch_org || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.sourcerPrice')
                                        }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.sourcer_price || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.prNo') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.pr_no || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.status') }}</p>
                                    <span :class="getStatusClass(selectedRequest?.status || 'pending')"
                                        class="rounded-full px-3 py-1 text-xs font-medium">
                                        {{ formatStatus(selectedRequest?.status || 'pending') }}
                                    </span>
                                </div>
                                <div class="md:col-span-2">
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('purchasing.remarks') }}
                                    </p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{
                                        selectedRequest?.remarks || '-' }}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Sticky Footer -->
                    <div
                        class="sticky bottom-0 z-10 flex gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-b-2xl">
                        <template v-if="showEditModal">
                            <button type="button" @click="closeModals"
                                class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                {{ t('common.cancel') }}
                            </button>
                            <button @click="saveRequest" :disabled="isSaving"
                                class="h-11 flex-1 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 disabled:opacity-50">
                                {{ isSaving ? t('common.saving') : t('purchasing.saveChanges') }}
                            </button>
                        </template>
                        <template v-else>
                            <button @click="closeModals"
                                class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                {{ t('common.close') }}
                            </button>
                            <button v-if="canUpdate" @click="editRequest(selectedRequest!)"
                                class="h-11 flex-1 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700">
                                {{ t('common.edit') }}
                            </button>
                        </template>
                    </div>
                </div>
            </div>

            <!-- Import Modal -->
            <div v-if="showImportModal" class="fixed inset-0 z-[100000] flex items-center justify-center" role="dialog"
                aria-modal="true" aria-labelledby="purchase-import-modal-title">
                <div class="absolute inset-0 bg-black/50" @click="showImportModal = false"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white w-full max-w-md flex flex-col dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <!-- Header -->
                    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h2 id="purchase-import-modal-title"
                            class="text-xl font-semibold text-gray-900 dark:text-white">{{
                                t('purchasing.importPurchaseRequests') }}</h2>
                    </div>
                    <!-- Body -->
                    <div class="px-6 py-4">
                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                            {{ t('purchasing.importDescription') }}
                        </p>
                        <ul class="text-xs text-gray-500 dark:text-gray-400 mb-4 space-y-1 list-disc list-inside">
                            <li>{{ t('purchasing.importSheetPending') }}</li>
                            <li>{{ t('purchasing.importSheetDone') }}</li>
                            <li>{{ t('purchasing.importSheetCancel') }}</li>
                        </ul>
                        <div class="space-y-4">
                            <div
                                class="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-6 text-center">
                                <input type="file" ref="importFileInput" @change="handleFileSelect"
                                    accept=".csv,.xlsx,.xls" class="hidden" />
                                <button @click="($refs.importFileInput as HTMLInputElement).click()"
                                    class="text-brand-600 dark:text-brand-400 hover:underline">
                                    {{ t('purchasing.clickToSelectFile') }}
                                </button>
                                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">{{
                                    t('purchasing.supportsFormats') }}</p>
                                <p v-if="importFile" class="text-sm text-gray-700 dark:text-gray-300 mt-2">
                                    {{ t('purchasing.selectedFile') }} {{ importFile.name }}
                                </p>
                            </div>
                        </div>
                    </div>
                    <!-- Footer -->
                    <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex gap-3">
                        <button @click="showImportModal = false"
                            class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.cancel') }}
                        </button>
                        <button @click="importData" :disabled="!importFile || isImporting"
                            class="h-11 flex-1 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 disabled:opacity-50">
                            {{ isImporting ? t('purchasing.importing') : t('purchasing.import') }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Delete Confirmation Modal -->
            <div v-if="showDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center" role="dialog"
                aria-modal="true" aria-labelledby="purchase-delete-modal-title">
                <div class="absolute inset-0 bg-black/50" @click="showDeleteModal = false"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <h2 id="purchase-delete-modal-title"
                        class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{{
                            t('purchasing.deletePurchaseRequest') }}</h2>
                    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ t('purchasing.deleteRequestMsg') }}</p>
                    <div class="flex gap-3">
                        <button @click="showDeleteModal = false"
                            class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.cancel') }}
                        </button>
                        <button @click="confirmDelete" :disabled="isDeleting"
                            class="h-11 flex-1 rounded-lg bg-error-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 disabled:opacity-50">
                            {{ isDeleting ? t('common.deleting') : t('common.delete') }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Bulk Delete Confirmation Modal -->
            <div v-if="showBulkDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center"
                role="dialog" aria-modal="true" aria-labelledby="purchase-bulk-delete-modal-title">
                <div class="absolute inset-0 bg-black/50" @click="showBulkDeleteModal = false"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <h2 id="purchase-bulk-delete-modal-title"
                        class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{{
                            t('purchasing.deleteSelected') }}</h2>
                    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ t('purchasing.deleteBulkMsg', {
                        count:
                        selectedIds.length })
                        }}</p>
                    <div class="flex gap-3">
                        <button @click="showBulkDeleteModal = false"
                            class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.cancel') }}
                        </button>
                        <button @click="confirmBulkDelete" :disabled="isDeleting"
                            class="h-11 flex-1 rounded-lg bg-error-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 disabled:opacity-50">
                            {{ isDeleting ? t('common.deleting') : t('purchasing.deleteAll') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
import flatpickr from 'flatpickr'
import { computed, nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
import { usePagePermission } from '@/composables/usePagePermission'
import { useToast } from '@/composables/useToast'
import { XIcon } from '@/icons'
import { type PurchaseRequest, purchaseRequestAPI } from '@/services/api/purchase-request'

const { showToast } = useToast()
const { canCreate, canUpdate, canDelete } = usePagePermission('purchasing')
const { t } = useI18n()

// Format number: strip trailing zeros (1.00 → 1, 1.50 → 1.5)
const formatNumber = (val: number | string | null | undefined): string => {
	if (val == null) return '1'
	const n = typeof val === 'string' ? parseFloat(val) : val
	if (Number.isNaN(n)) return '1'
	return String(parseFloat(n.toFixed(2)))
}

// Tabs
type TabKey = 'pending' | 'done' | 'canceled'

const tabs = ref([
	{ key: 'pending' as TabKey, label: 'purchasing.tabListOfPurchase', count: 0 },
	{ key: 'done' as TabKey, label: 'purchasing.tabDone', count: 0 },
	{ key: 'canceled' as TabKey, label: 'purchasing.tabCancelPurchase', count: 0 },
])
const activeTab = ref<TabKey>('pending')

// Columns per tab
const baseColumns = [
	{ key: 'request_date', label: 'purchasing.colRequestDate' },
	{ key: 'owner', label: 'purchasing.colOwner' },
	{ key: 'doc_id', label: 'purchasing.colDocId' },
	{ key: 'part_no', label: 'purchasing.colPartNo' },
	{ key: 'description_spec', label: 'purchasing.colDescription' },
]
const pendingDoneColumns = [
	...baseColumns,
	{ key: 'pr_no', label: 'purchasing.colPrNo' },
	{ key: 'status', label: 'purchasing.colStatus' },
]
const canceledColumns = [
	...baseColumns,
	{ key: 'remarks', label: 'purchasing.colCancelReason' },
	{ key: 'status', label: 'purchasing.colStatus' },
]

const currentColumns = computed(() =>
	activeTab.value === 'canceled' ? canceledColumns : pendingDoneColumns,
)

// State
const isLoading = ref(false)
const purchaseRequests = ref<PurchaseRequest[]>([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [10, 20, 50, 100]
const searchQuery = ref('')

// Sorting
const sortField = ref('request_date')
const sortDirection = ref<'asc' | 'desc'>('desc')

// Selection
const selectedIds = ref<number[]>([])
const bulkStatusTarget = ref('')

const isAllSelected = computed(
	() =>
		purchaseRequests.value.length > 0 &&
		purchaseRequests.value.every((pr) => selectedIds.value.includes(pr.id)),
)
const isIndeterminate = computed(() => selectedIds.value.length > 0 && !isAllSelected.value)

// Modals
const showDetailModal = ref(false)
const showEditModal = ref(false)
const showImportModal = ref(false)
const showDeleteModal = ref(false)
const showBulkDeleteModal = ref(false)
const showExportMenu = ref(false)
const selectedRequest = ref<PurchaseRequest | null>(null)
const deleteId = ref<number | null>(null)

// Form
const editForm = ref({
	request_date: '',
	owner: '',
	doc_id: '',
	part_no: '',
	description_spec: '',
	material_category: '',
	purpose_desc: '',
	qty: 1,
	plant: '',
	project_code: '',
	pr_type: '',
	mrp_id: '',
	purch_org: '',
	sourcer_price: '',
	pr_no: '',
	remarks: '',
	status: 'pending' as 'pending' | 'done' | 'canceled',
})
const isSaving = ref(false)
const isDeleting = ref(false)
const isImporting = ref(false)
const importFile = ref<File | null>(null)
const requestDateInput = ref<HTMLInputElement | null>(null)
let requestDatePicker: flatpickr.Instance | null = null

// Computed
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value) || 1)
const pageRangeStart = computed(() =>
	totalCount.value > 0 ? (currentPage.value - 1) * pageSize.value + 1 : 0,
)
const pageRangeEnd = computed(() => Math.min(currentPage.value * pageSize.value, totalCount.value))

// Methods
const formatDate = (date: string | null) => {
	if (!date) return '-'
	return new Date(date).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
	})
}

const formatStatus = (status: string) => {
	return status.charAt(0).toUpperCase() + status.slice(1)
}

const getStatusClass = (status: string) => {
	switch (status) {
		case 'done':
			return 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300'
		case 'canceled':
			return 'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300'
		default:
			return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-500/20 dark:text-yellow-300'
	}
}

const getOrdering = () => {
	const prefix = sortDirection.value === 'desc' ? '-' : ''
	return `${prefix}${sortField.value}`
}

const loadData = async () => {
	isLoading.value = true
	try {
		const response = await purchaseRequestAPI.list({
			page: currentPage.value,
			page_size: pageSize.value,
			search: searchQuery.value || undefined,
			status: activeTab.value,
			ordering: getOrdering(),
		})
		purchaseRequests.value = response.results
		totalCount.value = response.count

		// Update current tab count
		const tab = tabs.value.find((t) => t.key === activeTab.value)
		if (tab) tab.count = response.count
	} catch (error) {
		console.error('Failed to load purchase requests:', error)
		showToast(t('purchasing.loadFailed'), 'error')
	} finally {
		isLoading.value = false
	}
}

const loadTabCounts = async () => {
	try {
		const [pending, done, canceled] = await Promise.all([
			purchaseRequestAPI.list({
				page: 1,
				page_size: 1,
				status: 'pending',
				search: searchQuery.value || undefined,
			}),
			purchaseRequestAPI.list({
				page: 1,
				page_size: 1,
				status: 'done',
				search: searchQuery.value || undefined,
			}),
			purchaseRequestAPI.list({
				page: 1,
				page_size: 1,
				status: 'canceled',
				search: searchQuery.value || undefined,
			}),
		])
		tabs.value[0]!.count = pending.count
		tabs.value[1]!.count = done.count
		tabs.value[2]!.count = canceled.count
	} catch {
		// Silently ignore count errors
	}
}

const switchTab = (tab: TabKey) => {
	activeTab.value = tab
	currentPage.value = 1
	clearSelection()
	loadData()
}

const handleSearch = () => {
	currentPage.value = 1
	clearSelection()
	loadData()
	loadTabCounts()
}

const goToPage = (page: number) => {
	if (page >= 1 && page <= totalPages.value) {
		currentPage.value = page
		clearSelection()
		loadData()
	}
}

const toggleSort = (field: string) => {
	if (sortField.value === field) {
		sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
	} else {
		sortField.value = field
		sortDirection.value = 'asc'
	}
	currentPage.value = 1
	loadData()
}

// Selection
const toggleSelectAll = () => {
	if (isAllSelected.value) {
		selectedIds.value = []
	} else {
		selectedIds.value = purchaseRequests.value.map((pr) => pr.id)
	}
}

const toggleSelect = (id: number) => {
	const idx = selectedIds.value.indexOf(id)
	if (idx > -1) {
		selectedIds.value.splice(idx, 1)
	} else {
		selectedIds.value.push(id)
	}
}

const clearSelection = () => {
	selectedIds.value = []
	bulkStatusTarget.value = ''
}

const handleBulkDelete = () => {
	showBulkDeleteModal.value = true
}

const confirmBulkDelete = async () => {
	isDeleting.value = true
	try {
		const result = await purchaseRequestAPI.bulkDelete(selectedIds.value)
		showToast(result.message, 'success')
		showBulkDeleteModal.value = false
		clearSelection()
		loadData()
		loadTabCounts()
	} catch (error) {
		console.error('Failed to bulk delete:', error)
		showToast(t('purchasing.deleteBulkFailed'), 'error')
	} finally {
		isDeleting.value = false
	}
}

const handleBulkStatusUpdate = async () => {
	if (!bulkStatusTarget.value) return
	try {
		const result = await purchaseRequestAPI.bulkUpdateStatus(
			selectedIds.value,
			bulkStatusTarget.value,
		)
		showToast(result.message, 'success')
		clearSelection()
		loadData()
		loadTabCounts()
	} catch (error) {
		console.error('Failed to bulk update status:', error)
		showToast(t('purchasing.updateStatusFailed'), 'error')
	}
}

const viewDetails = (pr: PurchaseRequest) => {
	selectedRequest.value = pr
	showDetailModal.value = true
}

const editRequest = (pr: PurchaseRequest) => {
	selectedRequest.value = pr
	editForm.value = {
		request_date: pr.request_date || '',
		owner: pr.owner || '',
		doc_id: pr.doc_id || '',
		part_no: pr.part_no || '',
		description_spec: pr.description_spec || '',
		material_category: pr.material_category || '',
		purpose_desc: pr.purpose_desc || '',
		qty: pr.qty || 1,
		plant: pr.plant || '',
		project_code: pr.project_code || '',
		pr_type: pr.pr_type || '',
		mrp_id: pr.mrp_id || '',
		purch_org: pr.purch_org || '',
		sourcer_price: pr.sourcer_price || '',
		pr_no: pr.pr_no || '',
		remarks: pr.remarks || '',
		status: pr.status || 'pending',
	}
	showDetailModal.value = false
	showEditModal.value = true

	nextTick(() => {
		initDatePicker()
	})
}

const initDatePicker = () => {
	if (requestDatePicker) {
		requestDatePicker.destroy()
	}
	if (requestDateInput.value) {
		requestDatePicker = flatpickr(requestDateInput.value, {
			dateFormat: 'Y-m-d',
			defaultDate: editForm.value.request_date || undefined,
			onChange: (selectedDates) => {
				if (selectedDates.length > 0 && selectedDates[0]) {
					const dateStr = selectedDates[0].toISOString().split('T')[0]
					editForm.value.request_date = dateStr ?? ''
				}
			},
		})
	}
}

const saveRequest = async () => {
	if (!selectedRequest.value) return

	isSaving.value = true
	try {
		await purchaseRequestAPI.update(selectedRequest.value.id, editForm.value)
		showToast(t('purchasing.requestUpdated'), 'success')
		closeModals()
		loadData()
		loadTabCounts()
	} catch (error) {
		console.error('Failed to save purchase request:', error)
		showToast(t('purchasing.requestSaveFailed'), 'error')
	} finally {
		isSaving.value = false
	}
}

const deleteRequest = (id: number) => {
	deleteId.value = id
	showDeleteModal.value = true
}

const confirmDelete = async () => {
	if (!deleteId.value) return

	isDeleting.value = true
	try {
		await purchaseRequestAPI.delete(deleteId.value)
		showToast(t('purchasing.requestDeleted'), 'success')
		showDeleteModal.value = false
		loadData()
		loadTabCounts()
	} catch (error) {
		console.error('Failed to delete purchase request:', error)
		showToast(t('purchasing.requestDeleteFailed'), 'error')
	} finally {
		isDeleting.value = false
	}
}

const closeModals = () => {
	showDetailModal.value = false
	showEditModal.value = false
	selectedRequest.value = null
	if (requestDatePicker) {
		requestDatePicker.destroy()
		requestDatePicker = null
	}
}

const handleFileSelect = (event: Event) => {
	const target = event.target as HTMLInputElement
	if (target.files && target.files.length > 0 && target.files[0]) {
		importFile.value = target.files[0]
	}
}

const importData = async () => {
	if (!importFile.value) return

	isImporting.value = true
	try {
		const result = await purchaseRequestAPI.importData(importFile.value)
		showToast(result.message, 'success')
		showImportModal.value = false
		importFile.value = null
		loadData()
		loadTabCounts()
	} catch (error) {
		console.error('Failed to import data:', error)
		showToast(t('purchasing.importFailed'), 'error')
	} finally {
		isImporting.value = false
	}
}

const exportData = async (format: 'csv' | 'xlsx') => {
	showExportMenu.value = false

	try {
		// Fetch all data for export (not just current page)
		const allData: Record<string, unknown>[] = []
		let page = 1
		let hasMore = true
		while (hasMore) {
			const response = await purchaseRequestAPI.list({
				page,
				page_size: 100,
				status: activeTab.value,
				search: searchQuery.value || undefined,
				ordering: getOrdering(),
			})
			response.results.forEach((pr) => {
				allData.push({
					[t('purchasing.requestDate')]: pr.request_date || '',
					[t('purchasing.owner')]: pr.owner_employee_details?.name || pr.owner || '',
					[t('purchasing.docId')]: pr.doc_id || '',
					[t('purchasing.partNo')]: pr.part_no || '',
					[t('purchasing.descriptionSpec')]: pr.description_spec || '',
					[t('purchasing.materialCategory')]: pr.material_category || '',
					[t('purchasing.purposeDesc')]: pr.purpose_desc || '',
					[t('purchasing.qty')]: formatNumber(pr.qty),
					[t('purchasing.plant')]: pr.plant || '',
					[t('purchasing.projectCode')]: pr.project_code || '',
					[t('purchasing.prType')]: pr.pr_type || '',
					[t('purchasing.mrpid')]: pr.mrp_id || '',
					[t('purchasing.purchOrg')]: pr.purch_org || '',
					[t('purchasing.sourcerPrice')]: pr.sourcer_price || '',
					[t('purchasing.prNo')]: pr.pr_no || '',
					[t('purchasing.remarks')]: pr.remarks || '',
					[t('purchasing.status')]: pr.status || '',
				})
			})
			hasMore = !!response.next
			page++
		}

		if (allData.length === 0) {
			showToast(t('purchasing.noDataToExport'), 'info')
			return
		}

		const dateStr = new Date().toISOString().split('T')[0]
		const tabLabel = tabs.value.find((tb) => tb.key === activeTab.value)?.label ?? activeTab.value
		const translatedTabLabel = t(tabLabel)

		if (format === 'csv') {
			const headers = Object.keys(allData[0]!)
			const csvContent = [
				headers.join(','),
				...allData.map((row) =>
					headers.map((h) => `"${(row[h] ?? '').toString().replace(/"/g, '""')}"`).join(','),
				),
			].join('\n')

			const blob = new Blob(['\uFEFF' + csvContent], {
				type: 'text/csv;charset=utf-8;',
			})
			const link = document.createElement('a')
			link.href = URL.createObjectURL(blob)
			link.download = `purchase_requests_${translatedTabLabel.replace(/\s+/g, '_')}_${dateStr}.csv`
			link.click()
			URL.revokeObjectURL(link.href)
			showToast(t('purchasing.csvExported'), 'success')
		} else if (format === 'xlsx') {
			const XLSX = await import('@e965/xlsx')
			const ws = XLSX.utils.json_to_sheet(allData)
			const wb = XLSX.utils.book_new()
			XLSX.utils.book_append_sheet(wb, ws, translatedTabLabel)
			XLSX.writeFile(
				wb,
				`purchase_requests_${translatedTabLabel.replace(/\s+/g, '_')}_${dateStr}.xlsx`,
			)
			showToast(t('purchasing.excelExported'), 'success')
		}
	} catch (error) {
		console.error('Failed to export data:', error)
		showToast(t('purchasing.exportFailed'), 'error')
	}
}

// Click outside to close export menu
const handleClickOutside = (event: MouseEvent) => {
	if (showExportMenu.value) {
		const target = event.target as HTMLElement
		if (!target.closest('.relative')) {
			showExportMenu.value = false
		}
	}
}

onMounted(() => {
	loadData()
	loadTabCounts()
	document.addEventListener('click', handleClickOutside)
})
</script>
