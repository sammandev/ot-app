<!-- @vue/component -->
<template>
    <AdminLayout>
        <div class="space-y-6">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.adminEmployees.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.adminEmployees.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.adminEmployees.subtitle') }}</p>
                </div>
                <button v-if="canCreate" @click="showCreateModal = true"
                    class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20">
                    {{ t('admin.emp.addEmployee') }}
                </button>
            </div>

            <!-- Search and Filter -->
            <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
                    <input v-model="searchQuery" type="text" :placeholder="t('admin.emp.searchPlaceholder')"
                        class="dark:bg-dark-900 h-11 flex-1 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300" />
                    <span
                        class="inline-flex h-11 items-center rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 shadow-theme-xs dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                        {{ t('common.search') }}
                    </span>
                </div>
            </div>

            <!-- Loading State -->
            <TableSkeleton v-if="isLoading" :rows="10" :columns="6" />

            <!-- Empty State -->
            <div v-else-if="employees.length === 0"
                class="rounded-2xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-white/[0.03]">
                <p class="text-gray-500 dark:text-gray-400">{{ t('admin.emp.noEmployees') }}</p>
            </div>

            <!-- Employees Table -->
            <div v-else
                class="overflow-x-auto rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
                <table class="w-full text-sm">
                    <thead class="border-b border-gray-200 dark:border-gray-800">
                        <tr>
                            <th @click="toggleSort('name')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('common.name') }}<span class="text-gray-400">{{ getSortIcon('name') }}</span></th>
                            <th @click="toggleSort('emp_id')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('admin.emp.employeeId') }}<span class="text-gray-400">{{ getSortIcon('emp_id') }}</span></th>
                            <th @click="toggleSort('department')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('admin.emp.department') }}<span class="text-gray-400">{{ getSortIcon('department') }}</span></th>
                            <th @click="toggleSort('is_enabled')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('common.status') }}<span class="text-gray-400">{{ getSortIcon('is_enabled') }}</span></th>
                            <th class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white">{{ t('admin.emp.otReports') }}</th>
                            <th class="px-6 py-4 text-center font-semibold text-gray-900 dark:text-white">{{ t('common.actions') }}</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                        <tr v-for="emp in paginatedEmployees" :key="emp.id"
                            class="hover:bg-gray-50 dark:hover:bg-white/5">
                            <td class="px-6 py-4 text-gray-900 dark:text-white">
                                <span class="font-medium">{{ emp.name }}</span>
                            </td>
                            <td class="px-6 py-4 text-gray-700 dark:text-gray-300">{{ emp.emp_id }}</td>
                            <td class="px-6 py-4 text-gray-700 dark:text-gray-300">
                                {{ departmentMap.get(emp.department)?.name || '—' }}
                            </td>
                            <td class="px-6 py-4">
                                <button v-if="canUpdate" @click="handleToggleEnabled(emp.id, emp.is_enabled)"
                                    :class="emp.is_enabled ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                                    class="rounded-full px-3 py-1 text-xs font-medium transition hover:opacity-80">
                                    {{ emp.is_enabled ? t('admin.enabled') : t('admin.disabled') }}
                                </button>
                                <span v-else
                                    :class="emp.is_enabled ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                                    class="rounded-full px-3 py-1 text-xs font-medium">
                                    {{ emp.is_enabled ? t('admin.enabled') : t('admin.disabled') }}
                                </span>
                            </td>
                            <td class="px-6 py-4">
                                <button v-if="canUpdate" @click="handleToggleReportExclusion(emp.id, !!emp.exclude_from_reports)"
                                    :class="emp.exclude_from_reports ? 'bg-orange-100 text-orange-800 dark:bg-orange-500/20 dark:text-orange-200' : 'bg-blue-100 text-blue-800 dark:bg-blue-500/20 dark:text-blue-200'"
                                    class="rounded-full px-3 py-1 text-xs font-medium transition hover:opacity-80">
                                    {{ emp.exclude_from_reports ? t('admin.emp.excludedFromOT') : t('admin.emp.includedInOT')
                                    }}
                                </button>
                                <span v-else
                                    :class="emp.exclude_from_reports ? 'bg-orange-100 text-orange-800 dark:bg-orange-500/20 dark:text-orange-200' : 'bg-blue-100 text-blue-800 dark:bg-blue-500/20 dark:text-blue-200'"
                                    class="rounded-full px-3 py-1 text-xs font-medium">
                                    {{ emp.exclude_from_reports ? t('admin.emp.excludedFromOT') : t('admin.emp.includedInOT')
                                    }}
                                </span>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <div class="flex justify-center gap-2">
                                    <button v-if="canUpdate" @click="handleEdit(emp)"
                                        class="h-9 rounded-lg border border-brand-300 px-3 text-sm font-medium text-brand-600 transition hover:bg-brand-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-brand-500/30 dark:text-brand-400 dark:hover:bg-brand-500/10">
                                        {{ t('common.edit') }}
                                    </button>
                                    <button v-if="canDelete" @click="handleDelete(emp.id)"
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
                        <p>{{ t('common.showing') }} {{ pageRangeStart }}-{{ pageRangeEnd }} {{ t('common.of') }} {{ sortedEmployees.length }}</p>
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
                class="fixed inset-0 z-[100000] flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50" @click="showCreateModal = false; showEditModal = false"></div>
                <div
                    role="dialog" aria-modal="true" aria-labelledby="employee-modal-title"
                    class="rounded-2xl border border-gray-200 bg-white w-full max-w-md max-h-[90vh] flex flex-col dark:border-gray-800 dark:bg-gray-900 relative z-10">
                    <!-- Sticky Header -->
                    <div class="sticky top-0 z-10 px-6 pt-5 pb-4 bg-white dark:bg-gray-900 rounded-t-2xl border-b border-gray-200 dark:border-gray-800">
                        <h2 id="employee-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white">
                            {{ editingEmp ? t('admin.emp.editEmployee') : t('admin.emp.addEmployeeTitle') }}
                        </h2>
                    </div>
                    <!-- Scrollable Body -->
                    <div class="flex-1 overflow-y-auto px-6 py-4">
                    <form @submit.prevent="handleSave" id="employeeForm" class="space-y-4">
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('common.name') }}</label>
                            <input v-model="formData.name" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                                :class="errors.name ? 'border-error-300 dark:border-error-700' : ''"
                                :placeholder="t('admin.emp.egName')" required />
                            <p v-if="errors.name" class="text-xs text-error-500">{{ errors.name }}</p>
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.emp.employeeId') }}</label>
                            <input v-model="formData.emp_id" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                                :class="errors.emp_id ? 'border-error-300 dark:border-error-700' : ''"
                                :placeholder="t('admin.emp.egId')" required />
                            <p v-if="errors.emp_id" class="text-xs text-error-500">{{ errors.emp_id }}</p>
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.emp.departmentOptional') }}</label>
                            <div class="relative">
                                <select v-model="formData.department_id"
                                    class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 pr-11 text-sm shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300">
                                    <option :value="null">{{ t('admin.emp.selectDepartment') }}</option>
                                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                        {{ dept.name }}
                                    </option>
                                </select>
                                <span
                                    class="absolute z-30 text-gray-500 -translate-y-1/2 pointer-events-none right-4 top-1/2 dark:text-gray-400">
                                    <svg class="stroke-current" width="20" height="20" viewBox="0 0 20 20" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path d="M4.79175 7.396L10.0001 12.6043L15.2084 7.396" stroke=""
                                            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                </span>
                            </div>
                        </div>
                        <div class="space-y-3">
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
                            <div class="flex items-start gap-2">
                                <input v-model="formData.exclude_from_reports" type="checkbox" id="exclude-reports"
                                    class="sr-only" />
                                <div :class="formData.exclude_from_reports ? 'border-orange-500 bg-orange-500' : 'bg-transparent border-gray-300 dark:border-gray-700'"
                                    class="mt-0.5 mr-2 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] hover:border-orange-500 dark:hover:border-orange-500 cursor-pointer">
                                    <span :class="formData.exclude_from_reports ? '' : 'opacity-0'">
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none"
                                            xmlns="http://www.w3.org/2000/svg">
                                            <path d="M11.6666 3.5L5.24992 9.91667L2.33325 7" stroke="white"
                                                stroke-width="1.94437" stroke-linecap="round" stroke-linejoin="round" />
                                        </svg>
                                    </span>
                                </div>
                                <div>
                                    <label for="exclude-reports"
                                        class="text-sm font-medium text-gray-700 dark:text-gray-200 cursor-pointer">
                                        {{ t('admin.emp.excludeFromOTReports') }}
                                    </label>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('admin.emp.excludeDescription') }}</p>
                                </div>
                            </div>
                        </div>
                    </form>
                    </div>
                    <!-- Sticky Footer -->
                    <div class="sticky bottom-0 z-10 flex gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 rounded-b-2xl">
                            <button type="button" @click="showCreateModal = false; showEditModal = false"
                                class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                                {{ t('common.cancel') }}
                            </button>
                            <button type="submit" form="employeeForm" :disabled="isSaving"
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
                    role="dialog" aria-modal="true" aria-labelledby="employee-delete-modal-title"
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
                    <h2 id="employee-delete-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        {{ t('admin.confirmDelete') }}
                    </h2>
                    <p class="text-gray-700 dark:text-gray-300 mb-6">
                        {{ t('admin.emp.deleteMsg') }}
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
        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
