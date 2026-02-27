<!-- @vue/component -->
<template>
    <AdminLayout>
        <div class="space-y-6 overflow-x-hidden">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.assets.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.assets.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.assets.subtitle') }}</p>
                </div>
                <div class="flex gap-2">
                    <button @click="showImportModal = true"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                        {{ t('common.import') }}
                    </button>
                    <button @click="showExportMenu = !showExportMenu"
                        class="relative h-11 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                        {{ t('common.export') }} ▾
                        <div v-if="showExportMenu"
                            class="absolute top-full right-0 mt-1 w-36 rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900 z-50">
                            <button @click="exportData('csv')"
                                class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">{{ t('common.csv') }}</button>
                            <button @click="exportData('xlsx')"
                                class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">{{ t('common.xlsx') }}</button>
                        </div>
                    </button>
                    <button v-if="canCreate" @click="showCreateModal = true"
                        class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20">
                        {{ t('assets.addAsset') }}
                    </button>
                </div>
            </div>

            <!-- Search and Filters -->
            <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
                    <input v-model="searchQuery" type="text"
                        :placeholder="t('assets.searchPlaceholder')"
                        class="dark:bg-dark-900 h-11 flex-1 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                        @keyup.enter="handleSearch" />
                    <select v-model="departmentFilter"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                        <option value="">{{ t('assets.allDepartments') }}</option>
                        <option v-for="dept in departmentOptions" :key="dept.id" :value="dept.id">
                            {{ dept.name }}
                        </option>
                    </select>
                    <select v-model="statusFilter"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                        <option value="">{{ t('assets.allStatus') }}</option>
                        <option value="Picking">{{ t('assets.picking') }}</option>
                        <option value="Broken">{{ t('assets.broken') }}</option>
                        <option value="Received">{{ t('assets.received') }}</option>
                    </select>
                    <button @click="handleSearch"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                        {{ t('common.search') }}
                    </button>
                    <button @click="handleReset"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                        {{ t('common.reset') }}
                    </button>
                </div>
            </div>

            <!-- Loading State -->
            <TableSkeleton v-if="isLoading" :rows="10" :columns="8" />

            <!-- Empty State -->
            <div v-else-if="assets.length === 0"
                class="rounded-2xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-white/[0.03]">
                <p class="text-gray-500 dark:text-gray-400">{{ t('assets.noAssetsFound') }}</p>
                <button @click="showImportModal = true" class="mt-2 text-brand-600 hover:underline">{{ t('assets.importAssetsFromFile') }}</button>
            </div>

            <!-- Assets Table -->
            <div v-else
                class="flex flex-col rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
                style="max-height: calc(100vh - 200px)">

                <!-- Bulk Actions Bar -->
                <div v-if="selectedIds.length > 0"
                    class="flex-none flex items-center gap-3 border-b border-gray-200 bg-brand-50 px-4 py-3 dark:border-gray-800 dark:bg-brand-500/10">
                    <span class="text-sm font-medium text-brand-700 dark:text-brand-300">
                        {{ selectedIds.length }} {{ t('assets.selected') }}
                    </span>
                    <div class="flex gap-2 ml-auto">
                        <!-- Bulk Status Update -->
                        <select v-if="canUpdate" v-model="bulkStatusTarget"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                            <option value="">{{ t('assets.changeStatus') }}</option>
                            <option value="Picking">{{ t('assets.picking') }}</option>
                            <option value="Broken">{{ t('assets.broken') }}</option>
                            <option value="Received">{{ t('assets.received') }}</option>
                            <option value="__custom__">{{ t('assets.customStatus') }}</option>
                        </select>
                        <input v-if="canUpdate && bulkStatusTarget === '__custom__'" v-model="customStatusValue"
                            type="text" :placeholder="t('assets.enterStatus')"
                            class="h-9 w-36 rounded-lg border border-gray-300 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                            @keyup.enter="handleBulkStatusUpdate" />
                        <button
                            v-if="canUpdate && (bulkStatusTarget && bulkStatusTarget !== '__custom__' || (bulkStatusTarget === '__custom__' && customStatusValue))"
                            @click="handleBulkStatusUpdate" :disabled="isBulkUpdating"
                            class="h-9 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
                            {{ isBulkUpdating ? t('assets.applying') : t('assets.applyStatus') }}
                        </button>
                        <button v-if="canDelete" @click="handleBulkDelete"
                            class="h-9 rounded-lg bg-error-600 px-4 text-sm font-medium text-white hover:bg-error-700">
                            {{ t('assets.deleteSelected') }}
                        </button>
                        <button @click="clearSelection"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                            {{ t('common.clear') }}
                        </button>
                    </div>
                </div>

                <!-- Scrollable Table -->
                <div class="flex-1 overflow-auto min-h-0">
                    <table class="w-full text-sm">
                        <thead
                            class="sticky top-0 z-10 border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900/90 backdrop-blur-sm">
                            <tr>
                                <th class="px-4 py-4 text-left w-10">
                                    <input type="checkbox" :checked="isAllSelected" :indeterminate="isIndeterminate"
                                        @change="toggleSelectAll"
                                        class="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800" />
                                </th>
                                <th v-for="col in tableColumns" :key="col.key"
                                    class="px-4 py-4 text-left font-semibold text-gray-900 dark:text-white whitespace-nowrap cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-800/50 transition"
                                    :class="{ 'max-w-xs': col.key === 'product_name' || col.key === 'spec' }"
                                    @click="toggleSort(col.key)">
                                    <div class="flex items-center gap-1">
                                        {{ col.label }}
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
                            <tr v-for="asset in assets" :key="asset.id"
                                class="hover:bg-gray-50 dark:hover:bg-white/5"
                                :class="{ 'bg-brand-50/50 dark:bg-brand-500/5': selectedIds.includes(asset.id) }">
                                <td class="px-4 py-3">
                                    <input type="checkbox" :checked="selectedIds.includes(asset.id)"
                                        @change="toggleSelect(asset.id)"
                                        class="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800" />
                                </td>
                                <td class="px-4 py-3 text-gray-900 dark:text-white font-medium whitespace-nowrap">
                                    {{ asset.asset_id }}
                                </td>
                                <td class="px-4 py-3 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                    {{ asset.part_number || '-' }}
                                </td>
                                <td class="px-4 py-3 text-gray-700 dark:text-gray-300 max-w-xs truncate"
                                    :title="asset.product_name || ''">
                                    {{ asset.product_name || '-' }}
                                </td>
                                <td class="px-4 py-3 text-gray-700 dark:text-gray-300 max-w-xs truncate"
                                    :title="asset.spec || ''">
                                    {{ asset.spec || '-' }}
                                </td>
                                <td class="px-4 py-3 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                    {{ formatNumber(asset.quantity) }}
                                </td>
                                <td class="px-4 py-3 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                    {{ asset.keeper_name || '-' }}
                                </td>
                                <td class="px-4 py-3 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                    {{ asset.department_code || '-' }}
                                </td>
                                <td class="px-4 py-3">
                                    <span v-if="asset.status" class="rounded-full px-3 py-1 text-xs font-medium"
                                        :class="getStatusClass(asset.status)">
                                        {{ asset.status }}
                                    </span>
                                    <span v-else class="text-gray-400">-</span>
                                </td>
                                <td class="px-4 py-3 text-center">
                                    <div class="flex justify-center gap-2">
                                        <button @click="viewAsset(asset.id)"
                                            class="h-8 rounded-lg border border-gray-300 px-3 text-xs font-medium text-gray-600 transition hover:bg-gray-50 focus:outline-hidden dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800">
                                            {{ t('common.view') }}
                                        </button>
                                        <button v-if="canUpdate" @click="editAsset(asset.id)"
                                            class="h-8 rounded-lg border border-brand-300 px-3 text-xs font-medium text-brand-600 transition hover:bg-brand-50 focus:outline-hidden dark:border-brand-500/30 dark:text-brand-400 dark:hover:bg-brand-500/10">
                                            {{ t('common.edit') }}
                                        </button>
                                        <button v-if="canDelete" @click="deleteAsset(asset.id)"
                                            class="h-8 rounded-lg border border-error-300 px-3 text-xs font-medium text-error-600 transition hover:bg-error-50 focus:outline-hidden dark:border-error-500/30 dark:text-error-400 dark:hover:bg-error-500/10">
                                            {{ t('common.delete') }}
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Sticky Pagination Footer -->
                <div
                    class="flex-none flex flex-col gap-3 border-t border-gray-200 px-6 py-4 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
                    <div class="flex items-center gap-3">
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            {{ t('common.showing') }} {{ pageRangeStart }}-{{ pageRangeEnd }} {{ t('common.of') }} {{ totalCount }}
                        </p>
                        <select v-model.number="pageSize"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                            <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} / {{ t('common.page') }}
                            </option>
                        </select>
                    </div>
                    <div class="flex items-center gap-2">
                        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.prev') }}
                        </button>
                        <div class="flex items-center gap-1.5 text-sm text-gray-700 dark:text-gray-300">
                            <input type="number" :value="currentPage" @change="handlePageInputChange"
                                @keydown.enter="($event.target as HTMLInputElement).blur()" :min="1" :max="totalPages"
                                class="h-9 w-14 rounded-lg border border-gray-300 bg-white px-2 text-center text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" />
                            <span>{{ t('common.of') }} {{ totalPages }}</span>
                        </div>
                        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.next') }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- View/Edit Asset Modal -->
            <div v-if="showDetailModal || showEditModal"
                class="fixed inset-0 z-[100000] flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50" @click="closeModals"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white w-full max-w-4xl max-h-[90vh] flex flex-col dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <!-- Sticky Header -->
                    <div
                        class="sticky top-0 z-10 flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-t-2xl">
                        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                            {{ showEditModal ? t('assets.editAsset') : t('assets.assetDetails') }}
                        </h2>
                        <button @click="closeModals" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                            <XIcon class="w-6 h-6" />
                        </button>
                    </div>

                    <!-- Scrollable Body -->
                    <div class="flex-1 overflow-y-auto px-6 py-4">
                        <!-- Edit Form -->
                        <form v-if="showEditModal" @submit.prevent="saveAsset" class="space-y-4" id="editAssetForm">
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                        {{ t('assets.assetId') }} <span class="text-error-500">*</span>
                                    </label>
                                    <input v-model="editForm.asset_id" type="text" required
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.assetId')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.partNumber') }}</label>
                                    <input v-model="editForm.part_number" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.partNumber')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.productName') }}</label>
                                    <input v-model="editForm.product_name" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.productName')" />
                                </div>
                                <div class="space-y-2 md:col-span-2 lg:col-span-3">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.spec') }}</label>
                                    <textarea v-model="editForm.spec" rows="2"
                                        class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.specifications')"></textarea>
                                </div>
                                <div class="space-y-2">
                                    <label
                                        class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.quantity') }}</label>
                                    <input v-model.number="editForm.quantity" type="number" min="1"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        placeholder="1" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('common.status') }}</label>
                                    <input v-model="editForm.status" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('common.status')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.costCenter') }}</label>
                                    <input v-model="editForm.cost_center" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.costCenter')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.keeperName') }}</label>
                                    <input v-model="editForm.keeper_name" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.keeperName')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.keeperDept') }}</label>
                                    <input v-model="editForm.keeper_dept" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.keeperDept')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.receiveDate') }}</label>
                                    <input ref="receiveDateInput" type="text" v-model="editForm.receive_date"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        placeholder="Select date" />
                                </div>
                                <div class="space-y-2">
                                    <label
                                        class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.storage') }}</label>
                                    <input v-model="editForm.storage" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.storageLocation')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.locationCode') }}</label>
                                    <input v-model="editForm.location_code" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.locationCode')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.serialNumber') }}</label>
                                    <input v-model="editForm.sn" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.serialNumber')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.price') }}</label>
                                    <input v-model.number="editForm.price" type="number" step="0.01"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.price')" />
                                </div>
                                <div class="space-y-2">
                                    <label
                                        class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.currency') }}</label>
                                    <input v-model="editForm.currency" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        placeholder="USD" />
                                </div>
                                <div class="space-y-2 md:col-span-2 lg:col-span-3">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.notes') }}</label>
                                    <textarea v-model="editForm.note1" rows="2"
                                        class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.additionalNotes')"></textarea>
                                </div>
                            </div>
                        </form>

                        <!-- View Mode -->
                        <div v-else-if="selectedAsset" class="space-y-4">
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.assetId') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.asset_id }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.partNumber') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.part_number || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.productName') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.product_name || '-' }}</p>
                                </div>
                                <div class="md:col-span-2 lg:col-span-3">
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.spec') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.spec || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.quantity') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ formatNumber(selectedAsset.quantity) }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('common.status') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.status || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.costCenter') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.cost_center || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.keeper') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.keeper_name || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.keeperDept') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.keeper_dept || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.receiveDate') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ formatDate(selectedAsset.receive_date) }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.storage') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.storage || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.locationCode') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.location_code || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.serialNumber') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.sn || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.price') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.price ? `${selectedAsset.price} ${selectedAsset.currency || ''}`
                                            : '-' }}
                                    </p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.vendor') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.vendor || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.prNo') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.pr_no || '-' }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.poNo') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.po_no || '-' }}</p>
                                </div>
                                <div class="md:col-span-2 lg:col-span-3">
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('assets.notes') }}</p>
                                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ selectedAsset.notes?.note1 || '-' }}</p>
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
                            <button @click="saveAsset" :disabled="isSaving"
                                class="h-11 flex-1 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 disabled:opacity-50">
                                {{ isSaving ? t('common.saving') : t('common.save') }}
                            </button>
                        </template>
                        <template v-else>
                            <button @click="closeModals"
                                class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                {{ t('common.close') }}
                            </button>
                            <button v-if="canUpdate && selectedAsset" @click="editAsset(selectedAsset.id)"
                                class="h-11 flex-1 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700">
                                {{ t('common.edit') }}
                            </button>
                        </template>
                    </div>
                </div>
            </div>

            <!-- Create Asset Modal -->
            <div v-if="showCreateModal && !showEditModal && !showDetailModal"
                class="fixed inset-0 z-[100000] flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50" @click="showCreateModal = false"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white w-full max-w-4xl max-h-[90vh] flex flex-col dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <!-- Sticky Header -->
                    <div
                        class="sticky top-0 z-10 flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-t-2xl">
                        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t('assets.addAsset') }}</h2>
                        <button @click="showCreateModal = false"
                            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                            <XIcon class="w-6 h-6" />
                        </button>
                    </div>

                    <!-- Scrollable Body -->
                    <div class="flex-1 overflow-y-auto px-6 py-4">
                        <form @submit.prevent="createAsset" class="space-y-4" id="createAssetForm">
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                        {{ t('assets.assetId') }} <span class="text-error-500">*</span>
                                    </label>
                                    <input v-model="createForm.asset_id" type="text" required
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.assetId')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.partNumber') }}</label>
                                    <input v-model="createForm.part_number" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.partNumber')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.productName') }}</label>
                                    <input v-model="createForm.product_name" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.productName')" />
                                </div>
                                <div class="space-y-2 md:col-span-2 lg:col-span-3">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.spec') }}</label>
                                    <textarea v-model="createForm.spec" rows="2"
                                        class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.specifications')"></textarea>
                                </div>
                                <div class="space-y-2">
                                    <label
                                        class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.quantity') }}</label>
                                    <input v-model.number="createForm.quantity" type="number" min="1"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        placeholder="1" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.costCenter') }}</label>
                                    <input v-model="createForm.cost_center" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.costCenterDeptCode')" />
                                </div>
                                <div class="space-y-2">
                                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('assets.keeperName') }}</label>
                                    <input v-model="createForm.keeper_name" type="text"
                                        class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                        :placeholder="t('assets.keeperName')" />
                                </div>
                            </div>
                        </form>
                    </div>

                    <!-- Sticky Footer -->
                    <div
                        class="sticky bottom-0 z-10 flex gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-b-2xl">
                        <button type="button" @click="showCreateModal = false"
                            class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.cancel') }}
                        </button>
                        <button @click="createAsset" :disabled="isCreating"
                            class="h-11 flex-1 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 disabled:opacity-50">
                            {{ isCreating ? t('assets.creatingAsset') : t('assets.createAsset') }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Import Modal -->
            <div v-if="showImportModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50" @click="showImportModal = false"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white w-full max-w-md flex flex-col dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <!-- Header -->
                    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t('assets.importAssets') }}</h2>
                    </div>
                    <!-- Body -->
                    <div class="px-6 py-4">
                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                            {{ t('assets.importDescription') }}
                        </p>
                        <div class="space-y-4">
                            <div
                                class="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-6 text-center">
                                <input type="file" ref="importFileInput" @change="handleFileSelect"
                                    accept=".csv,.xlsx,.xls" class="hidden" />
                                <button @click="($refs.importFileInput as HTMLInputElement).click()"
                                    class="text-brand-600 dark:text-brand-400 hover:underline">
                                    {{ t('assets.clickToSelectFile') }}
                                </button>
                                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">{{ t('assets.supportsFormats') }}</p>
                                <p v-if="importFile" class="text-sm text-gray-700 dark:text-gray-300 mt-2">
                                    {{ t('assets.selectedFile') }} {{ importFile.name }}
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
                            {{ isImporting ? t('common.loading') : t('common.import') }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Delete Confirmation Modal -->
            <div v-if="showDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50" @click="showDeleteModal = false"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{{ t('assets.deleteAsset') }}</h2>
                    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ t('assets.deleteAssetMsg') }}</p>
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
            <div v-if="showBulkDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50" @click="showBulkDeleteModal = false"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-700 dark:bg-gray-900 relative z-10">
                    <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{{ t('assets.deleteSelected') }}</h2>
                    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ t('assets.deleteBulkMsg', { count: selectedIds.length }) }}</p>
                    <div class="flex gap-3">
                        <button @click="showBulkDeleteModal = false"
                            class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.cancel') }}
                        </button>
                        <button @click="confirmBulkDelete" :disabled="isDeleting"
                            class="h-11 flex-1 rounded-lg bg-error-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 disabled:opacity-50">
                            {{ isDeleting ? t('common.deleting') : t('assets.deleteAll') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
defineOptions({
	name: 'AssetsView',
})

import * as XLSX from '@e965/xlsx'
import flatpickr from 'flatpickr'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
import { usePagePermission } from '@/composables/usePagePermission'
import { useToast } from '@/composables/useToast'
import { XIcon } from '@/icons'
import { type Asset, type AssetSummary, assetAPI } from '@/services/api/asset'

const { showToast } = useToast()
const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = usePagePermission('assets')

// Format number: strip trailing zeros (1.00 → 1, 1.50 → 1.5)
const formatNumber = (val: number | string | null | undefined): string => {
	if (val == null) return '1'
	const n = typeof val === 'string' ? parseFloat(val) : val
	if (Number.isNaN(n)) return '1'
	return String(parseFloat(n.toFixed(2)))
}

// Table columns
const tableColumns = computed(() => [
	{ key: 'asset_id', label: t('assets.colAssetId') },
	{ key: 'part_number', label: t('assets.colPartNumber') },
	{ key: 'product_name', label: t('assets.colProductName') },
	{ key: 'spec', label: t('assets.colSpec') },
	{ key: 'quantity', label: t('assets.colQty') },
	{ key: 'keeper_name', label: t('assets.colKeeper') },
	{ key: 'department_code', label: t('assets.colDept') },
	{ key: 'status', label: t('assets.colStatus') },
])

// Sorting
const sortField = ref('')
const sortDirection = ref<'asc' | 'desc'>('asc')

// Pagination
const currentPage = ref(1)
const pageSize = ref(25)
const totalCount = ref(0)
const pageSizeOptions = [10, 25, 50, 100]

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))
const pageRangeStart = computed(() =>
	totalCount.value === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1,
)
const pageRangeEnd = computed(() => Math.min(currentPage.value * pageSize.value, totalCount.value))

