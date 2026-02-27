<template>
    <div v-if="showFilters"
        class="mb-4 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm">
        <div class="flex flex-wrap items-end gap-4">
            <!-- Department Filter (PTB admins only) -->
            <div v-if="isPtbAdmin" class="flex-1 min-w-[200px]">
                <label
                    class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.department') }}</label>
                <div class="relative">
                    <select :value="selectedDepartment" @change="$emit('update:selectedDepartment', ($event.target as HTMLSelectElement).value === '' ? null : Number(($event.target as HTMLSelectElement).value))"
                        class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                        <option :value="null">{{ t('kanban.allDepartments') }}</option>
                        <option v-for="dept in sortedDepartments" :key="dept.id" :value="dept.id">{{ dept.name
                            }}</option>
                    </select>
                    <ChevronDownIcon
                        class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
            </div>

            <!-- Employee Filter (PTB admins only) -->
            <div v-if="isPtbAdmin" class="flex-1 min-w-[200px]">
                <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.employee') }}</label>
                <div class="relative">
                    <select :value="selectedEmployee" @change="$emit('update:selectedEmployee', ($event.target as HTMLSelectElement).value === '' ? null : Number(($event.target as HTMLSelectElement).value))"
                        class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                        <option :value="null">{{ t('kanban.allEmployees') }}</option>
                        <option v-for="emp in filteredEmployees" :key="emp.id" :value="emp.id">{{ emp.name }}
                        </option>
                    </select>
                    <ChevronDownIcon
                        class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
            </div>

            <!-- Project Filter (Searchable Dropdown) -->
            <div class="flex-1 min-w-[200px]">
                <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.project') }}</label>
                <div class="relative" ref="filterProjectDropdownRef">
                    <input type="text" :value="filterProjectSearch" @input="$emit('update:filterProjectSearch', ($event.target as HTMLInputElement).value)" @focus="$emit('update:showFilterProjectDropdown', true)"
                        @blur="$emit('filter-project-blur')"
                        :placeholder="selectedProject ? '' : t('kanban.searchProjects')"
                        class="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:border-brand-500" />

                    <!-- Selected Project Display -->
                    <div v-if="selectedProject && !showFilterProjectDropdown && !filterProjectSearch"
                        class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                        <span class="text-gray-700 dark:text-gray-300 text-sm">
                            {{sortedProjects.find(p => p.id === selectedProject)?.name}}
                        </span>
                    </div>

                    <ChevronDownIcon class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />

                    <!-- Dropdown -->
                    <div v-if="showFilterProjectDropdown"
                        class="absolute z-50 mt-1 w-full max-h-48 overflow-y-auto bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
                        <button type="button"
                            @mousedown.prevent="$emit('update:selectedProject', null); $emit('update:showFilterProjectDropdown', false); $emit('update:filterProjectSearch', '')"
                            :class="['w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700', selectedProject === null ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300' : 'text-gray-700 dark:text-gray-300']">
                            {{ t('kanban.allProjects') }}
                        </button>
                        <button v-for="proj in filteredFilterProjects" :key="proj.id" type="button"
                            @mousedown.prevent="$emit('update:selectedProject', proj.id); $emit('update:showFilterProjectDropdown', false); $emit('update:filterProjectSearch', '')"
                            :class="['w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700', selectedProject === proj.id ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300' : 'text-gray-700 dark:text-gray-300']">
                            {{ proj.name }}
                        </button>
                        <p v-if="filteredFilterProjects.length === 0 && filterProjectSearch"
                            class="text-center text-gray-400 text-sm py-2">
                            {{ t('kanban.noProjectsFound') }}
                        </p>
                    </div>
                </div>
            </div>

            <!-- Status Filter -->
            <div class="flex-1 min-w-[150px]">
                <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.status') }}</label>
                <div class="relative">
                    <select :value="selectedStatus" @change="$emit('update:selectedStatus', ($event.target as HTMLSelectElement).value || null)"
                        class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                        <option :value="null">{{ t('kanban.allStatuses') }}</option>
                        <option value="todo">{{ t('kanban.todo') }}</option>
                        <option value="in_progress">{{ t('kanban.inProgress') }}</option>
                        <option value="done">{{ t('kanban.done') }}</option>
                    </select>
                    <ChevronDownIcon
                        class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
            </div>

            <!-- Priority Filter -->
            <div class="flex-1 min-w-[140px]">
                <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.priority') }}</label>
                <div class="relative">
                    <select :value="selectedPriority" @change="$emit('update:selectedPriority', ($event.target as HTMLSelectElement).value || null)"
                        class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                        <option :value="null">{{ t('kanban.allPriorities') }}</option>
                        <option value="low">{{ t('kanban.low') }}</option>
                        <option value="medium">{{ t('kanban.medium') }}</option>
                        <option value="high">{{ t('kanban.high') }}</option>
                        <option value="urgent">{{ t('kanban.urgent') }}</option>
                    </select>
                    <ChevronDownIcon
                        class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
            </div>

            <!-- Label Filter -->
            <div class="flex-1 min-w-[150px]">
                <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.label') }}</label>
                <div class="relative">
                    <select :value="selectedLabel" @change="$emit('update:selectedLabel', ($event.target as HTMLSelectElement).value || null)"
                        class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                        <option :value="null">{{ t('kanban.allLabels') }}</option>
                        <option v-for="label in availableLabels" :key="label.name" :value="label.name">{{
                            label.name }}</option>
                    </select>
                    <ChevronDownIcon
                        class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
            </div>

            <!-- Group Filter -->
            <div class="flex-1 min-w-[150px]">
                <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.group') }}</label>
                <div class="relative">
                    <select :value="selectedGroup" @change="$emit('update:selectedGroup', ($event.target as HTMLSelectElement).value === '' ? null : Number(($event.target as HTMLSelectElement).value))"
                        class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                        <option :value="null">{{ t('kanban.allGroups') }}</option>
                        <option v-for="group in taskGroups" :key="group.id" :value="group.id">
                            {{ group.name }}
                        </option>
                    </select>
                    <ChevronDownIcon
                        class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
            </div>

            <!-- Clear Filters Button -->
            <button v-if="activeFiltersCount > 0" @click="$emit('clear-filters')"
                class="px-3 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 transition flex items-center gap-1">
                <XIcon class="w-4 h-4" />
                <span>{{ t('common.clear') }}</span>
            </button>
        </div>

        <!-- Active Filters Summary -->
        <div v-if="activeFiltersCount > 0" class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
            <div class="flex flex-wrap items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <span>{{ t('kanban.showingTasksFor') }}</span>
                <span v-if="isPtbAdmin && selectedDepartment"
                    class="inline-flex items-center px-2 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded-full text-xs">
                    {{sortedDepartments.find(d => d.id === selectedDepartment)?.name}}
                    <button @click="$emit('update:selectedDepartment', null)" class="ml-1 hover:text-purple-900">×</button>
                </span>
                <span v-if="isPtbAdmin && selectedEmployee"
                    class="inline-flex items-center px-2 py-0.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-full text-xs">
                    {{filteredEmployees.find(e => e.id === selectedEmployee)?.name || sortedEmployees.find(e =>
                        e.id === selectedEmployee)?.name}}
                    <button @click="$emit('update:selectedEmployee', null)" class="ml-1 hover:text-blue-900">×</button>
                </span>
                <span v-if="selectedProject"
                    class="inline-flex items-center px-2 py-0.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-full text-xs">
                    {{sortedProjects.find(p => p.id === selectedProject)?.name}}
                    <button @click="$emit('update:selectedProject', null)" class="ml-1 hover:text-green-900">×</button>
                </span>
                <span v-if="selectedStatus"
                    class="inline-flex items-center px-2 py-0.5 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 rounded-full text-xs">
                    {{ selectedStatus === 'todo' ? t('kanban.todo') : selectedStatus === 'in_progress' ? t('kanban.inProgress') :
                        t('kanban.done') }}
                    <button @click="$emit('update:selectedStatus', null)" class="ml-1 hover:text-orange-900">×</button>
                </span>
                <span v-if="selectedPriority"
                    class="inline-flex items-center px-2 py-0.5 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-full text-xs">
                    {{ getPriorityConfig(selectedPriority)?.icon }} {{
                        getPriorityConfig(selectedPriority)?.label }}
                    <button @click="$emit('update:selectedPriority', null)" class="ml-1 hover:text-red-900">×</button>
                </span>
                <span v-if="selectedLabel"
                    :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs', getLabelColor(selectedLabel)]">
                    {{ selectedLabel }}
                    <button @click="$emit('update:selectedLabel', null)" class="ml-1 hover:opacity-75">×</button>
                </span>
                <span v-if="selectedGroup" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs"
                    :style="{ backgroundColor: getSelectedGroupColor() + '20', color: getSelectedGroupColor(), borderColor: getSelectedGroupColor() }"
                    style="border-width: 1px;">
                    {{taskGroups.find(g => g.id === selectedGroup)?.name}}
                    <button @click="$emit('update:selectedGroup', null)" class="ml-1 hover:opacity-75">×</button>
                </span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { availableLabels, getLabelColor, getPriorityConfig } from '@/composables/kanban'
