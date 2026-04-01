<template>
    <div v-if="showFilters"
        class="mb-4 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div v-if="isPtbAdmin" class="min-w-0 space-y-2">
                <label class="block text-xs font-semibold uppercase tracking-[0.14em] text-gray-500 dark:text-gray-400">
                    {{ t('kanban.department') }}
                </label>
                <MultipleSelect v-model="departmentSelection" :options="departmentOptions"
                    :placeholder="t('kanban.allDepartments')" searchable :search-placeholder="searchDepartmentsLabel"
                    :empty-text="t('common.noData')" />
            </div>

            <div v-if="isPtbAdmin" class="min-w-0 space-y-2">
                <label class="block text-xs font-semibold uppercase tracking-[0.14em] text-gray-500 dark:text-gray-400">
                    {{ t('kanban.employee') }}
                </label>
                <MultipleSelect v-model="employeeSelection" :options="employeeOptions"
                    :placeholder="t('kanban.allEmployees')" searchable :search-placeholder="searchEmployeesLabel"
                    :empty-text="t('common.noData')" />
            </div>

            <div class="min-w-0 space-y-2">
                <label class="block text-xs font-semibold uppercase tracking-[0.14em] text-gray-500 dark:text-gray-400">
                    {{ t('kanban.project') }}
                </label>
                <MultipleSelect v-model="projectSelection" :options="projectOptions"
                    :placeholder="t('kanban.allProjects')" searchable :search-placeholder="t('kanban.searchProjects')"
                    :empty-text="t('kanban.noProjectsFound')" />
            </div>

            <div class="min-w-0 space-y-2">
                <label class="block text-xs font-semibold uppercase tracking-[0.14em] text-gray-500 dark:text-gray-400">
                    {{ t('kanban.status') }}
                </label>
                <MultipleSelect v-model="statusSelection" :options="statusOptions"
                    :placeholder="t('kanban.allStatuses')" />
            </div>

            <div class="min-w-0 space-y-2">
                <label class="block text-xs font-semibold uppercase tracking-[0.14em] text-gray-500 dark:text-gray-400">
                    {{ t('kanban.priority') }}
                </label>
                <MultipleSelect v-model="prioritySelection" :options="priorityOptions"
                    :placeholder="t('kanban.allPriorities')" />
            </div>

            <div class="min-w-0 space-y-2">
                <label class="block text-xs font-semibold uppercase tracking-[0.14em] text-gray-500 dark:text-gray-400">
                    {{ t('kanban.label') }}
                </label>
                <MultipleSelect v-model="labelSelection" :options="labelOptions" :placeholder="t('kanban.allLabels')" />
            </div>

            <div class="min-w-0 space-y-2">
                <label class="block text-xs font-semibold uppercase tracking-[0.14em] text-gray-500 dark:text-gray-400">
                    {{ t('kanban.group') }}
                </label>
                <MultipleSelect v-model="groupSelection" :options="groupOptions" :placeholder="t('kanban.allGroups')"
                    searchable :search-placeholder="searchGroupsLabel" :empty-text="t('common.noData')" />
            </div>
        </div>

        <div class="mt-4 flex flex-wrap items-start justify-between gap-3 border-t border-gray-100 pt-4 dark:border-gray-700">
            <div class="flex flex-wrap gap-2">
                <span v-for="departmentId in selectedDepartment" :key="`department-${departmentId}`"
                    class="inline-flex items-center rounded-full bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700 dark:bg-sky-900/30 dark:text-sky-200">
                    {{ departmentName(departmentId) }}
                    <button @click="removeDepartment(departmentId)" class="ml-2 text-sky-500 hover:text-sky-800">
                        ×
                    </button>
                </span>
                <span v-for="employeeId in selectedEmployee" :key="`employee-${employeeId}`"
                    class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-200">
                    {{ employeeName(employeeId) }}
                    <button @click="removeEmployee(employeeId)" class="ml-2 text-blue-500 hover:text-blue-800">
                        ×
                    </button>
                </span>
                <span v-for="projectId in selectedProject" :key="`project-${projectId}`"
                    class="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-200">
                    {{ projectName(projectId) }}
                    <button @click="removeProject(projectId)" class="ml-2 text-emerald-500 hover:text-emerald-800">
                        ×
                    </button>
                </span>
                <span v-for="status in selectedStatus" :key="`status-${status}`"
                    class="inline-flex items-center rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-200">
                    {{ statusLabel(status) }}
                    <button @click="removeStatus(status)" class="ml-2 text-amber-500 hover:text-amber-800">
                        ×
                    </button>
                </span>
                <span v-for="priority in selectedPriority" :key="`priority-${priority}`"
                    class="inline-flex items-center rounded-full bg-rose-50 px-3 py-1 text-xs font-medium text-rose-700 dark:bg-rose-900/30 dark:text-rose-200">
                    {{ priorityLabel(priority) }}
                    <button @click="removePriority(priority)" class="ml-2 text-rose-500 hover:text-rose-800">
                        ×
                    </button>
                </span>
                <span v-for="label in selectedLabel" :key="`label-${label}`"
                    :class="['inline-flex items-center rounded-full px-3 py-1 text-xs font-medium', getLabelColor(label)]">
                    {{ label }}
                    <button @click="removeLabel(label)" class="ml-2 hover:opacity-80">
                        ×
                    </button>
                </span>
                <span v-for="groupId in selectedGroup" :key="`group-${groupId}`"
                    class="inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium"
                    :style="groupChipStyle(groupId)">
                    {{ groupName(groupId) }}
                    <button @click="removeGroup(groupId)" class="ml-2 hover:opacity-80">
                        ×
                    </button>
                </span>
                <span v-if="activeFiltersCount === 0" class="text-sm text-gray-500 dark:text-gray-400">
                    {{ showingAllTasksLabel }}
                </span>
            </div>

            <button v-if="activeFiltersCount > 0" @click="$emit('clear-filters')"
                class="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 transition hover:border-red-300 hover:text-red-600 dark:border-gray-600 dark:text-gray-300 dark:hover:border-red-500/40 dark:hover:text-red-300">
                <XIcon class="h-4 w-4" />
                <span>{{ t('common.clear') }}</span>
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import MultipleSelect from '@/components/forms/FormElements/MultipleSelect.vue'
import { availableLabels, getLabelColor, getPriorityConfig } from '@/composables/kanban'
import type { PriorityLevel, TaskStatus } from '@/composables/kanban/useKanbanHelpers'
import { XIcon } from '@/icons'
import type { Department } from '@/services/api/department'
import type { Employee } from '@/services/api/employee'
import type { Project } from '@/services/api/project'
import type { TaskGroup } from '@/services/api/task'

