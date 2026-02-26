/**
 * Comprehensive API Service
 * Centralized axios instance with interceptors and all backend endpoints
 */

import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000', 10)

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
	baseURL: API_BASE_URL,
	timeout: API_TIMEOUT,
	headers: {
		'Content-Type': 'application/json',
	},
	withCredentials: true, // Send httpOnly cookies with every request
})

// Request interceptor - no-op (httpOnly cookies are sent automatically)
apiClient.interceptors.request.use(
	(config: InternalAxiosRequestConfig) => config,
	(error) => {
		return Promise.reject(error)
	},
)

// Flag to prevent multiple simultaneous logout redirects
let isLoggingOut = false

// Response interceptor - Handle token refresh
apiClient.interceptors.response.use(
	(response) => response,
	async (error: AxiosError) => {
		if (!error.config) return Promise.reject(error)
		const originalRequest: InternalAxiosRequestConfig & {
			_retry?: boolean
		} = error.config

		// If 401 and not already retried, try to refresh token
		// Critical: Do not retry if the failed request was the refresh request itself
		const refreshUrl = '/auth/token/refresh/'
		if (
			error.response?.status === 401 &&
			!originalRequest._retry &&
			!originalRequest.url?.includes(refreshUrl)
		) {
			originalRequest._retry = true

			try {
				const authStore = useAuthStore()

				// Guard: If user is already null or logging out, don't attempt refresh
				if (!authStore.user || isLoggingOut) {
					return Promise.reject(error)
				}

				await authStore.refreshToken()

				// Retry original request (cookies are sent automatically)
				return apiClient(originalRequest)
			} catch (refreshError) {
				// Guard: Prevent multiple logout redirects
				if (isLoggingOut) {
					return Promise.reject(refreshError)
				}
				isLoggingOut = true

				// Refresh failed, logout user
				try {
					const authStore = useAuthStore()
					authStore.clearAuth()
				} catch {
					// Ignore errors during cleanup
				}

				// Redirect to login using Vue Router (SPA-friendly, no full page reload)
				if (window.location.pathname !== '/login') {
					setTimeout(() => {
						isLoggingOut = false
						router.push('/login')
					}, 100)
				} else {
					isLoggingOut = false
				}

				return Promise.reject(refreshError)
			}
		}

		return Promise.reject(error)
	},
)

// ============================================================================
// Type Definitions
// ============================================================================

export interface PaginatedResponse<T> {
	count: number
	next: string | null
	previous: string | null
	results: T[]
}

export interface Department {
	id: number
	code: string
	name: string
	is_enabled: boolean
	api_version?: string
	created_at?: string
	updated_at?: string
}

export interface Employee {
	id: number
	emp_id: string
	name: string
	department: number
	department_name?: string
	is_enabled: boolean
	exclude_from_reports: boolean
	api_version?: string
	created_at?: string
	updated_at?: string
}

export interface Project {
	id: number
	name: string
	is_enabled: boolean
	api_version?: string
	created_at?: string
	updated_at?: string
}

export interface OvertimeBreak {
	id?: number
	break_start: string
	break_end: string
	duration_minutes?: number
}

export interface OvertimeRequest {
	time_start: string
	id?: number
	employee: number
	employee_name?: string
	employee_id?: string
	employee_emp_id?: string
	department_code?: string
	project: number
	project_name?: string
	request_date: string
	time_in: string
	time_out: string
	breaks?: OvertimeBreak[]
	work_description?: string
	reason?: string
	detail?: string
	status?: 'pending' | 'approved' | 'rejected' | 'cancelled'
	rejection_reason?: string
	approver?: number
	approver_name?: string
	approved_at?: string
	total_duration_minutes?: number
	net_duration_minutes?: number
	total_hours?: number
	has_break?: boolean
	break_start?: string | null
	break_end?: string | null
	break_hours?: number | null
	is_weekend?: boolean
	is_holiday?: boolean
	created_at?: string
	updated_at?: string
}

export interface CalendarEvent {
	id?: number
	title: string
	start: string
	end: string
	all_day: boolean
	event_type: 'holiday' | 'leave' | 'meeting' | 'task'
	status?: 'todo' | 'in_progress' | 'done'
	description?: string
	location?: string
	color?: string
	priority?: 'low' | 'medium' | 'high' | 'urgent'
	labels?: string[]
	is_repeating?: boolean
	repeat_frequency?: 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | null
	parent_event?: number | null
	created_by?: number
	assigned_to?: number[]
	meeting_url?: string
	project?: number | null
	applied_by?: number | null
	agent?: number | null
	leave_type?: string
	employee?: number
	employee_name?: string
	project_name?: string
	overtime_request?: number
	// Task Group fields
	group?: number | null
	group_name?: string
	group_color?: string
	// Subtask progress fields
	subtask_count?: number
	subtask_completed?: number
	// Time tracking fields
	estimated_hours?: number | null
	actual_hours?: number
	created_at?: string
	updated_at?: string
}

