import { computed, type Ref, ref, shallowReactive, watch } from 'vue'

import type { CalendarEvent } from '@/services/api/calendar'
import type { Project } from '@/services/api/project'
import type { TaskGroup } from '@/services/api/task'
import { useAuthStore } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import { useEmployeeStore } from '@/stores/employee'

import type { PriorityLevel, TaskStatus } from './useKanbanHelpers'

export type TaskScope = 'all' | 'mine'

export function useKanbanFilters(
	events: Ref<CalendarEvent[]>,
	projects: Ref<Project[]>,
	taskGroups: Ref<TaskGroup[]>,
) {
	const authStore = useAuthStore()
	const employeeStore = useEmployeeStore()
	const departmentStore = useDepartmentStore()

	const selectedProject = ref<number[]>([])
	const selectedEmployee = ref<number[]>([])
	const selectedDepartment = ref<number[]>([])
	const selectedStatus = ref<TaskStatus[]>([])
	const showFilters = ref(false)
	const selectedLabel = ref<string[]>([])
	const selectedPriority = ref<PriorityLevel[]>([])
	const selectedGroup = ref<number[]>([])
	const storedScope = localStorage.getItem('kanban-task-scope')
	const taskScope = ref<TaskScope>(storedScope === 'all' || storedScope === 'mine' ? storedScope : 'all')
	watch(taskScope, (value) => localStorage.setItem('kanban-task-scope', value))
	const isElevatedTaskManager = computed(
		() => authStore.isPtbAdmin || authStore.isSuperAdmin || authStore.isDeveloper,
	)

	const currentUserEmployeeId = computed(() => {
		const currentUser = authStore.user
		if (!currentUser?.worker_id) return null
		const matchingEmployee = employeeStore.employees.find(
			(employee) => employee.emp_id.toLowerCase() === currentUser.worker_id?.toLowerCase(),
		)
		return matchingEmployee?.id ?? null
	})

	const userGroupIds = computed(() => {
		const userEmpId = currentUserEmployeeId.value
		if (!userEmpId) return []
		return taskGroups.value
			.filter((group) => group.members.includes(userEmpId))
			.map((group) => group.id)
	})

	const userGroupIdSet = computed(() => new Set(userGroupIds.value))

	const sortedProjects = computed(() => {
		return [...projects.value]
			.filter((project) => project.is_enabled)
			.sort((left, right) => left.name.localeCompare(right.name))
	})

	const sortedEmployees = computed(() => {
		return [...employeeStore.employees]
			.filter((employee) => employee.is_enabled)
			.sort((left, right) => left.name.localeCompare(right.name))
	})

	const sortedDepartments = computed(() => {
		return [...departmentStore.departments]
			.filter((department) => department.is_enabled)
			.sort((left, right) => left.name.localeCompare(right.name))
	})

	const filteredEmployees = computed(() => {
		if (selectedDepartment.value.length === 0) return sortedEmployees.value
		const selectedDepartmentSet = new Set(selectedDepartment.value)
		return sortedEmployees.value.filter((employee) => selectedDepartmentSet.has(employee.department))
	})

	const activeFiltersCount = computed(() => {
		let count = selectedProject.value.length
		count += selectedStatus.value.length
		count += selectedLabel.value.length
		count += selectedPriority.value.length
		count += selectedGroup.value.length

		if (isElevatedTaskManager.value) {
			count += selectedEmployee.value.length
			count += selectedDepartment.value.length
		}

		return count
	})

	const columnTasksMap = shallowReactive<Record<TaskStatus, CalendarEvent[]>>({
		todo: [],
		in_progress: [],
		done: [],
	})

	const visibleTasks = computed(() => {
		const canSeeAllTasks = isElevatedTaskManager.value && taskScope.value === 'all'
		const userEmpId = currentUserEmployeeId.value
		const selectedProjectSet = new Set(selectedProject.value)
		const selectedLabelSet = new Set(selectedLabel.value)
		const selectedPrioritySet = new Set(selectedPriority.value)
		const selectedGroupSet = new Set(selectedGroup.value)
		const selectedEmployeeSet = new Set(selectedEmployee.value)
		const selectedDepartmentSet = new Set(selectedDepartment.value)

		const deptEmployeeIdSet =
			isElevatedTaskManager.value && selectedDepartmentSet.size > 0
				? new Set(
						employeeStore.employees
							.filter((employee) => selectedDepartmentSet.has(employee.department))
							.map((employee) => employee.id),
				  )
				: new Set<number>()

		const matchesUserScope = (task: CalendarEvent) => {
			if (!userEmpId) return false
			const isCreator = task.created_by === userEmpId
			const isAssigned = task.assigned_to?.includes(userEmpId)
			const isInUserGroup = !!task.group && userGroupIdSet.value.has(task.group)
			return isCreator || !!isAssigned || isInUserGroup
		}

		return events.value.filter((task) => {
			if (selectedProjectSet.size > 0 && (!task.project || !selectedProjectSet.has(task.project))) {
				return false
			}

			if (
				selectedLabelSet.size > 0 &&
				!(task.labels ?? []).some((label) => selectedLabelSet.has(label))
			) {
				return false
			}

			if (
				selectedPrioritySet.size > 0 &&
				(!task.priority || !selectedPrioritySet.has(task.priority))
			) {
				return false
			}

			if (selectedGroupSet.size > 0 && (!task.group || !selectedGroupSet.has(task.group))) {
				return false
			}

			const taskStatus = (task.status || 'todo') as TaskStatus
			if (selectedStatus.value.length > 0 && !selectedStatus.value.includes(taskStatus)) {
				return false
			}

			if (isElevatedTaskManager.value && selectedEmployeeSet.size > 0) {
				const isCreator = !!task.created_by && selectedEmployeeSet.has(task.created_by)
				const isAssigned = task.assigned_to?.some((employeeId) => selectedEmployeeSet.has(employeeId))
				if (!isCreator && !isAssigned) {
					return false
				}
			}

			if (isElevatedTaskManager.value && selectedDepartmentSet.size > 0) {
				const creatorInDepartment = task.created_by ? deptEmployeeIdSet.has(task.created_by) : false
				const assigneeInDepartment =
					task.assigned_to?.some((employeeId) => deptEmployeeIdSet.has(employeeId)) ?? false
				if (!creatorInDepartment && !assigneeInDepartment) {
					return false
				}
			}

			if (!canSeeAllTasks && !matchesUserScope(task)) {
				return false
			}

			return true
		})
	})

	function updateColumnTasks() {
		const nextTodo: CalendarEvent[] = []
		const nextInProgress: CalendarEvent[] = []
		const nextDone: CalendarEvent[] = []

		for (const task of visibleTasks.value) {
			const status = (task.status || 'todo') as TaskStatus
			if (status === 'todo') nextTodo.push(task)
			else if (status === 'in_progress') nextInProgress.push(task)
			else if (status === 'done') nextDone.push(task)
		}

		columnTasksMap.todo = nextTodo
		columnTasksMap.in_progress = nextInProgress
		columnTasksMap.done = nextDone
	}

	function clearFilters() {
		selectedProject.value = []
		if (isElevatedTaskManager.value) {
			selectedEmployee.value = []
			selectedDepartment.value = []
		}
		selectedStatus.value = []
		selectedLabel.value = []
		selectedPriority.value = []
		selectedGroup.value = []
	}

	watch(
		[
			events,
			selectedProject,
			selectedEmployee,
			selectedDepartment,
			selectedStatus,
			selectedLabel,
			selectedPriority,
			selectedGroup,
			taskScope,
			userGroupIds,
		],
		() => updateColumnTasks(),
		{ immediate: true, deep: true },
	)

	watch(selectedDepartment, (newDepartments) => {
		if (newDepartments.length === 0 || selectedEmployee.value.length === 0) return

		const allowedDepartmentSet = new Set(newDepartments)
		selectedEmployee.value = selectedEmployee.value.filter((employeeId) => {
			const employee = employeeStore.employees.find((entry) => entry.id === employeeId)
			return employee ? allowedDepartmentSet.has(employee.department) : false
		})
	})

	return {
		selectedProject,
		selectedEmployee,
		selectedDepartment,
		selectedStatus,
		showFilters,
		selectedLabel,
		selectedPriority,
		selectedGroup,
		taskScope,
		isElevatedTaskManager,
		currentUserEmployeeId,
		userGroupIds,
		sortedProjects,
		sortedEmployees,
		sortedDepartments,
		filteredEmployees,
		activeFiltersCount,
		columnTasksMap,
		updateColumnTasks,
		clearFilters,
	}
}