type OptionItem = {
	value: number | string
	label: string
}

const { t, te } = useI18n()

const props = defineProps<{
	showFilters: boolean
	isPtbAdmin: boolean
	selectedDepartment: number[]
	selectedEmployee: number[]
	selectedProject: number[]
    selectedStatus: TaskStatus[]
    selectedPriority: PriorityLevel[]
	selectedLabel: string[]
	selectedGroup: number[]
	activeFiltersCount: number
	sortedDepartments: Department[]
	sortedEmployees: Employee[]
	filteredEmployees: Employee[]
	sortedProjects: Project[]
	taskGroups: TaskGroup[]
}>()

const emit = defineEmits<{
	'update:selectedDepartment': [value: number[]]
	'update:selectedEmployee': [value: number[]]
	'update:selectedProject': [value: number[]]
    'update:selectedStatus': [value: TaskStatus[]]
    'update:selectedPriority': [value: PriorityLevel[]]
	'update:selectedLabel': [value: string[]]
	'update:selectedGroup': [value: number[]]
	'clear-filters': []
}>()

const searchDepartmentsLabel = computed(() =>
	te('kanban.searchDepartments') ? t('kanban.searchDepartments') : t('common.search'),
)
const searchEmployeesLabel = computed(() =>
	te('kanban.searchEmployees') ? t('kanban.searchEmployees') : t('common.search'),
)
const searchGroupsLabel = computed(() =>
	te('kanban.searchGroups') ? t('kanban.searchGroups') : t('common.search'),
)
const showingAllTasksLabel = computed(() =>
	te('kanban.showingAllTasks') ? t('kanban.showingAllTasks') : t('kanban.showingTasksFor'),
)

const departmentOptions = computed<OptionItem[]>(() =>
	props.sortedDepartments.map((department) => ({
		value: department.id,
		label: department.name,
	})),
)

const employeeOptions = computed<OptionItem[]>(() =>
	props.filteredEmployees.map((employee) => ({
		value: employee.id,
		label: employee.name,
	})),
)

const projectOptions = computed<OptionItem[]>(() =>
	props.sortedProjects.map((project) => ({
		value: project.id,
		label: project.name,
	})),
)

const statusOptions = computed<OptionItem[]>(() => [
	{ value: 'todo', label: t('kanban.todo') },
	{ value: 'in_progress', label: t('kanban.inProgress') },
	{ value: 'done', label: t('kanban.done') },
])