// Task Board Advanced Features
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

export interface OvertimeRule {
	id: number
	max_hours_per_day: number
	max_hours_per_week: number
	max_hours_per_month: number
	min_break_duration_minutes: number
	max_continuous_hours: number
	effective_from: string
	effective_until?: string | null
	is_active: boolean
	description?: string
	created_at?: string
	updated_at?: string
}

export interface OvertimeRegulationContent {
	id: number
	title: string
	description: string
	category: string
	order: number
	is_active: boolean
	api_version?: string
	created_at?: string
	updated_at?: string
}

export interface OvertimeRegulationDocument {
	id: number
	title: string
	description?: string
	file: string
	file_size: number
	version: number
	is_active: boolean
	uploaded_by?: number
	uploaded_by_name?: string
	created_at: string
	updated_at: string
}

export interface LoginResponse {
	user: User
}

export interface User {
	id: number
	username: string
	email: string
	first_name: string
	last_name: string
	is_staff: boolean
	is_superuser: boolean
	is_active?: boolean
	is_ptb_admin?: boolean
	role?: 'developer' | 'superadmin' | 'user'
	worker_id?: string
	employee_id?: number
	department_id?: number
	date_joined?: string
	last_login?: string
	groups?: string[]
	permissions?: Record<string, boolean | string | number>
	menu_permissions?: string[] | Record<string, string[]>
	event_reminders_enabled?: boolean
	preferred_language?: string
	permission_updated_at?: string // Timestamp for force logout detection
}

export interface UserAccessControl {
	id: number
	username: string
	worker_id: string
	email: string
	first_name: string
	last_name: string
	is_ptb_admin: boolean
	is_superuser: boolean
	is_staff: boolean
	is_active: boolean
	role?: 'developer' | 'superadmin' | 'user'
	menu_permissions?: string[] | Record<string, string[]>
	event_reminders_enabled?: boolean
	permission_updated_at?: string // Timestamp for force logout detection
}

export interface UserAccessUpdate {
	is_ptb_admin?: boolean
	is_superuser?: boolean
	is_staff?: boolean
	is_active?: boolean
	role?: 'developer' | 'superadmin' | 'user'
	menu_permissions?: string[] | Record<string, string[]>
	event_reminders_enabled?: boolean
}

// Holiday Calendar Types
export interface Holiday {
	id: number
	title: string
	date: string // YYYY-MM-DD
	color: string // Hex color code
	description?: string
	is_recurring: boolean
	created_by?: number
	created_by_username?: string
	created_at?: string
	updated_at?: string
}

export interface EmployeeLeave {
	id: number
	employee: number
	employee_name: string
	employee_emp_id: string
	employee_dept_code?: string | null
	date: string // YYYY-MM-DD
	notes?: string
	agents?: number[] // Array of agent employee IDs
	agent_ids?: number[] // Read-only list of agent IDs
	agent_details?: Array<{
		id: number
		name: string
		emp_id: string
		dept_code?: string | null
	}> // Read-only agent details
	agent_names?: string // Custom agent names (free text)
	created_by?: number
	created_by_username?: string
	created_at?: string
	updated_at?: string
}

// Personal Notes Types (for Kanban Personal Board)
export interface PersonalNote {
	id: number
	owner: number
	owner_username?: string
	title: string
	content?: string
	color: string // Hex color code (default: #FFEB3B)
	is_pinned: boolean
	is_completed: boolean
	due_date?: string // YYYY-MM-DD
	order: number
	created_at?: string
	updated_at?: string
}

// Task Group Types (for organizing Kanban tasks)
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

// Task Attachment Types
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

// Task Reminder Types (alerts/reminders for tasks)
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

/**
 * Authentication API
 */
export const authAPI = {
	/**
	 * Login with local credentials
	 */
	async loginLocal(credentials: { username: string; password: string }) {
		const response = await apiClient.post<LoginResponse>('/auth/login/local/', credentials)
		return response.data
	},

	/**
	 * Login with external service
	 */
	async loginExternal(credentials: { username: string; password: string }) {
		const response = await apiClient.post<LoginResponse>('/auth/login/external/', credentials)
		return response.data
	},

	/**
	 * Refresh access token (cookie-based, no body needed)
	 */
	async refreshToken() {
		await apiClient.post('/auth/token/refresh/')
	},

	/**
	 * Logout
	 */
	async logout() {
		await apiClient.post('/auth/logout/')
	},

	/**
	 * Get current user info
	 */
	async getCurrentUser() {
		const response = await apiClient.get<User>('/auth/me/')
		return response.data
	},

	/**
	 * Update current user preferences
	 */
	async updatePreferences(prefs: {
		event_reminders_enabled?: boolean
		preferred_language?: string
	}) {
		const response = await apiClient.patch('/auth/me/', prefs)
		return response.data
	},

	/**
	 * Verify token validity and determine source
	 */
	async verifyToken(token: string) {
		const response = await apiClient.post<{
			valid: boolean
			source: 'local' | 'external' | 'unknown'
			details?: {
				user_id?: number
				username?: string
				exp?: number
				iat?: number
				error?: string
			}
		}>('/auth/token/verify/', { token })
		return response.data
	},

	/**
	 * Exchange an external access token for httpOnly session cookies
	 */
	async exchangeExternalToken(token: string) {
		const response = await apiClient.post<{ user: User }>('/auth/exchange-token/', { token })
		return response.data
	},
}