import { usePagePermission } from '@/composables/usePagePermission'
import type { Employee } from '@/services/api'
import { useDepartmentStore } from '@/stores/department'
import { useEmployeeStore } from '@/stores/employee'

// Pinia Stores
const { t } = useI18n()
const employeeStore = useEmployeeStore()
const departmentStore = useDepartmentStore()
const { canCreate, canUpdate, canDelete } = usePagePermission('admin_employees')

// Computed data from stores
const employees = computed(() => employeeStore.employees)
const departments = computed(() => departmentStore.departments)
const isLoading = computed(() => employeeStore.loading || departmentStore.loading)
const isSaving = ref(false)
const searchQuery = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editingEmp = ref<Employee | null>(null)
const deletingEmpId = ref<number | null>(null)

const formData = reactive({
	name: '',
	emp_id: '',
	department_id: null as number | null,
	is_enabled: true,
	exclude_from_reports: false,
})

const errors = reactive({
	name: '',
	emp_id: '',
})

import { getSortIcon as _getSortIcon } from '@/utils/getSortIcon'

const sortBy = ref<'name' | 'emp_id' | 'department' | 'is_enabled' | null>(null)
const sortOrder = ref<'asc' | 'desc'>('asc')

// O(1) department lookup map instead of .find() inside v-for
const departmentMap = computed(() => new Map(departments.value.map((d) => [d.id, d])))
const pageSizeOptions = [5, 10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)

