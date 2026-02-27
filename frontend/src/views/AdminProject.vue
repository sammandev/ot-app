<!-- @vue/component -->
<template>
    <AdminLayout>
        <div class="space-y-6">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.adminProjects.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.adminProjects.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.adminProjects.subtitle') }}</p>
                </div>
                <button v-if="canCreate" @click="handleCreate"
                    class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20">
                    {{ t('admin.proj.addProject') }}
                </button>
            </div>

            <!-- Search and Filter -->
            <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
                    <input v-model="searchQuery" type="text" :placeholder="t('admin.proj.searchPlaceholder')"
                        class="dark:bg-dark-900 h-11 flex-1 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300" />
                    <span
                        class="inline-flex h-11 items-center rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 shadow-theme-xs dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                        {{ t('common.search') }}
                    </span>
                </div>
            </div>

            <!-- Loading State -->
            <TableSkeleton v-if="isLoading" :rows="8" :columns="3" />

            <!-- Empty State -->
            <div v-else-if="projects.length === 0"
                class="rounded-2xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-white/[0.03]">
                <p class="text-gray-500 dark:text-gray-400">{{ t('admin.proj.noProjects') }}</p>
            </div>

            <!-- Projects Table -->
            <div v-else
                class="overflow-x-auto rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
                <table class="w-full text-sm">
                    <thead class="border-b border-gray-200 dark:border-gray-800">
                        <tr>
                            <th @click="toggleSort('name')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('admin.proj.projectName') }}<span class="text-gray-400">{{ getSortIcon('name') }}</span></th>
                            <th @click="toggleSort('is_enabled')"
                                class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                {{ t('common.status') }}<span class="text-gray-400">{{ getSortIcon('is_enabled') }}</span></th>
                            <th class="px-6 py-4 text-center font-semibold text-gray-900 dark:text-white">{{ t('common.actions') }}</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                        <tr v-for="proj in paginatedProjects" :key="proj.id"
                            class="hover:bg-gray-50 dark:hover:bg-white/5">
                            <td class="px-6 py-4 text-gray-900 dark:text-white">
                                <span class="font-medium">{{ proj.name }}</span>
                            </td>
                            <td class="px-6 py-4">
                                <button v-if="canUpdate" @click="handleToggleEnabled(proj.id, proj.is_enabled)"
                                    :class="proj.is_enabled ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                                    class="rounded-full px-3 py-1 text-xs font-medium transition hover:opacity-80">
                                    {{ proj.is_enabled ? t('admin.enabled') : t('admin.disabled') }}
                                </button>
                                <span v-else
                                    :class="proj.is_enabled ? 'bg-green-100 text-green-800 dark:bg-green-500/20 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-500/20 dark:text-gray-300'"
                                    class="rounded-full px-3 py-1 text-xs font-medium">
                                    {{ proj.is_enabled ? t('admin.enabled') : t('admin.disabled') }}
                                </span>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <div v-if="canUpdate || canDelete" class="flex justify-center gap-2">
                                    <button v-if="canUpdate" @click="handleEdit(proj)"
                                        class="h-9 rounded-lg border border-brand-300 px-3 text-sm font-medium text-brand-600 transition hover:bg-brand-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-brand-500/30 dark:text-brand-400 dark:hover:bg-brand-500/10">
                                        {{ t('common.edit') }}
                                    </button>
                                    <button v-if="canDelete" @click="handleDelete(proj.id)"
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
                        <p>{{ t('common.showing') }} {{ pageRangeStart }}-{{ pageRangeEnd }} {{ t('common.of') }} {{ sortedProjects.length }}</p>
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
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
                    <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        {{ editingProj ? t('admin.proj.editProject') : t('admin.proj.addProjectTitle') }}
                    </h2>
                    <form @submit.prevent="handleSave" class="space-y-4">
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('admin.proj.projectName') }}</label>
                            <input v-model="formData.name" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-300"
                                :class="errors.name ? 'border-error-300 dark:border-error-700' : ''"
                                :placeholder="t('admin.proj.egName')" required />
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
            <div v-if="showDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50" @click="cancelDelete"></div>
                <div
                    class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
                    <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        {{ t('admin.confirmDelete') }}
                    </h2>
                    <p class="text-gray-700 dark:text-gray-300 mb-6">
                        {{ t('admin.proj.deleteMsg') }}
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
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'
import type { Project } from '@/types/admin'

const { t } = useI18n()
const { showToast } = useToast()

// Auth Store for permission checks
const authStore = useAuthStore()
const canCreate = computed(() => authStore.hasPermission('projects', 'create'))
const canUpdate = computed(() => authStore.hasPermission('projects', 'update'))
const canDelete = computed(() => authStore.hasPermission('projects', 'delete'))