// State
const isLoading = ref(false)
const assets = ref<AssetSummary[]>([])
const departmentOptions = ref<{ id: number; name: string }[]>([])
const searchQuery = ref('')
const departmentFilter = ref('')
const statusFilter = ref('')

// Selection
const selectedIds = ref<number[]>([])

// Bulk status
const bulkStatusTarget = ref('')
const customStatusValue = ref('')
const isBulkUpdating = ref(false)

// Modals
const showDetailModal = ref(false)
const showEditModal = ref(false)
const showCreateModal = ref(false)
const showImportModal = ref(false)
const showDeleteModal = ref(false)
const showBulkDeleteModal = ref(false)
const showExportMenu = ref(false)
const selectedAsset = ref<Asset | null>(null)
const deleteId = ref<number | null>(null)

// Form
const editForm = ref({
	asset_id: '',
	part_number: '',
	product_name: '',
	spec: '',
	quantity: 1,
	status: '',
	cost_center: '',
	keeper_name: '',
	keeper_dept: '',
	receive_date: '',
	storage: '',
	location_code: '',
	sn: '',
	price: null as number | null,
	currency: '',
	note1: '',
})
const createForm = ref({
	asset_id: '',
	part_number: '',
	product_name: '',
	spec: '',
	quantity: 1,
	cost_center: '',
	keeper_name: '',
})
const isSaving = ref(false)
const isCreating = ref(false)
const isDeleting = ref(false)
const isImporting = ref(false)
const importFile = ref<File | null>(null)
const receiveDateInput = ref<HTMLInputElement | null>(null)
let receiveDatePicker: flatpickr.Instance | null = null