import { ChevronDownIcon, XIcon } from '@/icons'
import type { Department } from '@/services/api/department'
import type { Employee } from '@/services/api/employee'
import type { Project } from '@/services/api/project'
import type { TaskGroup } from '@/services/api/task'

const { t } = useI18n()

const filterProjectDropdownRef = ref<HTMLElement | null>(null)

defineProps<{
	showFilters: boolean
	isPtbAdmin: boolean
	selectedDepartment: number | null
	selectedEmployee: number | null
	selectedProject: number | null
	selectedStatus: string | null
	selectedPriority: string | null
	selectedLabel: string | null
	selectedGroup: number | null
	filterProjectSearch: string
	showFilterProjectDropdown: boolean
	activeFiltersCount: number
	sortedDepartments: Department[]
	sortedEmployees: Employee[]
	filteredEmployees: Employee[]
	sortedProjects: Project[]
	filteredFilterProjects: Project[]
	taskGroups: TaskGroup[]
	getSelectedGroupColor: () => string
}>()

defineEmits<{
	'update:selectedDepartment': [value: number | null]
	'update:selectedEmployee': [value: number | null]
	'update:selectedProject': [value: number | null]
	'update:selectedStatus': [value: string | null]
	'update:selectedPriority': [value: string | null]
	'update:selectedLabel': [value: string | null]
	'update:selectedGroup': [value: number | null]
	'update:filterProjectSearch': [value: string]
	'update:showFilterProjectDropdown': [value: boolean]
	'filter-project-blur': []
	'clear-filters': []
}>()
</script>
