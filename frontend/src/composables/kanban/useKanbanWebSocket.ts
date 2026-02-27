import type { Ref } from 'vue'

import type { CalendarEvent } from '@/services/api/calendar'
import type { BoardWebSocket } from '@/services/websocket'

export function useKanbanWebSocket(events: Ref<CalendarEvent[]>, boardWs: BoardWebSocket) {
	// ── WebSocket Setup ────────────────────────────────────────────────
	function setupWebSocket() {
		boardWs.connect()

		// Handle real-time task created
		boardWs.onTaskCreated = (task: CalendarEvent) => {
			if (task.event_type === 'task' && !events.value.find((e) => e.id === task.id)) {
				events.value = [...events.value, task]
			}
		}

		// Handle real-time task updated
		boardWs.onTaskUpdated = (task: CalendarEvent) => {
			const idx = events.value.findIndex((e) => e.id === task.id)
			if (idx !== -1) {
				const updated = [...events.value]
				updated[idx] = task
				events.value = updated
			}
		}

		// Handle real-time task deleted
		boardWs.onTaskDeleted = (taskId: number) => {
			events.value = events.value.filter((e) => e.id !== taskId)
		}

		// Handle real-time task moved
		boardWs.onTaskMoved = (taskId: number, _fromStatus: string, toStatus: string) => {
			const idx = events.value.findIndex((e) => e.id === taskId)
			if (idx !== -1) {
				const updated = [...events.value]
				updated[idx] = {
					...updated[idx]!,
					status: toStatus as 'todo' | 'in_progress' | 'done',
				}
				events.value = updated
			}
		}
	}

	// ── Presence Helpers ──────────────────────────────────────────────
	function isTaskBeingEdited(taskId: number | undefined): boolean {
		if (!taskId) return false
		return boardWs.viewers.value.some((v) => v.editing_task_id === taskId)
	}

	function getTaskEditorName(taskId: number | undefined): string {
		if (!taskId) return ''
		const editor = boardWs.viewers.value.find((v) => v.editing_task_id === taskId)
		return editor?.user_name?.split(' ')[0] || ''
	}

	function getTaskEditors(taskId: number | undefined): { user_id: number; user_name: string }[] {
		if (!taskId) return []
		return boardWs.viewers.value
			.filter((v) => v.editing_task_id === taskId)
			.map((v) => ({ user_id: v.user_id, user_name: v.user_name }))
	}

	function getTaskEditingIndicator(taskId: number | undefined): string {
		if (!taskId) return ''
		return isTaskBeingEdited(taskId) ? 'ring-2 ring-yellow-400 ring-offset-1' : ''
	}

	return {
		setupWebSocket,
		isTaskBeingEdited,
		getTaskEditorName,
		getTaskEditors,
		getTaskEditingIndicator,
	}
}