// Selection helpers
const isAllSelected = computed(() => {
	return assets.value.length > 0 && assets.value.every((a) => selectedIds.value.includes(a.id))
})

const isIndeterminate = computed(() => {
	const count = assets.value.filter((a) => selectedIds.value.includes(a.id)).length
	return count > 0 && count < assets.value.length
})

const toggleSelectAll = () => {
	if (isAllSelected.value) {
		const pageIds = new Set(assets.value.map((a) => a.id))
		selectedIds.value = selectedIds.value.filter((id) => !pageIds.has(id))
	} else {
		const newIds = assets.value.map((a) => a.id).filter((id) => !selectedIds.value.includes(id))
		selectedIds.value.push(...newIds)
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
	customStatusValue.value = ''
}

// Status colors
const getStatusClass = (status: string) => {
	const s = status.toLowerCase()
	if (s === 'picking') return 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300'
	if (s === 'broken') return 'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300'
	if (s === 'received') return 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300'
	return 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'
}

// Methods
const formatDate = (date: string | null) => {
	if (!date) return '-'
	return new Date(date).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
	})
}

const toggleSort = (field: string) => {
	if (sortField.value === field) {
		sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
	} else {
		sortField.value = field
		sortDirection.value = 'asc'
	}
	loadData()
}

const loadData = async () => {
	isLoading.value = true
	try {
		const ordering = sortField.value
			? `${sortDirection.value === 'desc' ? '-' : ''}${sortField.value}`
			: undefined

		const response = await assetAPI.list({
			page: currentPage.value,
			page_size: pageSize.value,
			search: searchQuery.value || undefined,
			department: departmentFilter.value ? Number(departmentFilter.value) : undefined,
			status: statusFilter.value || undefined,
			ordering,
		})

		assets.value = response.results
		totalCount.value = response.count
	} catch (error) {
		console.error('Failed to load assets:', error)
		showToast(t('assets.loadFailed'), 'error')
	} finally {
		isLoading.value = false
	}
}

