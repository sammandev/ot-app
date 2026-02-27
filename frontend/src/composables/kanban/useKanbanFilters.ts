import { computed, type Ref, ref, shallowReactive, watch } from 'vue'

import type { CalendarEvent } from '@/services/api/calendar'
import type { Project } from '@/services/api/project'
import type { TaskGroup } from '@/services/api/task'
import { useAuthStore } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import { useEmployeeStore } from '@/stores/employee'

import type { PriorityLevel, TaskStatus } from './useKanbanHelpers'

export function useKanbanFilters(
	events: Ref<CalendarEvent[]>,
	projects: Ref<Project[]>,
	taskGroups: Ref<TaskGroup[]>,
) {
	const authStore = useAuthStore()
	const employeeStore = useEmployeeStore()
	const departmentStore = useDepartmentStore()

	// ── Filter State ────────────────────────────────────────────────────
	const selectedProject = ref<number | null>(null)
	const selectedEmployee = ref<number | null>(null)
	const selectedDepartment = ref<number | null>(null)
	const selectedStatus = ref<string | null>(null)
	const showFilters = ref(false)
	const selectedLabel = ref<string | null>(null)
	const selectedPriority = ref<PriorityLevel | null>(null)
	const selectedGroup = ref<number | null>(null)

	// Filter dropdown search state
	const filterProjectSearch = ref('')
	const showFilterProjectDropdown = ref(false)
	const filterProjectDropdownRef = ref<HTMLElement | null>(null)

	// ── Computed: Current User Employee ID ──────────────────────────────
	const currentUserEmployeeId = computed(() => {
		const currentUser = authStore.user
		if (!currentUser?.worker_id) return null
		const matchingEmployee = employeeStore.employees.find(
			(emp) => emp.emp_id.toLowerCase() === currentUser.worker_id?.toLowerCase(),
		)
		return matchingEmployee?.id ?? null
	})

	// Groups the current user is a member of
	const userGroupIds = computed(() => {
		const userEmpId = currentUserEmployeeId.value
		if (!userEmpId) return []
		return taskGroups.value
			.filter((group) => group.members.includes(userEmpId))
			.map((group) => group.id)
	})

	// ── Sorted Reference Data ──────────────────────────────────────────
	const sortedProjects = computed(() => {
		return [...projects.value]
			.filter((p) => p.is_enabled)
			.sort((a, b) => a.name.localeCompare(b.name))
	})

	const sortedEmployees = computed(() => {
		return [...employeeStore.employees]
			.filter((e) => e.is_enabled)
			.sort((a, b) => a.name.localeCompare(b.name))
	})

	const sortedDepartments = computed(() => {
		return [...departmentStore.departments]
			.filter((d) => d.is_enabled)
			.sort((a, b) => a.name.localeCompare(b.name))
	})

	// Employees filtered by selected department
	const filteredEmployees = computed(() => {
		if (!selectedDepartment.value) return sortedEmployees.value
		return sortedEmployees.value.filter((e) => e.department === selectedDepartment.value)
	})

	// Filter dropdown search filtered projects
	const filteredFilterProjects = computed(() => {
		if (!filterProjectSearch.value) return sortedProjects.value
		const query = filterProjectSearch.value.toLowerCase()
		return sortedProjects.value.filter((p) => p.name.toLowerCase().includes(query))
	})

	// Active filters count
	const activeFiltersCount = computed(() => {
		let count = 0
		if (selectedProject.value) count++
		if (authStore.isPtbAdmin && selectedEmployee.value) count++
		if (authStore.isPtbAdmin && selectedDepartment.value) count++
		if (selectedStatus.value) count++
		if (selectedLabel.value) count++
		if (selectedPriority.value) count++
		if (selectedGroup.value) count++
		return count
	})

	// ── Column Tasks Map ───────────────────────────────────────────────
	const columnTasksMap = shallowReactive<Record<TaskStatus, CalendarEvent[]>>({
		todo: [],
		in_progress: [],
		done: [],
	})

	function updateColumnTasks() {
		const isPtbAdmin = authStore.isPtbAdmin
		const userEmpId = currentUserEmployeeId.value

		// Pre-compute department employee ID set once (avoids per-task recomputation)
		const deptEmployeeIdSet =
			isPtbAdmin && selectedDepartment.value
				? new Set(
						employeeStore.employees
							.filter((e) => e.department === selectedDepartment.value)
							.map((e) => e.id),
					)
				: new Set<number>()

		const filteredEvents = events.value.filter((task) => {
			if (selectedProject.value && task.project !== selectedProject.value) return false
			if (selectedLabel.value && !task.labels?.includes(selectedLabel.value)) return false
			if (selectedPriority.value && task.priority !== selectedPriority.value) return false
			if (selectedGroup.value && task.group !== selectedGroup.value) return false

			// Employee filter (PTB admins only)
			if (isPtbAdmin && selectedEmployee.value) {
				const isCreator = task.created_by === selectedEmployee.value
				const isAssigned = task.assigned_to?.includes(selectedEmployee.value)
				if (!isCreator && !isAssigned) return false
			}

			// Department filter (PTB admins only)
			if (isPtbAdmin && selectedDepartment.value) {
				const creatorInDept = task.created_by ? deptEmployeeIdSet.has(task.created_by) : false
				const assigneeInDept = task.assigned_to?.some((id) => deptEmployeeIdSet.has(id)) ?? false
				if (!creatorInDept && !assigneeInDept) return false
			}

			// Non-PTB admin: only show tasks user created, is assigned to, or is in their groups
			if (!isPtbAdmin) {
				if (!userEmpId) return false
				const isCreator = task.created_by === userEmpId
				const isAssigned = task.assigned_to?.includes(userEmpId)
				const isInUserGroup = task.group && userGroupIds.value.includes(task.group)
				if (!isCreator && !isAssigned && !isInUserGroup) return false
			}

			return true
		})

		if (selectedStatus.value) {
			const statusFiltered = filteredEvents.filter(
				(t) => (t.status || 'todo') === selectedStatus.value,
			)
			columnTasksMap.todo = selectedStatus.value === 'todo' ? statusFiltered : []
			columnTasksMap.in_progress = selectedStatus.value === 'in_progress' ? statusFiltered : []
			columnTasksMap.done = selectedStatus.value === 'done' ? statusFiltered : []
		} else {
			columnTasksMap.todo = filteredEvents.filter((t) => (t.status || 'todo') === 'todo')
			columnTasksMap.in_progress = filteredEvents.filter((t) => t.status === 'in_progress')
			columnTasksMap.done = filteredEvents.filter((t) => t.status === 'done')
		}
	}

	// ── Functions ──────────────────────────────────────────────────────
	function clearFilters() {
		selectedProject.value = null
		filterProjectSearch.value = ''
		if (authStore.isPtbAdmin) {
			selectedEmployee.value = null
			selectedDepartment.value = null
		}
		selectedStatus.value = null
		selectedLabel.value = null
		selectedPriority.value = null
		selectedGroup.value = null
	}

	function handleFilterProjectBlur() {
		setTimeout(() => {
			showFilterProjectDropdown.value = false
			filterProjectSearch.value = ''
		}, 150)
	}

	// ── Watchers ───────────────────────────────────────────────────────
	watch(
		[
			events,
			selectedProject,
			selectedEmployee,
			selectedDepartment,
			selectedStatus,
			selectedLabel,
			selectedPriority,
			userGroupIds,
		],
		() => updateColumnTasks(),
		{ immediate: true },
	)

	// Clear employee filter when department changes (if employee not in new department)
	watch(selectedDepartment, (newDept) => {
		if (newDept && selectedEmployee.value) {
			const employee = employeeStore.employees.find((e) => e.id === selectedEmployee.value)
			if (employee && employee.department !== newDept) {
				selectedEmployee.value = null
			}
		}
	})

	return {
		// Filter state
		selectedProject,
		selectedEmployee,
		selectedDepartment,
		selectedStatus,
		showFilters,
		selectedLabel,
		selectedPriority,
		selectedGroup,
		// Filter dropdown search
		filterProjectSearch,
		showFilterProjectDropdown,
		filterProjectDropdownRef,
		// Computeds
		currentUserEmployeeId,
		userGroupIds,
		sortedProjects,
		sortedEmployees,
		sortedDepartments,
		filteredEmployees,
		filteredFilterProjects,
		activeFiltersCount,
		// Column tasks
		columnTasksMap,
		updateColumnTasks,
		// Functions
		clearFilters,
		handleFilterProjectBlur,
	}
}
