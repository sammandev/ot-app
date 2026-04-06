import { type ComputedRef, computed, type Ref, ref } from 'vue'

import { extractApiError } from '@/utils/extractApiError'
import type { Employee } from '@/services/api/employee'
import { type TaskGroup, taskGroupAPI } from '@/services/api/task'

export function useKanbanGroups(
	taskGroups: Ref<TaskGroup[]>,
	sortedEmployees: ComputedRef<Employee[]>,
) {
	const showGroupListModal = ref(false)
	const groupModalTab = ref<'all' | 'create' | 'edit'>('all')
	const groupForm = ref({
		name: '',
		description: '',
		color: '#6366F1',
		members: [] as number[],
	})
	const groupMemberSearch = ref('')

	const editingGroup = ref<number | null>(null)
	const editGroupForm = ref({
		name: '',
		description: '',
		color: '#6366F1',
		members: [] as number[],
	})
	const syncingDepartments = ref(false)
	const groupActionError = ref<string | null>(null)

	// ── Computeds ──────────────────────────────────────────────────────
	const filteredGroupMembers = computed(() => {
		if (!groupMemberSearch.value) return sortedEmployees.value
		const query = groupMemberSearch.value.toLowerCase()
		return sortedEmployees.value.filter((e) => e.name.toLowerCase().includes(query))
	})

	function resetGroupForm() {
		groupForm.value = {
			name: '',
			description: '',
			color: '#6366F1',
			members: [],
		}
	}

	function openGroupListModal(tab: 'all' | 'create' | 'edit' = 'all') {
		groupActionError.value = null
		if (tab === 'create') {
			resetGroupForm()
		}
		if (tab !== 'edit') {
			editingGroup.value = null
		}
		groupModalTab.value = tab
		groupMemberSearch.value = ''
		showGroupListModal.value = true
	}

	function closeGroupListModal() {
		showGroupListModal.value = false
		groupModalTab.value = 'all'
		editingGroup.value = null
		groupActionError.value = null
		groupMemberSearch.value = ''
	}

	async function saveGroup() {
		groupActionError.value = null
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
			resetGroupForm()
			groupMemberSearch.value = ''
			groupModalTab.value = 'all'
		} catch (error) {
			groupActionError.value = extractApiError(error, 'Failed to create group')
			console.error('Failed to create group:', error)
		}
	}

	function startEditGroup(group: TaskGroup) {
		groupActionError.value = null
		editingGroup.value = group.id
		editGroupForm.value = {
			name: group.name,
			description: group.description || '',
			color: group.color || '#6366F1',
			members: [...(group.members || [])],
		}
		groupModalTab.value = 'edit'
		showGroupListModal.value = true
	}

	function cancelEditGroup() {
		editingGroup.value = null
		groupModalTab.value = 'all'
		groupMemberSearch.value = ''
	}

	async function saveEditGroup() {
		if (!editingGroup.value) return
		groupActionError.value = null
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
			groupActionError.value = extractApiError(error, 'Failed to update group')
			console.error('Failed to update group:', error)
		}
	}

	async function deleteGroup(groupId: number) {
		groupActionError.value = null
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
			groupActionError.value = extractApiError(error, 'Failed to delete group')
			console.error('Failed to delete group:', error)
		}
	}

	async function leaveGroup(groupId: number) {
		groupActionError.value = null
		try {
			const updatedGroup = await taskGroupAPI.leaveGroup(groupId)
			const index = taskGroups.value.findIndex((g) => g.id === groupId)
			if (index !== -1) {
				taskGroups.value[index] = updatedGroup
			}
		} catch (error) {
			groupActionError.value = extractApiError(error, 'Failed to leave group')
			console.error('Failed to leave group:', error)
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
		showGroupListModal,
		groupModalTab,
		groupForm,
		groupMemberSearch,
		openGroupListModal,
		closeGroupListModal,
		filteredGroupMembers,
		saveGroup,
		editingGroup,
		editGroupForm,
		syncingDepartments,
		groupActionError,
		startEditGroup,
		cancelEditGroup,
		saveEditGroup,
		deleteGroup,
		leaveGroup,
		syncDepartmentGroups,
	}
}
