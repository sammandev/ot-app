<!-- @vue/component -->
<template>
    <AdminLayout>
        <div class="space-y-6">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.adminDepartments.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.adminDepartments.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.adminDepartments.subtitle') }}</p>
                </div>
                <button v-if="canCreate" @click="showCreateModal = true"
                    class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20">
                    {{ t('admin.dept.addDepartment') }}
                </button>
            </div>

            <!-- Search and Filter -->
            <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
                    <input v-model="searchQuery" type="text" :placeholder="t('admin.dept.searchPlaceholder')"
                        class="dark:bg-dark-900 h-11 flex-1 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300" />
                    <span
                        class="inline-flex h-11 items-center rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 shadow-theme-xs dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                        {{ t('common.search') }}
                    </span>
                </div>
            </div>

            <!-- Loading State -->
            <TableSkeleton v-if="isLoading" :rows="8" :columns="4" />

            <!-- Empty State -->
            <div v-else-if="departments.length === 0"
                class="rounded-2xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-white/[0.03]">
                <p class="text-gray-500 dark:text-gray-400">{{ t('admin.dept.noDepartments') }}</p>
            </div>

            <!-- Departments Table -->
            <div v-else
                class="overflow-x-auto rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
                <table class="w-full text-sm">
                    <thead class="border-b border-gray-200 dark:border-gray-800">
                        <tr>
                            <th @click="toggleSort('code')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('admin.dept.code') }}<span class="text-gray-400">{{ getSortIcon('code') }}</span></th>
                            <th @click="toggleSort('name')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('common.name') }}<span class="text-gray-400">{{ getSortIcon('name') }}</span></th>
                            <th @click="toggleSort('is_enabled')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('common.status') }}<span class="text-gray-400">{{ getSortIcon('is_enabled') }}</span></th>
                            <th class="px-6 py-4 text-center font-semibold text-gray-900 dark:text-white">{{ t('common.actions') }}</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                        <tr v-for="dept in paginatedDepartments" :key="dept.id"
                            class="hover:bg-gray-50 dark:hover:bg-white/5">
                            <td class="px-6 py-4 text-gray-900 dark:text-white">
                                <button @click="viewEmployees(dept)"
                                    class="font-medium text-brand-600 dark:text-brand-400 hover:underline cursor-pointer">
                                    {{ dept.code }}
                                </button>
                            </td>
                            <td class="px-6 py-4 text-gray-700 dark:text-gray-300">
                                <button @click="viewEmployees(dept)"
                                    class="hover:text-brand-600 dark:hover:text-brand-400 hover:underline cursor-pointer">
                                    {{ dept.name }}
                                </button>
                            </td>
                            <td class="px-6 py-4">
                                <button v-if="canUpdate" @click="handleToggleEnabled(dept.id, dept.is_enabled)"
                                    :class="dept.is_enabled ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                                    class="rounded-full px-3 py-1 text-xs font-medium transition hover:opacity-80">
                                    {{ dept.is_enabled ? t('admin.enabled') : t('admin.disabled') }}
                                </button>
                                <span v-else
                                    :class="dept.is_enabled ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                                    class="rounded-full px-3 py-1 text-xs font-medium">
                                    {{ dept.is_enabled ? t('admin.enabled') : t('admin.disabled') }}
                                </span>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <div v-if="canUpdate || canDelete" class="flex justify-center gap-2">
                                    <button v-if="canUpdate" @click="handleEdit(dept)"
                                        class="h-9 rounded-lg border border-brand-300 px-3 text-sm font-medium text-brand-600 transition hover:bg-brand-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-brand-500/30 dark:text-brand-400 dark:hover:bg-brand-500/10">
                                        {{ t('common.edit') }}
                                    </button>
                                    <button v-if="canDelete" @click="handleDelete(dept.id)"
                                        class="h-9 rounded-lg border border-error-300 px-3 text-sm font-medium text-error-600 transition hover:bg-error-50 focus:outline-hidden focus:ring-3 focus:ring-error-500/10 dark:border-error-500/30 dark:text-error-400 dark:hover:bg-error-500/10">
                                        {{ t('common.delete') }}
                                    </button>
                                </div>
                                <span v-else class="text-gray-400 text-sm">—</span>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <div
                    class="flex flex-col gap-3 border-t border-gray-200 px-6 py-4 text-sm text-gray-700 dark:border-gray-800 dark:text-gray-300 sm:flex-row sm:items-center sm:justify-between">
                    <div class="flex items-center gap-3">
                        <p>{{ t('common.showing') }} {{ pageRangeStart }}-{{ pageRangeEnd }} {{ t('common.of') }} {{ sortedDepartments.length }}</p>
                        <select v-model.number="pageSize"
                            class="h-9 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                            <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} {{ t('common.perPage') }}</option>
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
            <div v-if="showCreateModal || showEditModal"
                class="fixed inset-0 z-[100000] flex items-center justify-center"
                role="dialog" aria-modal="true" aria-labelledby="dept-form-modal-title">
                <div class="absolute inset-0 bg-black/50" @click="showCreateModal = false; showEditModal = false"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
                    <h2 id="dept-form-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        {{ editingDept ? t('admin.dept.editDepartment') : t('admin.dept.addDepartmentTitle') }}
                    </h2>
                    <form @submit.prevent="handleSave" class="space-y-4">
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.dept.departmentCode') }}</label>
                            <input v-model="formData.code" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                                :class="errors.code ? 'border-error-300 dark:border-error-700' : ''"
                                :placeholder="t('admin.dept.egCode')" required />
                            <p v-if="errors.code" class="text-xs text-error-500">{{ errors.code }}</p>
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.dept.departmentName') }}</label>
                            <input v-model="formData.name" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                                :class="errors.name ? 'border-error-300 dark:border-error-700' : ''"
                                :placeholder="t('admin.dept.egName')" required />
                            <p v-if="errors.name" class="text-xs text-error-500">{{ errors.name }}</p>
                        </div>
                        <div class="flex items-center gap-2">
                            <input v-model="formData.is_enabled" type="checkbox" id="enabled" class="sr-only" />
                            <div :class="formData.is_enabled ? 'border-brand-500 bg-brand-500' : 'bg-transparent border-gray-300 dark:border-gray-700'"
                                class="mr-2 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] hover:border-brand-500 dark:hover:border-brand-500 cursor-pointer">
                                <span :class="formData.is_enabled ? '' : 'opacity-0'">
                                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path d="M11.6666 3.5L5.24992 9.91667L2.33325 7" stroke="white"
                                            stroke-width="1.94437" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                </span>
                            </div>
                            <label for="enabled"
                                class="text-sm font-medium text-gray-700 dark:text-gray-200 cursor-pointer">
                                {{ t('admin.enabled') }}
                            </label>
                        </div>
                        <div class="flex gap-3 pt-4">
                            <button type="button" @click="showCreateModal = false; showEditModal = false"
                                class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                {{ t('common.cancel') }}
                            </button>
                            <button type="submit" :disabled="isSaving"
                                class="h-11 flex-1 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 disabled:opacity-60 disabled:cursor-not-allowed">
                                {{ isSaving ? t('common.saving') : t('common.save') }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Delete Confirmation Modal -->
            <div v-if="showDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center"
                role="dialog" aria-modal="true" aria-labelledby="dept-delete-modal-title">
                <div class="absolute inset-0 bg-black/50" @click="cancelDelete"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
                    <h2 id="dept-delete-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        {{ t('admin.confirmDelete') }}
                    </h2>
                    <p class="text-gray-700 dark:text-gray-300 mb-6">
                        {{ t('admin.dept.deleteMsg') }}
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

            <!-- Employees Modal -->
            <div v-if="showEmployeesModal" class="fixed inset-0 z-[100000] flex items-center justify-center"
                role="dialog" aria-modal="true" aria-labelledby="dept-employees-modal-title">
                <div class="absolute inset-0 bg-black/50" @click="closeEmployeesModal"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white w-full max-w-2xl max-h-[80vh] flex flex-col dark:border-gray-800 dark:bg-gray-900 relative z-10">
                    <!-- Sticky Header -->
                    <div class="sticky top-0 z-10 flex items-center justify-between px-6 pt-5 pb-4 bg-white dark:bg-gray-900 rounded-t-2xl border-b border-gray-200 dark:border-gray-800">
                        <div>
                            <h2 id="dept-employees-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white">
                                {{ t('admin.dept.departmentEmployees') }}
                            </h2>
                            <p class="text-sm text-gray-500 dark:text-gray-400">
                                {{ selectedDepartment?.code }} - {{ selectedDepartment?.name }}
                            </p>
                        </div>
                        <button @click="closeEmployeesModal"
                            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition">
                            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <!-- Scrollable Body -->
                    <div class="flex-1 overflow-y-auto px-6 py-4">
                    <!-- Loading -->
                    <div v-if="loadingEmployees" class="flex items-center justify-center py-8">
                        <div class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent">
                        </div>
                    </div>

                    <!-- Empty State -->
                    <div v-else-if="departmentEmployees.length === 0"
                        class="text-center py-8 text-gray-500 dark:text-gray-400">
                        {{ t('admin.dept.noEmployeesAssigned') }}
                    </div>

                    <!-- Employees List -->
                    <div v-else>
                        <table class="w-full text-sm">
                            <thead class="bg-gray-50 dark:bg-gray-800 sticky top-0">
                                <tr>
                                    <th class="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">{{ t('admin.dept.employeeId') }}</th>
                                    <th class="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">{{ t('common.name') }}</th>
                                    <th class="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">{{ t('common.status') }}
                                    </th>
                                    <th v-if="isPtbAdmin"
                                        class="px-4 py-3 text-center font-semibold text-gray-900 dark:text-white">
                                        {{ t('common.actions') }}</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                                <tr v-for="emp in departmentEmployees" :key="emp.id"
                                    class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                    <td class="px-4 py-3 text-gray-900 dark:text-white font-medium">{{ emp.emp_id }}
                                    </td>
                                    <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ emp.name }}</td>
                                    <td class="px-4 py-3">
                                        <span
                                            :class="emp.is_enabled ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                                            class="rounded-full px-2 py-0.5 text-xs font-medium">
                                            {{ emp.is_enabled ? t('admin.active') : t('admin.inactive') }}
                                        </span>
                                    </td>
                                    <td v-if="isPtbAdmin" class="px-4 py-3 text-center">
                                        <button @click="confirmRemoveEmployee(emp)"
                                            class="text-xs px-2 py-1 rounded border border-error-300 text-error-600 hover:bg-error-50 dark:border-error-500/30 dark:text-error-400 dark:hover:bg-error-500/10 transition">
                                            {{ t('admin.dept.removeEmployee') }}
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    </div>

                    <!-- Sticky Footer -->
                    <div
                        class="sticky bottom-0 z-10 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-b-2xl text-sm text-gray-500 dark:text-gray-400">
                        {{ t('admin.dept.totalEmployees', { count: departmentEmployees.length }) }}
                    </div>
                </div>
            </div>

            <!-- Remove Employee Confirmation -->
            <div v-if="showRemoveConfirmModal" class="fixed inset-0 z-[100001] flex items-center justify-center"
                role="dialog" aria-modal="true" aria-labelledby="dept-remove-emp-modal-title">
                <div class="absolute inset-0 bg-black/50" @click="cancelRemoveEmployee"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
                    <h2 id="dept-remove-emp-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        {{ t('admin.dept.removeEmployeeTitle') }}
                    </h2>
                    <p class="text-gray-700 dark:text-gray-300 mb-6">
                        {{ t('admin.dept.removeEmployeeMsg', { employee: employeeToRemove?.name, department: selectedDepartment?.code }) }}
                    </p>
                    <div class="flex gap-3">
                        <button @click="cancelRemoveEmployee" type="button"
                            class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.cancel') }}
                        </button>
                        <button @click="executeRemoveEmployee" :disabled="isRemoving"
                            class="h-11 flex-1 rounded-lg bg-error-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 focus:outline-hidden focus:ring-3 focus:ring-error-500/20 disabled:opacity-60 disabled:cursor-not-allowed">
                            {{ isRemoving ? t('admin.dept.removing') : t('admin.dept.removeEmployee') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
import { useToast } from '@/composables/useToast'
import { departmentAPI } from '@/services/api/department'
import { useAuthStore } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import type { Department } from '@/types/admin'

const { t } = useI18n()
const { showToast } = useToast()

interface DepartmentEmployee {
	id: number
	emp_id: string
	name: string
	is_enabled: boolean
}

// Auth Store for permission checks
const authStore = useAuthStore()
const canCreate = computed(() => authStore.hasPermission('departments', 'create'))
const canUpdate = computed(() => authStore.hasPermission('departments', 'update'))
const canDelete = computed(() => authStore.hasPermission('departments', 'delete'))
const isPtbAdmin = computed(() => authStore.isPtbAdmin || authStore.isSuperAdmin)

// Pinia Store
const departmentStore = useDepartmentStore()

// Computed data from store
const departments = computed(() => departmentStore.departments)
const isLoading = computed(() => departmentStore.loading)
const isSaving = ref(false)
const searchQuery = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editingDept = ref<Department | null>(null)
const deletingDeptId = ref<number | null>(null)

// Employee modal state
const showEmployeesModal = ref(false)
const selectedDepartment = ref<Department | null>(null)
const departmentEmployees = ref<DepartmentEmployee[]>([])
const loadingEmployees = ref(false)
const showRemoveConfirmModal = ref(false)
const employeeToRemove = ref<DepartmentEmployee | null>(null)
const isRemoving = ref(false)

const formData = reactive({
	code: '',
	name: '',
	is_enabled: true,
})

const errors = reactive({
	code: '',
	name: '',
})

import { getSortIcon as _getSortIcon } from '@/utils/getSortIcon'

const sortBy = ref<'code' | 'name' | 'is_enabled' | null>(null)
const sortOrder = ref<'asc' | 'desc'>('asc')
const pageSizeOptions = [5, 10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)

const resetForm = () => {
	formData.code = ''
	formData.name = ''
	formData.is_enabled = true
	errors.code = ''
	errors.name = ''
	editingDept.value = null
}

const filteredDepartments = computed(() => {
	if (!searchQuery.value.trim()) return departments.value
	const query = searchQuery.value.toLowerCase()
	return departments.value.filter(
		(dept) => dept.code.toLowerCase().includes(query) || dept.name.toLowerCase().includes(query),
	)
})

const sortedDepartments = computed(() => {
	// If no sort applied, return filtered data as-is
	if (!sortBy.value) return filteredDepartments.value

	const sorted = [...filteredDepartments.value].sort((a, b) => {
		let aVal: string | boolean = a[sortBy.value!]
		let bVal: string | boolean = b[sortBy.value!]

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
	Math.max(1, Math.ceil(sortedDepartments.value.length / pageSize.value)),
)
const paginatedDepartments = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value
	const end = start + pageSize.value
	return sortedDepartments.value.slice(start, end)
})
const pageRangeStart = computed(() =>
	sortedDepartments.value.length === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1,
)
const pageRangeEnd = computed(() =>
	Math.min(sortedDepartments.value.length, currentPage.value * pageSize.value),
)

const toggleSort = (field: 'code' | 'name' | 'is_enabled') => {
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

const getSortIcon = (field: 'code' | 'name' | 'is_enabled') =>
	_getSortIcon(field, sortBy, sortOrder)

const goToPage = (page: number) => {
	if (page < 1 || page > totalPages.value) return
	currentPage.value = page
}

watch([pageSize, () => sortedDepartments.value.length], () => {
	currentPage.value = 1
})

const handleEdit = (dept: Department) => {
	editingDept.value = dept
	formData.code = dept.code
	formData.name = dept.name
	formData.is_enabled = dept.is_enabled
	showEditModal.value = true
}

const handleDelete = (id: number) => {
	deletingDeptId.value = id
	showDeleteModal.value = true
}

const confirmDelete = async () => {
	if (deletingDeptId.value !== null) {
		try {
			await departmentStore.deleteDepartment(deletingDeptId.value)
			showDeleteModal.value = false
			deletingDeptId.value = null
		} catch (error) {
			console.error('Failed to delete department:', error)
			showToast(t('admin.dept.deleteFailed', 'Failed to delete department'), 'error')
		}
	}
}

const cancelDelete = () => {
	showDeleteModal.value = false
	deletingDeptId.value = null
}

const handleToggleEnabled = async (id: number, currentStatus: boolean) => {
	try {
		await departmentStore.updateDepartment(id, { is_enabled: !currentStatus })
	} catch (error) {
		console.error('Failed to toggle status:', error)
		showToast(t('admin.dept.toggleFailed', 'Failed to toggle status'), 'error')
	}
}

const handleSave = async () => {
	errors.code = ''
	errors.name = ''

	if (!formData.code.trim()) {
		errors.code = t('admin.dept.codeRequired')
		return
	}
	if (!formData.name.trim()) {
		errors.name = t('admin.dept.nameRequired')
		return
	}

	isSaving.value = true
	try {
		const payload = {
			code: formData.code,
			name: formData.name,
			is_enabled: formData.is_enabled,
		}

		if (editingDept.value) {
			await departmentStore.updateDepartment(editingDept.value.id, payload)
		} else {
			await departmentStore.createDepartment(payload)
		}
		showCreateModal.value = false
		showEditModal.value = false
		resetForm()
	} catch (error) {
		console.error('Failed to save department:', error)
		if (typeof error === 'object' && error !== null && 'response' in error) {
			const err = error as {
				response?: {
					data?: { code?: string | string[]; name?: string | string[] }
				}
			}
			if (err.response?.data?.code) {
				errors.code = Array.isArray(err.response.data.code)
					? err.response.data.code[0] || ''
					: err.response.data.code || ''
			}
			if (err.response?.data?.name) {
				errors.name = Array.isArray(err.response.data.name)
					? err.response.data.name[0] || ''
					: err.response.data.name || ''
			}
		}
	} finally {
		isSaving.value = false
	}
}

// Employee modal functions
const viewEmployees = async (dept: Department) => {
	selectedDepartment.value = dept
	showEmployeesModal.value = true
	loadingEmployees.value = true

	try {
		const response = await departmentAPI.getEmployees(dept.id)
		departmentEmployees.value = response.data
	} catch (error) {
		console.error('Failed to fetch employees:', error)
		departmentEmployees.value = []
	} finally {
		loadingEmployees.value = false
	}
}

const closeEmployeesModal = () => {
	showEmployeesModal.value = false
	selectedDepartment.value = null
	departmentEmployees.value = []
}

const confirmRemoveEmployee = (emp: DepartmentEmployee) => {
	employeeToRemove.value = emp
	showRemoveConfirmModal.value = true
}

const cancelRemoveEmployee = () => {
	showRemoveConfirmModal.value = false
	employeeToRemove.value = null
}

const executeRemoveEmployee = async () => {
	if (!selectedDepartment.value || !employeeToRemove.value) return

	isRemoving.value = true
	try {
		await departmentAPI.removeEmployee(selectedDepartment.value.id, employeeToRemove.value.id)
		// Remove from local list
		departmentEmployees.value = departmentEmployees.value.filter(
			(e) => e.id !== employeeToRemove.value?.id,
		)
		showRemoveConfirmModal.value = false
		employeeToRemove.value = null
	} catch (error) {
		console.error('Failed to remove employee:', error)
		showToast(t('admin.dept.removeEmployeeFailed'), 'error')
	} finally {
		isRemoving.value = false
	}
}

// Handle Esc key to close modals
const handleEscKey = (event: KeyboardEvent) => {
	if (event.key === 'Escape') {
		if (showRemoveConfirmModal.value) {
			cancelRemoveEmployee()
		} else if (showEmployeesModal.value) {
			closeEmployeesModal()
		} else if (showDeleteModal.value) {
			cancelDelete()
		} else if (showCreateModal.value || showEditModal.value) {
			showCreateModal.value = false
			showEditModal.value = false
		}
	}
}

// Load initial data from API
onMounted(async () => {
	await departmentStore.fetchDepartments()
	window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', handleEscKey)
})
</script>