const loadDepartmentOptions = async () => {
	try {
		const groups = await assetAPI.byDepartment()
		departmentOptions.value = groups.map((g) => ({
			id: g.department_id ?? 0,
			name: `${g.department_name} (${g.asset_count})`,
		}))
	} catch {
		// Silently fail - department filter won't be populated but page still works
	}
}

const handleSearch = () => {
	currentPage.value = 1
	clearSelection()
	loadData()
}

const handleReset = () => {
	searchQuery.value = ''
	departmentFilter.value = ''
	statusFilter.value = ''
	sortField.value = ''
	currentPage.value = 1
	clearSelection()
	loadData()
}

const goToPage = (page: number) => {
	if (page < 1 || page > totalPages.value) return
	currentPage.value = page
	loadData()
}

const handlePageInputChange = (event: Event) => {
	const target = event.target as HTMLInputElement
	const page = parseInt(target.value, 10)
	if (!Number.isNaN(page) && page >= 1 && page <= totalPages.value) {
		goToPage(page)
	} else {
		target.value = String(currentPage.value)
	}
}

// Bulk status update
const handleBulkStatusUpdate = async () => {
	const status =
		bulkStatusTarget.value === '__custom__' ? customStatusValue.value : bulkStatusTarget.value
	if (!status || selectedIds.value.length === 0) return

	isBulkUpdating.value = true
	try {
		const result = await assetAPI.bulkUpdateStatus(selectedIds.value, status)
		showToast(result.message, 'success')
		clearSelection()
		loadData()
	} catch (error) {
		console.error('Failed to bulk update status:', error)
		showToast(t('assets.updateStatusFailed'), 'error')
	} finally {
		isBulkUpdating.value = false
	}
}