const resetForm = () => {
	formData.name = ''
	formData.emp_id = ''
	formData.department_id = null
	formData.is_enabled = true
	formData.exclude_from_reports = false
	errors.name = ''
	errors.emp_id = ''
	editingEmp.value = null
}

const filteredEmployees = computed(() => {
	if (!searchQuery.value.trim()) return employees.value
	const query = searchQuery.value.toLowerCase()
	return employees.value.filter(
		(emp) => emp.name.toLowerCase().includes(query) || emp.emp_id.toLowerCase().includes(query),
	)
})

const sortedEmployees = computed(() => {
	// If no sort applied, return filtered data as-is
	if (!sortBy.value) return filteredEmployees.value

	const sorted = [...filteredEmployees.value].sort((a, b) => {
		let aVal: string | boolean | number = a[sortBy.value!]
		let bVal: string | boolean | number = b[sortBy.value!]

		if (sortBy.value === 'department') {
			const deptA = departments.value.find((d) => d.id === a.department)
			const deptB = departments.value.find((d) => d.id === b.department)
			aVal = deptA?.name || ''
			bVal = deptB?.name || ''
		}

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
	Math.max(1, Math.ceil(sortedEmployees.value.length / pageSize.value)),
)
const paginatedEmployees = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value
	const end = start + pageSize.value
	return sortedEmployees.value.slice(start, end)
})
const pageRangeStart = computed(() =>
	sortedEmployees.value.length === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1,
)
const pageRangeEnd = computed(() =>
	Math.min(sortedEmployees.value.length, currentPage.value * pageSize.value),
)

const toggleSort = (field: 'name' | 'emp_id' | 'department' | 'is_enabled') => {
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

const getSortIcon = (field: 'name' | 'emp_id' | 'department' | 'is_enabled') =>
	_getSortIcon(field, sortBy, sortOrder)

const goToPage = (page: number) => {
	if (page < 1 || page > totalPages.value) return
	currentPage.value = page
}

watch([pageSize, () => sortedEmployees.value.length], () => {
	currentPage.value = 1
})

const handleEdit = (emp: Employee) => {
	editingEmp.value = emp
	formData.name = emp.name
	formData.emp_id = emp.emp_id
	formData.department_id = emp.department || null
	formData.is_enabled = emp.is_enabled
	formData.exclude_from_reports = Boolean(emp.exclude_from_reports)
	showEditModal.value = true
}

const handleDelete = (id: number) => {
	deletingEmpId.value = id
	showDeleteModal.value = true
}

const confirmDelete = async () => {
	if (deletingEmpId.value !== null) {
		try {
			await employeeStore.deleteEmployee(deletingEmpId.value)
			showDeleteModal.value = false
			deletingEmpId.value = null
		} catch (error) {
			console.error('Failed to delete employee:', error)
		}
	}
}

const cancelDelete = () => {
	showDeleteModal.value = false
	deletingEmpId.value = null
}

// Handle Esc key to close modals
const handleEscKey = (event: KeyboardEvent) => {
	if (event.key === 'Escape') {
		if (showDeleteModal.value) {
			cancelDelete()
		} else if (showCreateModal.value || showEditModal.value) {
			showCreateModal.value = false
			showEditModal.value = false
		}
	}
}

const handleToggleEnabled = async (id: number, currentStatus: boolean) => {
	try {
		await employeeStore.updateEmployee(id, { is_enabled: !currentStatus })
	} catch (error) {
		console.error('Failed to toggle status:', error)
	}
}

const handleToggleReportExclusion = async (id: number, currentStatus: boolean) => {
	try {
		await employeeStore.updateEmployee(id, {
			exclude_from_reports: !currentStatus,
		})
	} catch (error) {
		console.error('Failed to toggle report exclusion:', error)
	}
}

const handleSave = async () => {
	errors.name = ''
	errors.emp_id = ''

	if (!formData.name.trim()) {
		errors.name = t('admin.emp.nameRequired')
		return
	}
	if (!formData.emp_id.trim()) {
		errors.emp_id = t('admin.emp.idRequired')
		return
	}

	isSaving.value = true
	try {
		const payload = {
			name: formData.name,
			emp_id: formData.emp_id,
			department: formData.department_id,
			is_enabled: formData.is_enabled,
			exclude_from_reports: formData.exclude_from_reports,
		}

		if (editingEmp.value) {
			// Update existing employee
			await employeeStore.updateEmployee(editingEmp.value.id, payload)
		} else {
			// Create new employee
			await employeeStore.createEmployee(payload)
		}
		showCreateModal.value = false
		showEditModal.value = false
		resetForm()
	} catch (error) {
		console.error('Failed to save employee:', error)
		// Show error message
		if (typeof error === 'object' && error !== null && 'response' in error) {
			const err = error as {
				response?: {
					data?: { emp_id?: string | string[]; name?: string | string[] }
				}
			}
			if (err.response?.data?.emp_id) {
				const empIdError = Array.isArray(err.response.data.emp_id)
					? err.response.data.emp_id[0]
					: err.response.data.emp_id
				errors.emp_id = empIdError ?? ''
			}
			if (err.response?.data?.name) {
				const nameError = Array.isArray(err.response.data.name)
					? err.response.data.name[0]
					: err.response.data.name
				errors.name = nameError ?? ''
			}
		}
	} finally {
		isSaving.value = false
	}
}

// Load initial data from API
onMounted(async () => {
	await Promise.all([employeeStore.fetchEmployees(), departmentStore.fetchDepartments()])
	window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', handleEscKey)
})
</script>