/**
 * Task Board API — groups, comments, subtasks, time logs, attachments, reminders, presence
 */

import type { CalendarEvent } from './calendar'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface TaskComment {
	id: number
	task: number
	author: number
	author_id: number
	author_name: string
	content: string
	parent: number | null
	mentions: number[]
	is_edited: boolean
	edited_at: string | null
	reply_count: number
	replies: TaskComment[]
	time_ago: string
	created_at: string
	updated_at: string
}

export interface TaskSubtask {
	id: number
	task: number
	title: string
	is_completed: boolean
	completed_at: string | null
	completed_by: number | null
	completed_by_name: string | null
	order: number
	created_by: number
	created_by_name: string
	created_at: string
	updated_at: string
}

export interface TaskTimeLog {
	id: number
	task: number
	task_title: string
	employee: number
	employee_name: string
	description: string
	started_at: string
	ended_at: string | null
	duration_minutes: number
	duration_formatted: string
	is_running: boolean
	created_at: string
	updated_at: string
}

export interface TaskTimeSummary {
	task_id: number
	total_minutes: number
	total_hours: number
	estimated_hours: number
	log_count: number
}

export interface TaskActivity {
	id: number
	task: number
	actor: number
	actor_id: number
	actor_name: string
	action:
		| 'created'
		| 'updated'
		| 'status_changed'
		| 'priority_changed'
		| 'assigned'
		| 'unassigned'
		| 'label_added'
		| 'label_removed'
		| 'comment_added'
		| 'due_date_changed'
		| 'moved'
	action_display: string
	old_value: string | null
	new_value: string | null
	extra_data: Record<string, unknown>
	time_ago: string
	created_at: string
}

export interface BoardPresence {
	id: number
	user: number
	user_id: number
	user_name: string
	editing_task: number | null
	last_seen: string
	channel_name: string
}

// WebSocket message types
export interface BoardWebSocketMessage {
	type:
		| 'user_joined'
		| 'user_left'
		| 'task_editing'
		| 'task_updated'
		| 'task_created'
		| 'task_deleted'
		| 'task_moved'
		| 'current_viewers'
		| 'heartbeat'
		| 'connected'
		| 'auth_error'
	user_id?: number
	error?: string
	user_name?: string
	task_id?: number
	task_data?: CalendarEvent
	from_status?: string
	to_status?: string
	viewers?: { user_id: number; user_name: string; editing_task_id?: number }[]
	timestamp?: string
	updated_by?: string
	deleted_by?: string
	moved_by?: string
	created_by?: string
}

export interface TaskWebSocketMessage {
	type:
		| 'comment_added'
		| 'comment_updated'
		| 'comment_deleted'
		| 'user_typing'
		| 'current_editors'
		| 'connected'
		| 'auth_error'
	error?: string
	comment?: TaskComment
	comment_id?: number
	new_content?: string
	author_name?: string
	user_id?: number
	user_name?: string
	is_typing?: boolean
	editors?: { user_id: number; user_name: string }[]
	timestamp?: string
}

export interface TaskGroup {
	id: number
	name: string
	description?: string
	color: string // Hex color code (default: #6366F1)
	icon?: string
	created_by: number
	created_by_username?: string
	members: number[]
	member_names?: string[]
	is_private: boolean
	order: number
	task_count?: number
	is_department_group?: boolean
	department?: number | null
	department_name?: string | null
	created_at?: string
	updated_at?: string
}

export interface TaskAttachment {
	id: number
	task: number
	file: string // File URL
	file_url?: string // Full URL for display
	filename: string
	file_size: number
	file_type: string // MIME type
	uploaded_by?: number
	uploaded_by_name?: string
	description?: string
	uploaded_at?: string
}

export type ReminderType = '15min' | '30min' | '1hour' | '2hours' | '1day' | 'custom'