/**
 * Department API
 */
export const departmentAPI = {
	async list(params?: { page?: number; page_size?: number; search?: string }) {
		const response = await apiClient.get<PaginatedResponse<Department>>('/v1/departments/', {
			params,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Department>(`/v1/departments/${id}/`)
		return response.data
	},

	async create(payload: { code: string; name: string; is_enabled?: boolean }) {
		const response = await apiClient.post<Department>('/v1/departments/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<{ code: string; name: string; is_enabled: boolean }>) {
		const response = await apiClient.patch<Department>(`/v1/departments/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/departments/${id}/`)
	},

	async getEmployees(departmentId: number) {
		return apiClient.get<{ id: number; emp_id: string; name: string; is_enabled: boolean }[]>(
			`/v1/departments/${departmentId}/employees/`,
		)
	},

	async removeEmployee(departmentId: number, employeeId: number) {
		return apiClient.post(`/v1/departments/${departmentId}/remove_employee/`, {
			employee_id: employeeId,
		})
	},
}

/**
 * Employee API
 */
export const employeeAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		search?: string
		department_id?: number
	}) {
		const response = await apiClient.get<PaginatedResponse<Employee>>('/v1/employees/', {
			params,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Employee>(`/v1/employees/${id}/`)
		return response.data
	},

	async create(payload: {
		emp_id: string
		name: string
		department?: number | null
		is_enabled?: boolean
		exclude_from_reports?: boolean
	}) {
		const response = await apiClient.post<Employee>('/v1/employees/', payload)
		return response.data
	},

	async update(
		id: number,
		payload: Partial<{
			emp_id: string
			name: string
			department: number | null
			is_enabled: boolean
			exclude_from_reports: boolean
		}>,
	) {
		const response = await apiClient.patch<Employee>(`/v1/employees/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/employees/${id}/`)
	},

	async export(params?: { fields?: string }) {
		const response = await apiClient.get('/v1/employees/export/', {
			params,
			responseType: 'blob',
		})
		return response.data
	},

	async bulkImport(file: File, updateExisting = false) {
		const formData = new FormData()
		formData.append('file', file)
		formData.append('update_existing', updateExisting.toString())

		const response = await apiClient.post('/v1/employees/bulk_import/', formData, {
			headers: {
				'Content-Type': 'multipart/form-data',
			},
		})
		return response.data
	},
}

/**
 * Project API
 */
export const projectAPI = {
	async list(params?: { page?: number; page_size?: number; search?: string }) {
		const response = await apiClient.get<PaginatedResponse<Project>>('/v1/projects/', {
			params,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Project>(`/v1/projects/${id}/`)
		return response.data
	},

	async create(payload: { name: string; is_enabled?: boolean }) {
		const response = await apiClient.post<Project>('/v1/projects/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<{ name: string; is_enabled: boolean }>) {
		const response = await apiClient.patch<Project>(`/v1/projects/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/projects/${id}/`)
	},
}

/**
 * Overtime Request API
 */
export const overtimeAPI = {
	async list(
		params?: {
			page?: number
			page_size?: number
			employee?: number
			project?: number
			status?: string
			start_date?: string
			end_date?: string
			request_date?: string
			ordering?: string
			search?: string
			department_code?: string
		},
		requestOptions?: { signal?: AbortSignal },
	) {
		const response = await apiClient.get<PaginatedResponse<OvertimeRequest>>(
			'/v1/overtime-requests/',
			{
				params,
				signal: requestOptions?.signal,
			},
		)
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<OvertimeRequest>(`/v1/overtime-requests/${id}/`)
		return response.data
	},

	async create(payload: Omit<OvertimeRequest, 'id'>) {
		const response = await apiClient.post<OvertimeRequest>('/v1/overtime-requests/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<OvertimeRequest>) {
		const response = await apiClient.patch<OvertimeRequest>(`/v1/overtime-requests/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/overtime-requests/${id}/`)
	},

	async approve(id: number) {
		const response = await apiClient.post<OvertimeRequest>(`/v1/overtime-requests/${id}/approve/`)
		return response.data
	},

	async reject(id: number, reason: string) {
		const response = await apiClient.post<OvertimeRequest>(`/v1/overtime-requests/${id}/reject/`, {
			rejection_reason: reason,
		})
		return response.data
	},

	async cancel(id: number) {
		const response = await apiClient.post<OvertimeRequest>(`/v1/overtime-requests/${id}/cancel/`)
		return response.data
	},

	async export(params?: {
		employee?: number
		project?: number
		start_date?: string
		end_date?: string
		format?: 'csv' | 'excel'
	}) {
		const response = await apiClient.get('/v1/overtime-requests/export/', {
			params,
			responseType: 'blob',
		})
		return response.data
	},

	async summary(params?: {
		employee?: number
		project?: number
		start_date?: string
		end_date?: string
		group_by?: 'employee' | 'project' | 'date'
	}) {
		const response = await apiClient.get('/v1/overtime-requests/summary/', {
			params,
		})
		return response.data
	},

	async bulkUpdateStatus(ids: number[], status: 'approved' | 'rejected' | 'pending') {
		const response = await apiClient.post<{
			message: string
			updated_count: number
			status: string
		}>('/v1/overtime-requests/bulk-update-status/', { ids, status })
		return response.data
	},

	/** Server-side aggregated employee statistics */
	async employeeStats(params?: {
		start_date?: string
		end_date?: string
		status?: string
		employee?: number
	}) {
		const response = await apiClient.get<
			Array<{
				employee: number
				employee_name: string
				total_hours: string | number
				total_requests: number
				weekday_hours: string | number
				weekend_hours: string | number
				holiday_hours: string | number
				approved_hours: string | number
				pending_hours: string | number
			}>
		>('/v1/overtime-requests/employee_stats/', { params })
		return response.data
	},

	/** Server-side aggregated project statistics */
	async projectStats(params?: {
		start_date?: string
		end_date?: string
		status?: string
		project?: number
	}) {
		const response = await apiClient.get<
			Array<{
				project: number
				project_name: string
				total_hours: string | number
				total_requests: number
				unique_employees: number
			}>
		>('/v1/overtime-requests/project_stats/', { params })
		return response.data
	},

	/** Server-side summary statistics with optional previous-period comparison */
	async summaryStats(params?: {
		start_date?: string
		end_date?: string
		prev_start_date?: string
		prev_end_date?: string
	}) {
		const response = await apiClient.get<{
			total_hours: string | number | null
			total_requests: number
			unique_employees: number
			unique_projects: number
			weekday_hours: string | number | null
			weekend_hours: string | number | null
			holiday_hours: string | number | null
			approved_hours: string | number | null
			pending_hours: string | number | null
			rejected_hours: string | number | null
			previous?: {
				total_hours: string | number | null
				total_requests: number
				unique_employees: number
				unique_projects: number
				weekday_hours: string | number | null
				weekend_hours: string | number | null
				holiday_hours: string | number | null
				approved_hours: string | number | null
				pending_hours: string | number | null
				rejected_hours: string | number | null
			}
		}>('/v1/overtime-requests/summary_stats/', { params })
		return response.data
	},
}

/**
 * Calendar Event API
 */
export const calendarAPI = {
	async list(params?: {
		start?: string
		end?: string
		employee?: number
		project?: number
		event_type?: 'event' | 'task' | 'meeting' | 'leave' | 'holiday'
		my_events?: boolean
	}) {
		const response = await apiClient.get<CalendarEvent[] | PaginatedResponse<CalendarEvent>>(
			'/v1/calendar-events/',
			{ params },
		)
		// Normalize: backend may return paginated { results: [...] } or plain array
		const data = response.data
		if (Array.isArray(data)) return data
		return data.results ?? []
	},

	async get(id: number) {
		const response = await apiClient.get<CalendarEvent>(`/v1/calendar-events/${id}/`)
		return response.data
	},

	async create(payload: Omit<CalendarEvent, 'id'>) {
		const response = await apiClient.post<CalendarEvent>('/v1/calendar-events/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<CalendarEvent>) {
		const response = await apiClient.patch<CalendarEvent>(`/v1/calendar-events/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/calendar-events/${id}/`)
	},
}

/**
 * Holiday API - for the new Holiday Calendar page
 */
export const holidayAPI = {
	async list(
		params?: { year?: number; month?: number; start_date?: string; end_date?: string },
		requestOptions?: { signal?: AbortSignal },
	) {
		const response = await apiClient.get<Holiday[]>('/v1/holidays/', {
			params,
			signal: requestOptions?.signal,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Holiday>(`/v1/holidays/${id}/`)
		return response.data
	},

	async create(
		payload: Omit<Holiday, 'id' | 'created_at' | 'updated_at' | 'created_by' | 'created_by_username'>,
	) {
		const response = await apiClient.post<Holiday>('/v1/holidays/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<Holiday>) {
		const response = await apiClient.patch<Holiday>(`/v1/holidays/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/holidays/${id}/`)
	},
}

/**
 * Employee Leave API - for tracking employee time off
 */
export const employeeLeaveAPI = {
	async list(
		params?: {
			year?: number
			month?: number
			start_date?: string
			end_date?: string
			employee?: number
			date?: string
		},
		requestOptions?: { signal?: AbortSignal },
	) {
		const response = await apiClient.get<EmployeeLeave[]>('/v1/employee-leaves/', {
			params,
			signal: requestOptions?.signal,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<EmployeeLeave>(`/v1/employee-leaves/${id}/`)
		return response.data
	},

	async create(payload: {
		employee: number
		date: string
		notes?: string
		agents?: number[]
		agent_names?: string
	}) {
		const response = await apiClient.post<EmployeeLeave>('/v1/employee-leaves/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<EmployeeLeave>) {
		const response = await apiClient.patch<EmployeeLeave>(`/v1/employee-leaves/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/employee-leaves/${id}/`)
	},
}

/**
 * Personal Notes API - for Kanban personal sticky notes board
 */
export const personalNoteAPI = {
	async list() {
		const response = await apiClient.get<PersonalNote[]>('/v1/personal-notes/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<PersonalNote>(`/v1/personal-notes/${id}/`)
		return response.data
	},

	async create(payload: { title: string; content?: string; color?: string; due_date?: string }) {
		const response = await apiClient.post<PersonalNote>('/v1/personal-notes/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<PersonalNote>) {
		const response = await apiClient.patch<PersonalNote>(`/v1/personal-notes/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/personal-notes/${id}/`)
	},

	async reorder(order: number[]) {
		const response = await apiClient.post<{ status: string }>('/v1/personal-notes/reorder/', {
			order,
		})
		return response.data
	},

	async togglePin(id: number) {
		const response = await apiClient.post<PersonalNote>(`/v1/personal-notes/${id}/toggle_pin/`)
		return response.data
	},

	async toggleComplete(id: number) {
		const response = await apiClient.post<PersonalNote>(`/v1/personal-notes/${id}/toggle_complete/`)
		return response.data
	},
}

/**
 * Task Groups API - for organizing Kanban tasks into groups/folders
 */
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

/**
 * Task Attachments API - for file attachments on Kanban tasks
 */
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
		// Explicitly override the instance-level Content-Type: application/json default
		// so the browser sets multipart/form-data with the correct boundary.
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

/**
 * Task Reminders API - alerts and reminders for Kanban tasks
 */
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

/**
 * Overtime Regulation API
 */
export const regulationAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		is_active?: boolean
		category?: string
	}) {
		const response = await apiClient.get<PaginatedResponse<OvertimeRegulationContent>>(
			'/v1/overtime-regulations/',
			{
				params,
			},
		)
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<OvertimeRegulationContent>(`/v1/overtime-regulations/${id}/`)
		return response.data
	},

	async create(payload: Partial<OvertimeRegulationContent>) {
		const response = await apiClient.post<OvertimeRegulationContent>(
			'/v1/overtime-regulations/',
			payload,
		)
		return response.data
	},

	async update(id: number, payload: Partial<OvertimeRegulationContent>) {
		const response = await apiClient.patch<OvertimeRegulationContent>(
			`/v1/overtime-regulations/${id}/`,
			payload,
		)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/overtime-regulations/${id}/`)
	},

	async getActive() {
		const response = await apiClient.get<OvertimeRegulationContent>(
			'/v1/overtime-regulations/active/',
		)
		return response.data
	},
}

/**
 * Overtime Limit Configuration
 */
export interface OvertimeLimitConfig {
	id: number
	max_weekly_hours: number
	max_monthly_hours: number
	recommended_weekly_hours: number
	recommended_monthly_hours: number
	is_active: boolean
	created_at?: string
	updated_at?: string
}

export const overtimeLimitAPI = {
	async getActive(): Promise<OvertimeLimitConfig> {
		const response = await apiClient.get<OvertimeLimitConfig>('/v1/overtime-limits/active/')
		return response.data
	},
	async updateLimits(payload: Partial<OvertimeLimitConfig>): Promise<OvertimeLimitConfig> {
		const response = await apiClient.patch<OvertimeLimitConfig>(
			'/v1/overtime-limits/update_limits/',
			payload,
		)
		return response.data
	},
}

/**
 * Overtime Regulation Document API
 */
export const regulationDocumentAPI = {
	async list(params?: { is_active?: boolean; page_size?: number }) {
		const response = await apiClient.get<PaginatedResponse<OvertimeRegulationDocument>>(
			'/v1/regulation-documents/',
			{
				params,
			},
		)
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<OvertimeRegulationDocument>(
			`/v1/regulation-documents/${id}/`,
		)
		return response.data
	},

	async upload(formData: FormData) {
		const response = await apiClient.post<OvertimeRegulationDocument>(
			'/v1/regulation-documents/',
			formData,
			{
				headers: {
					'Content-Type': 'multipart/form-data',
				},
			},
		)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/regulation-documents/${id}/`)
	},
}

/**
 * Health Check API
 */
export const healthAPI = {
	async check() {
		const response = await apiClient.get('/health/')
		return response.data
	},

	async detailed() {
		const response = await apiClient.get('/health/detailed/')
		return response.data
	},
}

/**
 * User Access Control API (Super Admin only)
 */
export const userAccessAPI = {
	/**
	 * Get all users with access control settings
	 */
	async getAll() {
		const response = await apiClient.get<PaginatedResponse<UserAccessControl>>(
			'/v1/users/access-control/',
		)
		return response.data.results
	},

	/**
	 * Update user access permissions
	 */
	async update(userId: number, data: UserAccessUpdate) {
		const response = await apiClient.patch<UserAccessControl>(
			`/v1/users/access-control/${userId}/`,
			data,
		)
		return response.data
	},
}

/**
 * Notification API
 */
export interface Notification {
	id: number
	title: string
	message: string
	is_read: boolean
	is_archived?: boolean
	created_at: string
	time_ago: string
	recipient: number
	event: number | null
	event_type?: string // 'meeting', 'task', 'leave', 'holiday', 'purchase_request'
	computed_event_type?: string // Computed event type from linked event
	meeting_url?: string | null // URL for meetings
}

export interface PaginatedNotifications {
	count: number
	next: string | null
	previous: string | null
	total_pages: number
	current_page: number
	results: Notification[]
}

export interface UnreadCountResponse {
	unread_count: number
}

export const notificationAPI = {
	/**
	 * List notifications with pagination
	 * @param params - Query parameters
	 * @param params.page - Page number (default: 1)
	 * @param params.limit - Number of items per page (default: 20, max: 100)
	 * @param params.no_pagination - If true, returns all notifications without pagination
	 * @param params.include_archived - If true, includes archived notifications
	 */
	async list(
		params?: {
			page?: number
			limit?: number
			no_pagination?: boolean
			include_archived?: boolean
			archived_only?: boolean
		},
		requestOptions?: { signal?: AbortSignal },
	) {
		const response = await apiClient.get<PaginatedNotifications | Notification[]>(
			'/v1/notifications/',
			{
				params: {
					page: params?.page,
					limit: params?.limit,
					no_pagination: params?.no_pagination ? 'true' : undefined,
					include_archived: params?.include_archived ? 'true' : undefined,
					archived_only: params?.archived_only ? 'true' : undefined,
				},
				signal: requestOptions?.signal,
			},
		)
		return response.data
	},

	/**
	 * Get latest notifications for dropdown menu (without pagination)
	 * @param limit - Number of notifications to fetch (default: 10)
	 */
	async getLatest(limit: number = 10, requestOptions?: { signal?: AbortSignal }) {
		const response = await apiClient.get<Notification[]>('/v1/notifications/', {
			params: { no_pagination: 'true', limit },
			signal: requestOptions?.signal,
		})
		return response.data
	},

	/**
	 * Get unread notification count (cached on server)
	 */
	async getUnreadCount(requestOptions?: { signal?: AbortSignal }) {
		const response = await apiClient.get<UnreadCountResponse>('/v1/notifications/unread-count/', {
			signal: requestOptions?.signal,
		})
		return response.data
	},

	async markRead(id: number) {
		const response = await apiClient.post<{ status: string }>(`/v1/notifications/${id}/mark_read/`)
		return response.data
	},

	async markAllRead() {
		const response = await apiClient.post<{ status: string; count: number }>(
			'/v1/notifications/mark-all-read/',
		)
		return response.data
	},

	/**
	 * Archive old notifications (admin only)
	 * @param days - Archive notifications older than this many days (default: 90)
	 */
	async archiveOld(days: number = 90) {
		const response = await apiClient.post<{ status: string; count: number }>(
			'/v1/notifications/archive-old/',
			{ days },
		)
		return response.data
	},

	/**
	 * Archive a single notification (idempotent)
	 */
	async archiveNotification(id: number) {
		const response = await apiClient.post<{ status: string }>(`/v1/notifications/${id}/archive/`)
		return response.data
	},

	/**
	 * Unarchive a single notification (idempotent)
	 */
	async unarchiveNotification(id: number) {
		const response = await apiClient.post<{ status: string }>(`/v1/notifications/${id}/unarchive/`)
		return response.data
	},

	/**
	 * Delete a single notification
	 */
	async deleteNotification(id: number) {
		await apiClient.delete(`/v1/notifications/${id}/`)
	},
}

/**
 * Task Comments API
 */
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

/**
 * Task Activity API
 */
export const taskActivityAPI = {
	async list(taskId: number, limit = 50) {
		const response = await apiClient.get<TaskActivity[]>('/v1/task-activities/', {
			params: { task_id: taskId, limit },
		})
		return response.data
	},
}

/**
 * Task Subtasks/Checklist API
 */
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

/**
 * Task Time Logs/Timer API
 */
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

/**
 * Board Presence API
 */
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

/**
 * Purchase Request API
 */
export interface PurchaseRequest {
	id: number
	request_date: string | null
	owner: string | null
	owner_employee: number | null
	owner_employee_details?: {
		id: number
		emp_id: string
		name: string
	} | null
	doc_id: string | null
	part_no: string | null
	description_spec: string | null
	material_category: string | null
	purpose_desc: string | null
	qty: number
	plant: string | null
	project_code: string | null
	pr_type: string | null
	mrp_id: string | null
	purch_org: string | null
	sourcer_price: string | null
	pr_no: string | null
	remarks: string | null
	status: 'pending' | 'done' | 'canceled'
	created_at: string
	updated_at: string
}

export const purchaseRequestAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		search?: string
		status?: string
		start_date?: string
		end_date?: string
		ordering?: string
	}) {
		const response = await apiClient.get<PaginatedResponse<PurchaseRequest>>(
			'/v1/purchase-requests/',
			{ params },
		)
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<PurchaseRequest>(`/v1/purchase-requests/${id}/`)
		return response.data
	},

	async create(data: Partial<PurchaseRequest>) {
		const response = await apiClient.post<PurchaseRequest>('/v1/purchase-requests/', data)
		return response.data
	},

	async update(id: number, data: Partial<PurchaseRequest>) {
		const response = await apiClient.patch<PurchaseRequest>(`/v1/purchase-requests/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/purchase-requests/${id}/`)
	},

	async bulkDelete(ids: number[]) {
		const response = await apiClient.post<{ message: string; deleted: number }>(
			'/v1/purchase-requests/bulk_delete/',
			{ ids },
		)
		return response.data
	},

	async bulkUpdateStatus(ids: number[], status: string) {
		const response = await apiClient.post<{ message: string; updated: number }>(
			'/v1/purchase-requests/bulk_update_status/',
			{ ids, status },
		)
		return response.data
	},

	async importData(file: File) {
		const formData = new FormData()
		formData.append('file', file)
		const response = await apiClient.post<{
			message: string
			created?: number
			updated?: number
		}>('/v1/purchase-requests/import_data/', formData, {
			headers: { 'Content-Type': 'multipart/form-data' },
		})
		return response.data
	},
}

/**
 * Asset API
 */
export interface Asset {
	id: number
	asset_id: string
	company_code: string | null
	fixed_asset_id: string | null
	is_fixed_asset: boolean
	is_customs_control: boolean
	part_number: string | null
	group_3: string | null
	product_name: string | null
	spec: string | null
	quantity: number
	receive_date: string | null
	status: string | null
	department: number | null
	department_details?: {
		id: number
		code: string
		name: string
	} | null
	cost_center: string | null
	cost_center_name: string | null
	keeper_dept: string | null
	keeper_dept_name: string | null
	keeper: string | null
	keeper_name: string | null
	group_1: string | null
	group_2: string | null
	storage: string | null
	location_code: string | null
	storage_desc: string | null
	consign: string | null
	vendor: string | null
	pr_no: string | null
	pr_sequence: string | null
	po_no: string | null
	po_sequence: string | null
	dn_no: string | null
	dn_sequence: string | null
	dn_date: string | null
	application_number: string | null
	sequence: string | null
	import_number: string | null
	picking_no: string | null
	picking_sequence: string | null
	picking_year: string | null
	picking_date: string | null
	chinese_product_name: string | null
	hs_code: string | null
	declaration_number: string | null
	declaration_date: string | null
	control_end_date: string | null
	outsource_number: string | null
	price: number | null
	currency: string | null
	local_price: number | null
	price_level: string | null
	sn: string | null
	is_qualified: boolean
	itc_end_date: string | null
	elec_declaration_number: string | null
	national_inspection_certification: string | null
	note1: string | null
	note2: string | null
	note3: string | null
	note4: string | null
	note5: string | null
	note6: string | null
	note7: string | null
	note8: string | null
	note9: string | null
	note10: string | null
	created_at: string
	updated_at: string
}

export interface AssetSummary {
	id: number
	asset_id: string
	part_number: string | null
	product_name: string | null
	spec: string | null
	quantity: number
	status: string | null
	cost_center: string | null
	keeper_name: string | null
	keeper_dept: string | null
	department: number | null
	department_code: string | null
	receive_date: string | null
}

export interface DepartmentAssets {
	department_id: number | null
	department_code: string
	department_name: string
	asset_count: number
	assets: AssetSummary[]
}

export const assetAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		search?: string
		department?: number
		cost_center?: string
		status?: string
		ordering?: string
	}) {
		const response = await apiClient.get<PaginatedResponse<AssetSummary>>('/v1/assets/', { params })
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Asset>(`/v1/assets/${id}/`)
		return response.data
	},

	async create(data: Partial<Asset>) {
		const response = await apiClient.post<Asset>('/v1/assets/', data)
		return response.data
	},

	async update(id: number, data: Partial<Asset>) {
		const response = await apiClient.patch<Asset>(`/v1/assets/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/assets/${id}/`)
	},

	async bulkDelete(ids: number[]) {
		const response = await apiClient.post<{ message: string; deleted: number }>(
			'/v1/assets/bulk_delete/',
			{ ids },
		)
		return response.data
	},

	async bulkUpdateStatus(ids: number[], status: string) {
		const response = await apiClient.post<{ message: string; updated: number }>(
			'/v1/assets/bulk_update_status/',
			{ ids, status },
		)
		return response.data
	},

	async byDepartment(params?: { search?: string }) {
		const response = await apiClient.get<DepartmentAssets[]>('/v1/assets/by_department/', {
			params,
		})
		return response.data
	},

	async importData(file: File) {
		const formData = new FormData()
		formData.append('file', file)
		const response = await apiClient.post<{
			message: string
			created?: number
			updated?: number
		}>('/v1/assets/import_data/', formData, {
			headers: { 'Content-Type': 'multipart/form-data' },
		})
		return response.data
	},
}

// ============================================================================
// SMB Configuration API (Super Admin)
// ============================================================================

export interface SMBConfigData {
	id?: number
	name: string
	server: string
	share_name: string
	username: string
	new_password?: string
	domain: string
	port: number
	path_prefix: string
	is_active: boolean
	has_password?: boolean
	created_at?: string
	updated_at?: string
}

export const smbConfigAPI = {
	async list() {
		const response = await apiClient.get<{
			results: SMBConfigData[]
			count: number
		}>('/v1/smb-configs/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<SMBConfigData>(`/v1/smb-configs/${id}/`)
		return response.data
	},

	async create(data: Partial<SMBConfigData>) {
		const response = await apiClient.post<SMBConfigData>('/v1/smb-configs/', data)
		return response.data
	},

	async update(id: number, data: Partial<SMBConfigData>) {
		const response = await apiClient.patch<SMBConfigData>(`/v1/smb-configs/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/smb-configs/${id}/`)
	},

	async activate(id: number) {
		const response = await apiClient.post<SMBConfigData>(`/v1/smb-configs/${id}/activate/`)
		return response.data
	},

	async testConnection(id: number) {
		const response = await apiClient.post(`/v1/smb-configs/${id}/test/`)
		return response.data
	},
}

// ============================================================================
// User Reports API
// ============================================================================

export interface UserReportData {
	id?: number
	reporter?: number
	reporter_name?: string
	reporter_username?: string
	reporter_worker_id?: string
	reporter_email?: string
	report_type: string
	report_type_display?: string
	title: string
	description: string
	page_url?: string
	priority: string
	priority_display?: string
	status?: string
	status_display?: string
	admin_notes?: string
	resolved_in_version?: string
	created_at?: string
	updated_at?: string
}

export interface UserReportStats {
	total: number
	by_status: Record<string, number>
	by_type: Record<string, number>
}

export const userReportAPI = {
	async list(params?: Record<string, string>) {
		const response = await apiClient.get<{
			results: UserReportData[]
			count: number
		}>('/v1/user-reports/', { params })
		return response.data
	},

	async create(data: Partial<UserReportData>) {
		const response = await apiClient.post<UserReportData>('/v1/user-reports/', data)
		return response.data
	},

	async update(id: number, data: Partial<UserReportData>) {
		const response = await apiClient.patch<UserReportData>(`/v1/user-reports/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/user-reports/${id}/`)
	},

	async stats(): Promise<UserReportStats> {
		const response = await apiClient.get<UserReportStats>('/v1/user-reports/stats/')
		return response.data
	},
}

// ============================================================================
// Release Notes API
// ============================================================================

export interface ReleaseNoteData {
	id?: number
	version: string
	release_date: string
	status: string
	status_display?: string
	summary: string
	new_features: string[]
	improvements: string[]
	bug_fixes: string[]
	breaking_changes: string[]
	security: string[]
	known_issues: string[]
	deprecations: string[]
	contributors: string[]
	published: boolean
	created_by?: number
	created_by_name?: string
	created_at?: string
	updated_at?: string
}

export const releaseNoteAPI = {
	async list() {
		const response = await apiClient.get<{
			results: ReleaseNoteData[]
			count: number
		}>('/v1/release-notes/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<ReleaseNoteData>(`/v1/release-notes/${id}/`)
		return response.data
	},

	async create(data: Partial<ReleaseNoteData>) {
		const response = await apiClient.post<ReleaseNoteData>('/v1/release-notes/', data)
		return response.data
	},

	async update(id: number, data: Partial<ReleaseNoteData>) {
		const response = await apiClient.patch<ReleaseNoteData>(`/v1/release-notes/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/release-notes/${id}/`)
	},
}

export default apiClient
