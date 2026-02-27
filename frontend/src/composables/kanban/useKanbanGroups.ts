import { type ComputedRef, computed, type Ref, ref } from 'vue'

import type { Employee } from '@/services/api/employee'
import { type TaskGroup, taskGroupAPI } from '@/services/api/task'

export function useKanbanGroups(
	taskGroups: Ref<TaskGroup[]>,
	sortedEmployees: ComputedRef<Employee[]>,
) {
	// ── Group Modal State ─────────────────────────────────────────────
	const showGroupModal = ref(false)
	const groupForm = ref({
		name: '',
		description: '',
		color: '#6366F1',
		members: [] as number[],
	})
	const groupMemberSearch = ref('')

	// ── List Groups Modal State ────────────────────────────────────────
	const showListGroupsModal = ref(false)
	const listGroupsTab = ref<'all' | 'edit'>('all')
	const editingGroup = ref<number | null>(null)
	const editGroupForm = ref({
		name: '',
		description: '',
		color: '#6366F1',
		members: [] as number[],
	})
	const syncingDepartments = ref(false)

	// ── Computeds ──────────────────────────────────────────────────────
	const filteredGroupMembers = computed(() => {
		if (!groupMemberSearch.value) return sortedEmployees.value
		const query = groupMemberSearch.value.toLowerCase()
		return sortedEmployees.value.filter((e) => e.name.toLowerCase().includes(query))
	})

	// ── Create Group ───────────────────────────────────────────────────
	function openGroupModal() {
		groupForm.value = {
			name: '',
			description: '',
			color: '#6366F1',
			members: [],
		}
		groupMemberSearch.value = ''
		showGroupModal.value = true
	}

	function closeGroupModal() {
		showGroupModal.value = false
		groupMemberSearch.value = ''
	}

	function toggleGroupMember(empId: number) {
		const index = groupForm.value.members.indexOf(empId)
		if (index > -1) {
			groupForm.value.members.splice(index, 1)
		} else {
			groupForm.value.members.push(empId)
		}
	}

	function selectAllGroupMembers() {
		groupForm.value.members = sortedEmployees.value.map((e) => e.id)
	}

	function deselectAllGroupMembers() {
		groupForm.value.members = []
	}

	async function saveGroup() {
		try {
			const payload = {
				name: groupForm.value.name,
				description: groupForm.value.description || undefined,
				color: groupForm.value.color,
				member_ids: groupForm.value.members,
				is_private: false,
			}
			const newGroup = await taskGroupAPI.create(payload)
			if (!Array.isArray(taskGroups.value)) {
				taskGroups.value = []
			}
			taskGroups.value.push(newGroup)
			closeGroupModal()
		} catch (error) {
			console.error('Failed to create group:', error)
		}
	}

	// ── List Groups Modal ─────────────────────────────────────────────
	function openListGroupsModal() {
		listGroupsTab.value = 'all'
		editingGroup.value = null
		groupMemberSearch.value = ''
		showListGroupsModal.value = true
	}

	function closeListGroupsModal() {
		showListGroupsModal.value = false
		editingGroup.value = null
		listGroupsTab.value = 'all'
		groupMemberSearch.value = ''
	}

	// ── Edit Group ─────────────────────────────────────────────────────
	function startEditGroup(group: TaskGroup) {
		editingGroup.value = group.id
		editGroupForm.value = {
			name: group.name,
			description: group.description || '',
			color: group.color || '#6366F1',
			members: [...(group.members || [])],
		}
		listGroupsTab.value = 'edit'
	}

	function cancelEditGroup() {
		editingGroup.value = null
		listGroupsTab.value = 'all'
		groupMemberSearch.value = ''
	}

	function toggleEditGroupMember(empId: number) {
		const index = editGroupForm.value.members.indexOf(empId)
		if (index > -1) {
			editGroupForm.value.members.splice(index, 1)
		} else {
			editGroupForm.value.members.push(empId)
		}
	}

	async function saveEditGroup() {
		if (!editingGroup.value) return
		try {
			const payload = {
				name: editGroupForm.value.name,
				description: editGroupForm.value.description || undefined,
				color: editGroupForm.value.color,
				member_ids: editGroupForm.value.members,
			}
			const updatedGroup = await taskGroupAPI.update(editingGroup.value, payload)

			const index = taskGroups.value.findIndex((g) => g.id === editingGroup.value)
			if (index !== -1) {
				taskGroups.value[index] = updatedGroup
			}

			cancelEditGroup()
		} catch (error) {
			console.error('Failed to update group:', error)
		}
	}

	async function deleteGroup(groupId: number) {
		if (
			!confirm('Are you sure you want to delete this group? Tasks in this group will be unassigned.')
		)
			return
		try {
			await taskGroupAPI.delete(groupId)
			taskGroups.value = taskGroups.value.filter((g) => g.id !== groupId)

			if (editingGroup.value === groupId) {
				cancelEditGroup()
			}
		} catch (error) {
			console.error('Failed to delete group:', error)
		}
	}

	async function syncDepartmentGroups() {
		syncingDepartments.value = true
		try {
			const result = await taskGroupAPI.syncDepartments()
			// Refresh groups list (caller should call fetchTaskGroups after)
			const response = await taskGroupAPI.list()
			taskGroups.value = Array.isArray(response) ? response : []
			alert(`Department groups synced!\nCreated: ${result.created}\nUpdated: ${result.updated}`)
		} catch (error) {
			console.error('Failed to sync department groups:', error)
			alert('Failed to sync department groups. Please try again.')
		} finally {
			syncingDepartments.value = false
		}
	}

	return {
		// Create group
		showGroupModal,
		groupForm,
		groupMemberSearch,
		openGroupModal,
		closeGroupModal,
		filteredGroupMembers,
		toggleGroupMember,
		selectAllGroupMembers,
		deselectAllGroupMembers,
		saveGroup,
		// List groups
		showListGroupsModal,
		listGroupsTab,
		editingGroup,
		editGroupForm,
		syncingDepartments,
		openListGroupsModal,
		closeListGroupsModal,
		// Edit group
		startEditGroup,
		cancelEditGroup,
		toggleEditGroupMember,
		saveEditGroup,
		deleteGroup,
		syncDepartmentGroups,
	}
}