const priorityOptions = computed<OptionItem[]>(() =>
	(['low', 'medium', 'high', 'urgent'] as const).map((priority) => ({
		value: priority,
		label: priorityLabel(priority),
	})),
)

const labelOptions = computed<OptionItem[]>(() =>
	availableLabels.map((label) => ({
		value: label.name,
		label: label.name,
	})),
)

const groupOptions = computed<OptionItem[]>(() =>
	props.taskGroups.map((group) => ({
		value: group.id,
		label: group.name,
	})),
)

function toOptionItems(values: Array<number | string>, options: OptionItem[]) {
	return values
		.map((value) => options.find((option) => option.value === value))
		.filter((option): option is OptionItem => !!option)
}

function fromOptionItems(values: OptionItem[]) {
	return values.map((value) => value.value)
}

const departmentSelection = computed<OptionItem[]>({
	get: () => toOptionItems(props.selectedDepartment, departmentOptions.value),
	set: (value) => emit('update:selectedDepartment', fromOptionItems(value).map(Number)),
})

const employeeSelection = computed<OptionItem[]>({
	get: () => toOptionItems(props.selectedEmployee, employeeOptions.value),
	set: (value) => emit('update:selectedEmployee', fromOptionItems(value).map(Number)),
})

const projectSelection = computed<OptionItem[]>({
	get: () => toOptionItems(props.selectedProject, projectOptions.value),
	set: (value) => emit('update:selectedProject', fromOptionItems(value).map(Number)),
})

const statusSelection = computed<OptionItem[]>({
	get: () => toOptionItems(props.selectedStatus, statusOptions.value),
    set: (value) => emit('update:selectedStatus', fromOptionItems(value).map(String) as TaskStatus[]),
})

const prioritySelection = computed<OptionItem[]>({
	get: () => toOptionItems(props.selectedPriority, priorityOptions.value),
    set: (value) =>
        emit('update:selectedPriority', fromOptionItems(value).map(String) as PriorityLevel[]),
})

const labelSelection = computed<OptionItem[]>({
	get: () => toOptionItems(props.selectedLabel, labelOptions.value),
	set: (value) => emit('update:selectedLabel', fromOptionItems(value).map(String)),
})

const groupSelection = computed<OptionItem[]>({
	get: () => toOptionItems(props.selectedGroup, groupOptions.value),
	set: (value) => emit('update:selectedGroup', fromOptionItems(value).map(Number)),
})

function departmentName(id: number) {
	return props.sortedDepartments.find((department) => department.id === id)?.name ?? String(id)
}

function employeeName(id: number) {
	return props.sortedEmployees.find((employee) => employee.id === id)?.name ?? String(id)
}

function projectName(id: number) {
	return props.sortedProjects.find((project) => project.id === id)?.name ?? String(id)
}

function groupName(id: number) {
	return props.taskGroups.find((group) => group.id === id)?.name ?? String(id)
}

function groupChipStyle(groupId: number) {
	const color = props.taskGroups.find((group) => group.id === groupId)?.color || '#6366F1'
	return {
		backgroundColor: `${color}20`,
		borderColor: `${color}66`,
		color,
	}
}

function statusLabel(status: TaskStatus) {
	if (status === 'todo') return t('kanban.todo')
	if (status === 'in_progress') return t('kanban.inProgress')
	return t('kanban.done')
}

function priorityLabel(priority: PriorityLevel) {
	const config = getPriorityConfig(priority)
	return config ? `${config.icon} ${config.label}` : priority
}

function removeDepartment(id: number) {
	emit('update:selectedDepartment', props.selectedDepartment.filter((value) => value !== id))
}

function removeEmployee(id: number) {
	emit('update:selectedEmployee', props.selectedEmployee.filter((value) => value !== id))
}

function removeProject(id: number) {
	emit('update:selectedProject', props.selectedProject.filter((value) => value !== id))
}

function removeStatus(status: TaskStatus) {
	emit('update:selectedStatus', props.selectedStatus.filter((value) => value !== status))
}

function removePriority(priority: PriorityLevel) {
	emit('update:selectedPriority', props.selectedPriority.filter((value) => value !== priority))
}

function removeLabel(label: string) {
	emit('update:selectedLabel', props.selectedLabel.filter((value) => value !== label))
}

function removeGroup(id: number) {
	emit('update:selectedGroup', props.selectedGroup.filter((value) => value !== id))
}
</script>
