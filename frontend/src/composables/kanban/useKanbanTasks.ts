import { type ComputedRef, computed, type Ref, ref, watch } from 'vue'

import { type CalendarEvent, calendarAPI } from '@/services/api/calendar'
import type { Employee } from '@/services/api/employee'
import { type Project, projectAPI } from '@/services/api/project'
import { type TaskGroup, taskGroupAPI } from '@/services/api/task'
import type { BoardWebSocket } from '@/services/websocket'
import { useDepartmentStore } from '@/stores/department'
import { useEmployeeStore } from '@/stores/employee'

import type { TaskStatus } from './useKanbanHelpers'

// Module-scoped set to deduplicate "unknown employee" warnings (replaces window global)
const _loggedUnknownEmpIds = new Set<number>()

export function useKanbanTasks(
	events: Ref<CalendarEvent[]>,
	projects: Ref<Project[]>,
	taskGroups: Ref<TaskGroup[]>,
	boardWs: BoardWebSocket,
	sortedEmployees: ComputedRef<Employee[]>,
	sortedProjects: ComputedRef<Project[]>,
	selectedGroup: Ref<number | null>,
) {
	const employeeStore = useEmployeeStore()
	const departmentStore = useDepartmentStore()

	// ── Task State ─────────────────────────────────────────────────────
	const showModal = ref(false)
	const isEditing = ref(false)
	const editingId = ref<number | null>(null)
	const showDeleteModal = ref(false)
	const taskToDelete = ref<number | null>(null)
	const showTaskDetail = ref(false)
	const selectedTask = ref<CalendarEvent | null>(null)

	// ── Form ───────────────────────────────────────────────────────────
	const form = ref({
		title: '',
		description: '',
		start: new Date().toISOString().split('T')[0] as string,
		end: new Date().toISOString().split('T')[0] as string,
		end_time: '17:00',
		status: 'todo' as 'todo' | 'in_progress' | 'done',
		project: null as number | null,
		event_type: 'task' as 'task' | 'holiday' | 'leave' | 'meeting',
		priority: 'medium' as 'low' | 'medium' | 'high' | 'urgent',
		labels: [] as string[],
		assigned_to: [] as number[],
		group: null as number | null,
		estimated_hours: null as number | null,
	})

	// ── Modal Search State ─────────────────────────────────────────────
	const projectModalSearch = ref('')
	const assigneeModalSearch = ref('')
	const showProjectDropdown = ref(false)
	const projectDropdownFocused = ref(false)
	const projectDropdownHovered = ref(false)

	// ── Computeds ──────────────────────────────────────────────────────
	const filteredModalProjects = computed(() => {
		if (!projectModalSearch.value) return sortedProjects.value
		const query = projectModalSearch.value.toLowerCase()
		return sortedProjects.value.filter((p) => p.name.toLowerCase().includes(query))
	})

	const filteredModalEmployees = computed(() => {
		let employees = sortedEmployees.value

		// If a group is selected, only show group members
		if (form.value.group) {
			const group = taskGroups.value.find((g) => g.id === form.value.group)
			if (group) {
				const memberSet = new Set(group.members)
				employees = employees.filter((e) => memberSet.has(e.id))
			}
		}

		if (!assigneeModalSearch.value) return employees
		const query = assigneeModalSearch.value.toLowerCase()
		return employees.filter((e) => e.name.toLowerCase().includes(query))
	})

	// When the group changes, remove any assignees not in the new group
	watch(
		() => form.value.group,
		(newGroup) => {
			if (newGroup) {
				const group = taskGroups.value.find((g) => g.id === newGroup)
				if (group) {
					const memberSet = new Set(group.members)
					form.value.assigned_to = form.value.assigned_to.filter((id) => memberSet.has(id))
				}
			}
		},
	)

	// ── Project Dropdown Handlers ─────────────────────────────────────
	function handleProjectDropdownBlur() {
		setTimeout(() => {
			if (!projectDropdownHovered.value) {
				projectDropdownFocused.value = false
				showProjectDropdown.value = false
			}
		}, 150)
	}

	function closeProjectDropdown() {
		projectDropdownFocused.value = false
		projectDropdownHovered.value = false
		showProjectDropdown.value = false
		projectModalSearch.value = ''
	}

	// ── Fetch Functions ────────────────────────────────────────────────
	async function fetchTasks() {
		try {
			const response = await calendarAPI.list({ event_type: 'task', page_size: 500 })
			events.value = response
		} catch (e) {
			console.error('Failed to fetch tasks', e)
		}
	}

	async function fetchProjects() {
		try {
			const response = await projectAPI.list()
			projects.value = response.results
		} catch (e) {
			console.error('Failed to fetch projects', e)
		}
	}

	async function fetchTaskGroups() {
		try {
			const response = await taskGroupAPI.list()
			taskGroups.value = Array.isArray(response) ? response : []
		} catch (e) {
			console.error('Failed to fetch task groups', e)
			taskGroups.value = []
		}
	}

	// ── Task Detail Drawer ─────────────────────────────────────────────
	function openTaskDetail(task: CalendarEvent) {
		selectedTask.value = task
		showTaskDetail.value = true
		boardWs.setEditingTask(task.id || null)
	}

	function closeTaskDetail() {
		showTaskDetail.value = false
		selectedTask.value = null
		boardWs.setEditingTask(null)
	}

	// ── Task CRUD ──────────────────────────────────────────────────────
	function openCreateModal() {
		isEditing.value = false
		form.value = {
			title: '',
			description: '',
			start: new Date().toISOString().split('T')[0] as string,
			end: new Date().toISOString().split('T')[0] as string,
			end_time: '17:00',
			status: 'todo',
			project: null,
			event_type: 'task',
			priority: 'medium',
			labels: [],
			assigned_to: [],
			group: null,
			estimated_hours: null,
		}
		showModal.value = true
	}

	function editTask(task: CalendarEvent) {
		isEditing.value = true
		editingId.value = task.id!

		const endDate = new Date(task.end)
		const endTime = endDate.toTimeString().slice(0, 5)

		form.value = {
			title: task.title,
			description: task.description || '',
			start: task.start?.split('T')[0] || (new Date().toISOString().split('T')[0] as string),
			end: task.end?.split('T')[0] || (new Date().toISOString().split('T')[0] as string),
			end_time: endTime || '17:00',
			status: task.status || 'todo',
			project: task.project || null,
			event_type: 'task',
			priority: task.priority || 'medium',
			labels: task.labels || [],
			assigned_to: task.assigned_to || [],
			group: task.group || null,
			estimated_hours: task.estimated_hours || null,
		}
		showModal.value = true
	}

	function closeModal() {
		showModal.value = false
		editingId.value = null
		projectModalSearch.value = ''
		assigneeModalSearch.value = ''
		showProjectDropdown.value = false
		projectDropdownFocused.value = false
		projectDropdownHovered.value = false
	}

	async function saveTask() {
		try {
			const endDateTime = `${form.value.end}T${form.value.end_time || '17:00'}:00`

			const payload = {
				title: form.value.title,
				description: form.value.description,
				start: form.value.start!,
				end: endDateTime,
				status: form.value.status,
				project: form.value.project,
				event_type: form.value.event_type,
				priority: form.value.priority,
				labels: form.value.labels,
				assigned_to: form.value.assigned_to,
				group: form.value.group,
				estimated_hours: form.value.estimated_hours,
				all_day: false,
			}

			if (isEditing.value && editingId.value) {
				await calendarAPI.update(editingId.value, payload)
			} else {
				await calendarAPI.create(payload)
			}

			await fetchTasks()
			closeModal()
		} catch (e) {
			console.error('Failed to save task', e)
			alert('Failed to save task')
		}
	}

	function deleteTask(id: number) {
		taskToDelete.value = id
		showDeleteModal.value = true
	}

	async function confirmDeleteTask() {
		if (!taskToDelete.value) return
		try {
			const deletedId = taskToDelete.value
			await calendarAPI.delete(deletedId)
			events.value = events.value.filter((e) => e.id !== deletedId)
			cancelDelete()
		} catch (e) {
			console.error('Failed to delete task', e)
		}
	}

	function cancelDelete() {
		showDeleteModal.value = false
		taskToDelete.value = null
	}

	// ── Drag & Drop ───────────────────────────────────────────────────
	async function onDragChange(
		evt: { added?: { element: CalendarEvent } },
		targetStatus: TaskStatus,
	) {
		if (!evt.added) return
		const task = evt.added.element
		if (!task || task.status === targetStatus) return

		try {
			await calendarAPI.update(task.id!, { status: targetStatus })
			const sourceTask = events.value.find((e) => e.id === task.id)
			if (sourceTask) {
				sourceTask.status = targetStatus
			}
		} catch (e) {
			console.error('Failed to update task status', e)
			await fetchTasks()
		}
	}

	// ── Form Toggles ──────────────────────────────────────────────────
	function toggleLabel(labelName: string) {
		const idx = form.value.labels.indexOf(labelName)
		if (idx > -1) {
			form.value.labels.splice(idx, 1)
		} else {
			form.value.labels.push(labelName)
		}
	}

	function toggleAssignee(empId: number) {
		const idx = form.value.assigned_to.indexOf(empId)
		if (idx > -1) {
			form.value.assigned_to.splice(idx, 1)
		} else {
			form.value.assigned_to.push(empId)
		}
	}

	function selectAllAssignees() {
		form.value.assigned_to = filteredModalEmployees.value.map((emp) => emp.id)
	}

	function deselectAllAssignees() {
		form.value.assigned_to = []
	}

	// ── Employee Lookup Map (O(1) instead of find() per call) ─────────
	const employeeNameMap = computed(() => {
		const map = new Map<number, string>()
		for (const emp of employeeStore.employees) {
			map.set(emp.id, emp.name)
		}
		return map
	})

	// ── Helpers (store-dependent) ─────────────────────────────────────
	function getEmployeeName(empId: number): string {
		if (!empId) return 'Unknown'
		const name = employeeNameMap.value.get(empId)
		if (name) return name
		if (!_loggedUnknownEmpIds.has(empId)) {
			console.warn(
				`[KanbanBoard] Employee not found for ID: ${empId}. Available employees: ${employeeStore.employees.length}`,
			)
			_loggedUnknownEmpIds.add(empId)
		}
		return 'Unknown'
	}

	function getDepartmentCode(deptId: number): string {
		const dept = departmentStore.departments.find((d) => d.id === deptId)
		return dept?.code || '—'
	}

	function getSelectedGroupColor(): string {
		const group = taskGroups.value.find((g) => g.id === selectedGroup.value)
		return group?.color || '#6366F1'
	}

	return {
		// Task state
		showModal,
		isEditing,
		editingId,
		showDeleteModal,
		taskToDelete,
		showTaskDetail,
		selectedTask,
		// Form
		form,
		// Modal search
		projectModalSearch,
		assigneeModalSearch,
		showProjectDropdown,
		projectDropdownFocused,
		projectDropdownHovered,
		// Computeds
		filteredModalProjects,
		filteredModalEmployees,
		// Fetch
		fetchTasks,
		fetchProjects,
		fetchTaskGroups,
		// Task detail
		openTaskDetail,
		closeTaskDetail,
		// CRUD
		openCreateModal,
		editTask,
		closeModal,
		saveTask,
		deleteTask,
		confirmDeleteTask,
		cancelDelete,
		// Drag & drop
		onDragChange,
		// Form toggles
		toggleLabel,
		toggleAssignee,
		selectAllAssignees,
		deselectAllAssignees,
		// Project dropdown
		handleProjectDropdownBlur,
		closeProjectDropdown,
		// Helpers
		getEmployeeName,
		getDepartmentCode,
		getSelectedGroupColor,
	}
}