const handleBulkDelete = () => {
	showBulkDeleteModal.value = true
}

const confirmBulkDelete = async () => {
	isDeleting.value = true
	try {
		const result = await assetAPI.bulkDelete(selectedIds.value)
		showToast(result.message, 'success')
		showBulkDeleteModal.value = false
		clearSelection()
		loadData()
	} catch (error) {
		console.error('Failed to bulk delete:', error)
		showToast(t('assets.deleteBulkFailed'), 'error')
	} finally {
		isDeleting.value = false
	}
}

const viewAsset = async (id: number) => {
	try {
		const asset = await assetAPI.get(id)
		selectedAsset.value = asset
		showDetailModal.value = true
	} catch (error) {
		console.error('Failed to load asset:', error)
		showToast(t('assets.detailLoadFailed'), 'error')
	}
}

const editAsset = async (id: number) => {
	try {
		const asset = await assetAPI.get(id)
		selectedAsset.value = asset
		editForm.value = {
			asset_id: asset.asset_id || '',
			part_number: asset.part_number || '',
			product_name: asset.product_name || '',
			spec: asset.spec || '',
			quantity: asset.quantity || 1,
			status: asset.status || '',
			cost_center: asset.cost_center || '',
			keeper_name: asset.keeper_name || '',
			keeper_dept: asset.keeper_dept || '',
			receive_date: asset.receive_date || '',
			storage: asset.storage || '',
			location_code: asset.location_code || '',
			sn: asset.sn || '',
			price: asset.price || null,
			currency: asset.currency || '',
			note1: asset.notes?.note1 || '',
		}
		showDetailModal.value = false
		showEditModal.value = true

		nextTick(() => {
			initDatePicker()
		})
	} catch (error) {
		console.error('Failed to load asset:', error)
		showToast(t('assets.detailLoadFailed'), 'error')
	}
}