// Pinia Store
const projectStore = useProjectStore()

// Computed data from store
const projects = computed(() => projectStore.projects)
const isLoading = computed(() => projectStore.loading)
const isSaving = ref(false)
const searchQuery = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editingProj = ref<Project | null>(null)
const deletingProjId = ref<number | null>(null)

const formData = reactive({
	name: '',
	is_enabled: true,
})

const errors = reactive({
	name: '',
})

import { getSortIcon as _getSortIcon } from '@/utils/getSortIcon'

const sortBy = ref<'name' | 'is_enabled' | null>(null)
const sortOrder = ref<'asc' | 'desc'>('asc')
const pageSizeOptions = [5, 10, 20, 50]
const pageSize = ref(10)
const currentPage = ref(1)

const resetForm = () => {
	formData.name = ''
	formData.is_enabled = true
	errors.name = ''
	editingProj.value = null
}

const handleCreate = () => {
	resetForm()
	showCreateModal.value = true
}

const filteredProjects = computed(() => {
	if (!searchQuery.value.trim()) return projects.value
	const query = searchQuery.value.toLowerCase()
	return projects.value.filter((proj) => proj.name.toLowerCase().includes(query))
})

const sortedProjects = computed(() => {
	// If no sort applied, return filtered data as-is
	if (!sortBy.value) return filteredProjects.value

	const sorted = [...filteredProjects.value].sort((a, b) => {
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
	Math.max(1, Math.ceil(sortedProjects.value.length / pageSize.value)),
)
const paginatedProjects = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value
	const end = start + pageSize.value
	return sortedProjects.value.slice(start, end)
})
const pageRangeStart = computed(() =>
	sortedProjects.value.length === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1,
)
const pageRangeEnd = computed(() =>
	Math.min(sortedProjects.value.length, currentPage.value * pageSize.value),
)

const toggleSort = (field: 'name' | 'is_enabled') => {
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

const getSortIcon = (field: 'name' | 'is_enabled') => _getSortIcon(field, sortBy, sortOrder)

const goToPage = (page: number) => {
	if (page < 1 || page > totalPages.value) return
	currentPage.value = page
}

watch([pageSize, () => sortedProjects.value.length], () => {
	currentPage.value = 1
})

const handleEdit = (proj: Project) => {
	editingProj.value = proj
	formData.name = proj.name
	formData.is_enabled = proj.is_enabled
	showEditModal.value = true
}

const handleDelete = (id: number) => {
	deletingProjId.value = id
	showDeleteModal.value = true
}

const confirmDelete = async () => {
	if (deletingProjId.value !== null) {
		try {
			await projectStore.deleteProject(deletingProjId.value)
			showDeleteModal.value = false
			deletingProjId.value = null
		} catch (error) {
			console.error('Failed to delete project:', error)
			showToast(t('admin.proj.deleteFailed', 'Failed to delete project'), 'error')
		}
	}
}

const cancelDelete = () => {
	showDeleteModal.value = false
	deletingProjId.value = null
}

const handleToggleEnabled = async (id: number, currentStatus: boolean) => {
	try {
		await projectStore.updateProject(id, { is_enabled: !currentStatus })
	} catch (error) {
		console.error('Failed to toggle status:', error)
		showToast(t('admin.proj.toggleFailed', 'Failed to toggle status'), 'error')
	}
}

const handleSave = async () => {
	errors.name = ''

	if (!formData.name.trim()) {
		errors.name = t('admin.proj.nameRequired')
		return
	}

	isSaving.value = true
	try {
		const payload = {
			name: formData.name,
			is_enabled: formData.is_enabled,
		}

		if (editingProj.value) {
			await projectStore.updateProject(editingProj.value.id, payload)
		} else {
			await projectStore.createProject(payload)
		}
		showCreateModal.value = false
		showEditModal.value = false
		resetForm()
	} catch (error) {
		console.error('Failed to save project:', error)
		if (typeof error === 'object' && error !== null && 'response' in error) {
			const err = error as {
				response?: { data?: { name?: string | string[] } }
			}
			if (err.response?.data?.name) {
				errors.name = Array.isArray(err.response.data.name)
					? err.response.data.name[0] || t('admin.proj.invalidName')
					: err.response.data.name || t('admin.proj.invalidName')
			}
		}
	} finally {
		isSaving.value = false
	}
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

// Load initial data from API
onMounted(async () => {
	await projectStore.fetchProjects()
	window.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', handleEscKey)
})
</script>