export interface TaskReminder {
	id: number
	task: number
	task_title?: string
	task_due?: string
	user: number
	reminder_type: ReminderType
	reminder_type_display?: string
	remind_at: string // ISO datetime
	message?: string
	is_triggered: boolean
	is_dismissed: boolean
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const taskGroupAPI = {
	async list() {
		const response = await apiClient.get<TaskGroup[]>('/v1/task-groups/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<TaskGroup>(`/v1/task-groups/${id}/`)
		return response.data
	},

	async create(payload: {
		name: string
		description?: string
		color?: string
		icon?: string
		is_private?: boolean
		member_ids?: number[]
	}) {
		const response = await apiClient.post<TaskGroup>('/v1/task-groups/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<TaskGroup>) {
		const response = await apiClient.patch<TaskGroup>(`/v1/task-groups/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/task-groups/${id}/`)
	},

	async addMember(id: number, employeeId: number) {
		const response = await apiClient.post<TaskGroup>(`/v1/task-groups/${id}/add_member/`, {
			employee_id: employeeId,
		})
		return response.data
	},

	async removeMember(id: number, employeeId: number) {
		const response = await apiClient.post<TaskGroup>(`/v1/task-groups/${id}/remove_member/`, {
			employee_id: employeeId,
		})
		return response.data
	},

	async reorder(order: number[]) {
		const response = await apiClient.post<{ status: string }>('/v1/task-groups/reorder/', { order })
		return response.data
	},

	async syncDepartments() {
		const response = await apiClient.post<{
			status: string
			created: number
			updated: number
		}>('/v1/task-groups/sync_departments/')
		return response.data
	},
}

export const taskAttachmentAPI = {
	async list(taskId?: number) {
		const params = taskId ? { task_id: taskId } : {}
		const response = await apiClient.get<TaskAttachment[]>('/v1/task-attachments/', { params })
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<TaskAttachment>(`/v1/task-attachments/${id}/`)
		return response.data
	},

	async upload(taskId: number, file: File, description?: string) {
		const formData = new FormData()
		formData.append('task', taskId.toString())
		formData.append('file', file)
		if (description) {
			formData.append('description', description)
		}
		const response = await apiClient.post<TaskAttachment>('/v1/task-attachments/', formData, {
			headers: { 'Content-Type': 'multipart/form-data' },
		})
		return response.data
	},

	async update(id: number, payload: { description?: string }) {
		const response = await apiClient.patch<TaskAttachment>(`/v1/task-attachments/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/task-attachments/${id}/`)
	},

	async byTask(taskId: number) {
		const response = await apiClient.get<TaskAttachment[]>('/v1/task-attachments/by_task/', {
			params: { task_id: taskId },
		})
		return response.data
	},
}

export const taskReminderAPI = {
	async list() {
		const response = await apiClient.get<TaskReminder[]>('/v1/task-reminders/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<TaskReminder>(`/v1/task-reminders/${id}/`)
		return response.data
	},

	async create(payload: {
		task: number
		reminder_type: ReminderType
		remind_at: string
		message?: string
	}) {
		const response = await apiClient.post<TaskReminder>('/v1/task-reminders/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<TaskReminder>) {
		const response = await apiClient.patch<TaskReminder>(`/v1/task-reminders/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/task-reminders/${id}/`)
	},

	async getPending() {
		const response = await apiClient.get<TaskReminder[]>('/v1/task-reminders/pending/')
		return response.data
	},

	async getDue() {
		const response = await apiClient.get<TaskReminder[]>('/v1/task-reminders/due/')
		return response.data
	},

	async trigger(id: number) {
		const response = await apiClient.post<TaskReminder>(`/v1/task-reminders/${id}/trigger/`)
		return response.data
	},

	async dismiss(id: number) {
		const response = await apiClient.post<TaskReminder>(`/v1/task-reminders/${id}/dismiss/`)
		return response.data
	},

	async byTask(taskId: number) {
		const response = await apiClient.get<TaskReminder[]>('/v1/task-reminders/by_task/', {
			params: { task_id: taskId },
		})
		return response.data
	},
}

export const taskCommentAPI = {
	async list(taskId: number) {
		const response = await apiClient.get<TaskComment[]>('/v1/task-comments/', {
			params: { task_id: taskId, top_level: true },
		})
		return response.data
	},

	async create(data: { task: number; content: string; parent?: number; mentions?: number[] }) {
		const response = await apiClient.post<TaskComment>('/v1/task-comments/', data)
		return response.data
	},

	async update(id: number, content: string, mentions?: number[]) {
		const response = await apiClient.patch<TaskComment>(`/v1/task-comments/${id}/`, {
			content,
			mentions,
		})
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/task-comments/${id}/`)
	},

	async getReplies(commentId: number) {
		const response = await apiClient.get<TaskComment[]>(`/v1/task-comments/${commentId}/replies/`)
		return response.data
	},
}

export const taskActivityAPI = {
	async list(taskId: number, limit = 50) {
		const response = await apiClient.get<TaskActivity[]>('/v1/task-activities/', {
			params: { task_id: taskId, limit },
		})
		return response.data
	},
}

export const taskSubtaskAPI = {
	async list(taskId: number) {
		const response = await apiClient.get<TaskSubtask[]>('/v1/task-subtasks/', {
			params: { task_id: taskId },
		})
		return response.data
	},

	async create(data: { task: number; title: string; order?: number }) {
		const response = await apiClient.post<TaskSubtask>('/v1/task-subtasks/', data)
		return response.data
	},

	async update(id: number, data: { title?: string; order?: number }) {
		const response = await apiClient.patch<TaskSubtask>(`/v1/task-subtasks/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/task-subtasks/${id}/`)
	},

	async toggle(id: number) {
		const response = await apiClient.post<TaskSubtask>(`/v1/task-subtasks/${id}/toggle/`)
		return response.data
	},

	async reorder(taskId: number, subtaskIds: number[]) {
		const response = await apiClient.post<TaskSubtask[]>('/v1/task-subtasks/reorder/', {
			task_id: taskId,
			subtask_ids: subtaskIds,
		})
		return response.data
	},
}

export const taskTimeLogAPI = {
	async list(taskId: number) {
		const response = await apiClient.get<TaskTimeLog[]>('/v1/task-time-logs/', {
			params: { task_id: taskId },
		})
		return response.data
	},

	async create(data: {
		task: number
		description?: string
		started_at?: string
		ended_at?: string
		duration_minutes?: number
	}) {
		const response = await apiClient.post<TaskTimeLog>('/v1/task-time-logs/', data)
		return response.data
	},

	async update(
		id: number,
		data: {
			description?: string
			ended_at?: string
			duration_minutes?: number
		},
	) {
		const response = await apiClient.patch<TaskTimeLog>(`/v1/task-time-logs/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/task-time-logs/${id}/`)
	},

	async startTimer(taskId: number, description?: string) {
		const response = await apiClient.post<TaskTimeLog>('/v1/task-time-logs/start_timer/', {
			task_id: taskId,
			description,
		})
		return response.data
	},

	async stopTimer(id: number) {
		const response = await apiClient.post<TaskTimeLog>(`/v1/task-time-logs/${id}/stop_timer/`)
		return response.data
	},

	async getActive() {
		const response = await apiClient.get<TaskTimeLog | null>('/v1/task-time-logs/active/')
		return response.data
	},

	async getSummary(taskId: number) {
		const response = await apiClient.get<TaskTimeSummary>('/v1/task-time-logs/summary/', {
			params: { task_id: taskId },
		})
		return response.data
	},
}

export const boardPresenceAPI = {
	async heartbeat(editingTaskId?: number) {
		const response = await apiClient.post<{
			status: string
			viewers: BoardPresence[]
		}>('/v1/board-presence/heartbeat/', { editing_task_id: editingTaskId })
		return response.data
	},

	async leave() {
		await apiClient.post('/v1/board-presence/leave/')
	},

	async list() {
		const response = await apiClient.get<BoardPresence[]>('/v1/board-presence/')
		return response.data
	},
}