const initDatePicker = () => {
	if (receiveDatePicker) {
		receiveDatePicker.destroy()
	}
	if (receiveDateInput.value) {
		receiveDatePicker = flatpickr(receiveDateInput.value, {
			dateFormat: 'Y-m-d',
			defaultDate: editForm.value.receive_date || undefined,
			onChange: (selectedDates) => {
				if (selectedDates.length > 0 && selectedDates[0]) {
					const dateStr = selectedDates[0].toISOString().split('T')[0]
					editForm.value.receive_date = dateStr ?? ''
				}
			},
		})
	}
}

const saveAsset = async () => {
	if (!selectedAsset.value) return

	isSaving.value = true
	try {
		const { note1, ...rest } = editForm.value
		const payload = { ...rest, notes: { note1: note1 || null } }
		await assetAPI.update(selectedAsset.value.id, payload)
		showToast(t('assets.assetUpdated'), 'success')
		closeModals()
		loadData()
	} catch (error) {
		console.error('Failed to save asset:', error)
		showToast(t('assets.assetSaveFailed'), 'error')
	} finally {
		isSaving.value = false
	}
}

const createAsset = async () => {
	if (!createForm.value.asset_id) {
		showToast(t('assets.assetIdRequired'), 'error')
		return
	}

	isCreating.value = true
	try {
		await assetAPI.create(createForm.value)
		showToast(t('assets.assetCreated'), 'success')
		showCreateModal.value = false
		createForm.value = {
			asset_id: '',
			part_number: '',
			product_name: '',
			spec: '',
			quantity: 1,
			cost_center: '',
			keeper_name: '',
		}
		loadData()
	} catch (error) {
		console.error('Failed to create asset:', error)
		showToast(t('assets.assetCreateFailed'), 'error')
	} finally {
		isCreating.value = false
	}
}

const deleteAsset = (id: number) => {
	deleteId.value = id
	showDeleteModal.value = true
}

const confirmDelete = async () => {
	if (!deleteId.value) return

	isDeleting.value = true
	try {
		await assetAPI.delete(deleteId.value)
		showToast(t('assets.assetDeleted'), 'success')
		showDeleteModal.value = false
		loadData()
	} catch (error) {
		console.error('Failed to delete asset:', error)
		showToast(t('assets.assetDeleteFailed'), 'error')
	} finally {
		isDeleting.value = false
	}
}

const closeModals = () => {
	showDetailModal.value = false
	showEditModal.value = false
	selectedAsset.value = null
	if (receiveDatePicker) {
		receiveDatePicker.destroy()
		receiveDatePicker = null
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
		const result = await assetAPI.importData(importFile.value)
		showToast(result.message, 'success')
		showImportModal.value = false
		importFile.value = null
		loadData()
	} catch (error) {
		console.error('Failed to import data:', error)
		showToast(t('assets.importFailed'), 'error')
	} finally {
		isImporting.value = false
	}
}

const exportData = async (format: 'csv' | 'xlsx') => {
	showExportMenu.value = false

	try {
		// Fetch all data for export (no pagination)
		const allAssets: AssetSummary[] = []
		let page = 1
		let hasMore = true
		while (hasMore) {
			const response = await assetAPI.list({
				page,
				page_size: 500,
				search: searchQuery.value || undefined,
				department: departmentFilter.value ? Number(departmentFilter.value) : undefined,
				status: statusFilter.value || undefined,
			})
			allAssets.push(...response.results)
			hasMore = !!response.next
			page++
		}

		if (allAssets.length === 0) {
			showToast(t('assets.noDataToExport'), 'info')
			return
		}

		const allData = allAssets.map((asset) => ({
			[t('assets.colAssetId')]: asset.asset_id,
			[t('assets.colPartNumber')]: asset.part_number || '',
			[t('assets.colProductName')]: asset.product_name || '',
			[t('assets.colSpec')]: asset.spec || '',
			[t('assets.quantity')]: formatNumber(asset.quantity),
			[t('assets.colStatus')]: asset.status || '',
			[t('assets.costCenter')]: asset.cost_center || '',
			[t('assets.colKeeper')]: asset.keeper_name || '',
			[t('assets.colDept')]: asset.department_code || '',
			[t('assets.receiveDate')]: asset.receive_date || '',
		}))

		const dateStr = new Date().toISOString().split('T')[0]

		if (format === 'csv') {
			const headers = Object.keys(allData[0]!)
			const csvContent = [
				headers.join(','),
				...allData.map((row) =>
					headers
						.map((h) => `"${((row as Record<string, unknown>)[h] ?? '').toString().replace(/"/g, '""')}"`)
						.join(','),
				),
			].join('\n')

			const blob = new Blob(['\uFEFF' + csvContent], {
				type: 'text/csv;charset=utf-8;',
			})
			const link = document.createElement('a')
			link.href = URL.createObjectURL(blob)
			link.download = `assets_${dateStr}.csv`
			link.click()
			URL.revokeObjectURL(link.href)
			showToast(t('assets.csvExported'), 'success')
		} else if (format === 'xlsx') {
			const wb = XLSX.utils.book_new()

			// Group data by status for separate sheets
			const grouped: Record<string, typeof allData> = {}
			for (const row of allData) {
				const status = (row[t('assets.colStatus')] as string) || t('assets.noStatus')
				if (!grouped[status]) grouped[status] = []
				grouped[status]!.push(row)
			}

			// Create a sheet for each status group
			for (const [status, rows] of Object.entries(grouped)) {
				// Sheet name max 31 chars, sanitize
				const sheetName = status.slice(0, 31).replace(/[[\]*?/\\:]/g, '_')
				const ws = XLSX.utils.json_to_sheet(rows!)
				XLSX.utils.book_append_sheet(wb, ws, sheetName)
			}

			XLSX.writeFile(wb, `assets_${dateStr}.xlsx`)
			showToast(t('assets.excelExported'), 'success')
		}
	} catch (error) {
		console.error('Failed to export data:', error)
		showToast(t('assets.exportFailed'), 'error')
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

// Watch pageSize changes
watch(pageSize, () => {
	currentPage.value = 1
	loadData()
})

onMounted(() => {
	loadData()
	loadDepartmentOptions()
	document.addEventListener('click', handleClickOutside)
})
</script>
