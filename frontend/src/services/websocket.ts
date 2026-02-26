/**
 * WebSocket Service for Task Board Real-time Features
 *
 * Provides:
 * - Real-time board updates (task created/updated/deleted/moved)
 * - Presence indicators (who's viewing/editing)
 * - Live comments synchronization
 * - Real-time permission updates
 */

import { ref } from 'vue'
import type {
	BoardWebSocketMessage,
	CalendarEvent,
	TaskComment,
	TaskWebSocketMessage,
	User,
} from './api'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
// Remove /api suffix and convert absolute http(s) URL to ws(s),
// or derive from current browser origin when API_BASE is relative.
const WS_BASE = API_BASE.startsWith('http')
	? API_BASE.replace(/\/api\/?$/, '').replace(/^http/, 'ws')
	: `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`

export interface BoardViewer {
	user_id: number
	user_name: string
	editing_task_id?: number
}

export interface TaskEditor {
	user_id: number
	user_name: string
}

export interface PermissionWebSocketMessage {
	type: 'connected' | 'permission_update' | 'new_notification' | 'account_deactivated' | 'auth_error'
	user?: User
	unread_count?: number
	error?: string
}

/**
 * Permission WebSocket connection for real-time permission updates
 */
export class PermissionWebSocket {
	private socket: WebSocket | null = null
	private reconnectAttempts = 0
	private maxReconnectAttempts = 5
	private reconnectDelay = 3000
	private heartbeatInterval: ReturnType<typeof setInterval> | null = null

	// Reactive state
	public connected = ref(false)
	public lastError = ref<string | null>(null)

	// Event handlers
	public onPermissionUpdate: ((user: User) => void) | null = null
	public onAccountDeactivated: (() => void) | null = null
	public onNewNotification: ((data: Record<string, unknown>) => void) | null = null

	connect() {
		if (this.socket?.readyState === WebSocket.OPEN) {
			return
		}

		// Close any lingering CONNECTING socket before retry
		if (this.socket?.readyState === WebSocket.CONNECTING) {
			this.socket.close()
			this.socket = null
		}

		try {
			// Authentication is handled automatically via httpOnly cookies
			// sent during WebSocket handshake — no first-message auth needed.
			const wsUrl = `${WS_BASE}/ws/notifications/`

			this.socket = new WebSocket(wsUrl)

			this.socket.onopen = () => {
				this.connected.value = true
				this.lastError.value = null
				this.reconnectAttempts = 0

				this.startHeartbeat()
			}

			this.socket.onmessage = (event) => {
				try {
					const message: PermissionWebSocketMessage = JSON.parse(event.data)
					this.handleMessage(message)
				} catch (e) {
					console.error('[PermissionWS] Failed to parse message:', e)
				}
			}

			this.socket.onclose = (event) => {
				this.connected.value = false
				this.stopHeartbeat()

				// Try to reconnect if not a normal close (use exponential backoff)
				if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
					this.reconnectAttempts++
					const delay = this.reconnectDelay * 2 ** (this.reconnectAttempts - 1)
					setTimeout(() => this.connect(), delay)
				}
			}

			this.socket.onerror = () => {
				// Only log on first error to avoid console spam during reconnects
				if (this.reconnectAttempts === 0) {
					this.lastError.value = 'WebSocket connection error'
				}
			}
		} catch {
			this.lastError.value = 'Failed to establish WebSocket connection'
		}
	}

	disconnect() {
		this.stopHeartbeat()
		this.reconnectAttempts = this.maxReconnectAttempts // Prevent auto-reconnect
		if (this.socket) {
			this.socket.close(1000, 'User disconnected')
			this.socket = null
		}
		this.connected.value = false
	}

	private startHeartbeat() {
		this.heartbeatInterval = setInterval(() => {
			if (this.socket?.readyState === WebSocket.OPEN) {
				this.socket.send(JSON.stringify({ type: 'ping' }))
			}
		}, 30000)
	}

	private stopHeartbeat() {
		if (this.heartbeatInterval) {
			clearInterval(this.heartbeatInterval)
			this.heartbeatInterval = null
		}
	}

	private handleMessage(message: PermissionWebSocketMessage) {
		switch (message.type) {
			case 'connected':
				break

			case 'auth_error':
				this.lastError.value = 'WebSocket authentication failed'
				break

			case 'permission_update':
				if (message.user) {
					// Check if account was deactivated
					if (message.user.is_active === false) {
						console.warn('[PermissionWS] Account has been deactivated')
						this.onAccountDeactivated?.()
					} else {
						this.onPermissionUpdate?.(message.user)
					}
				}
				break

			case 'new_notification':
				this.onNewNotification?.(message as unknown as Record<string, unknown>)
				break
		}
	}
}

// Singleton instance for permission WebSocket
let permissionWsInstance: PermissionWebSocket | null = null

export function usePermissionWebSocket() {
	if (!permissionWsInstance) {
		permissionWsInstance = new PermissionWebSocket()
	}
	return permissionWsInstance
}

export function disconnectPermissionWebSocket() {
	if (permissionWsInstance) {
		permissionWsInstance.disconnect()
		permissionWsInstance = null
	}
}

/**
 * Board WebSocket connection for real-time updates
 */
export class BoardWebSocket {
	private socket: WebSocket | null = null
	private reconnectAttempts = 0
	private maxReconnectAttempts = 5
	private reconnectDelay = 1000
	private heartbeatInterval: ReturnType<typeof setInterval> | null = null
	private editingTaskId: number | null = null
	private visibilityHandler: (() => void) | null = null
	private wasConnectedBeforeHide = false

	// Reactive state
	public connected = ref(false)
	public viewers = ref<BoardViewer[]>([])
	public lastError = ref<string | null>(null)

	// Event handlers
	public onTaskCreated: ((task: CalendarEvent) => void) | null = null
	public onTaskUpdated: ((task: CalendarEvent, updatedBy: string) => void) | null = null
	public onTaskDeleted: ((taskId: number, deletedBy: string) => void) | null = null
	public onTaskMoved:
		| ((taskId: number, fromStatus: string, toStatus: string, movedBy: string) => void)
		| null = null
	public onViewerJoined: ((viewer: BoardViewer) => void) | null = null
	public onViewerLeft: ((userId: number) => void) | null = null
	public onTaskEditing: ((userId: number, userName: string, taskId: number) => void) | null = null

	connect() {
		if (this.socket?.readyState === WebSocket.OPEN) {
			return
		}

		try {
			// Authentication is handled automatically via httpOnly cookies
			// sent during WebSocket handshake — no first-message auth needed.
			const wsUrl = `${WS_BASE}/ws/board/`

			this.socket = new WebSocket(wsUrl)

			this.socket.onopen = () => {
				this.connected.value = true
				this.lastError.value = null
				this.reconnectAttempts = 0

				this.startHeartbeat()
				this.startVisibilityTracking()
			}

			this.socket.onmessage = (event) => {
				try {
					const message: BoardWebSocketMessage = JSON.parse(event.data)
					if (message.type === 'auth_error') {
						this.lastError.value = 'Board WebSocket authentication failed'
						return
					}
					this.handleMessage(message)
				} catch (e) {
					console.error('[BoardWS] Failed to parse message:', e)
				}
			}

			this.socket.onclose = (event) => {
				this.connected.value = false
				this.stopHeartbeat()

				// Try to reconnect if not a normal close
				if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
					this.reconnectAttempts++
					setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts)
				}
			}

			this.socket.onerror = () => {
				this.lastError.value = 'WebSocket connection error'
			}
		} catch {
			this.lastError.value = 'Failed to establish WebSocket connection'
		}
	}

	disconnect() {
		this.stopHeartbeat()
		this.stopVisibilityTracking()
		this.reconnectAttempts = this.maxReconnectAttempts // Prevent auto-reconnect
		if (this.socket) {
			this.socket.close(1000, 'User disconnected')
			this.socket = null
		}
		this.connected.value = false
		this.viewers.value = []
	}

	private startHeartbeat() {
		this.stopHeartbeat()
		this.heartbeatInterval = setInterval(() => {
			this.sendHeartbeat()
		}, 30000) // Every 30 seconds
	}

	private stopHeartbeat() {
		if (this.heartbeatInterval) {
			clearInterval(this.heartbeatInterval)
			this.heartbeatInterval = null
		}
	}

	private sendHeartbeat() {
		this.send({
			type: 'heartbeat',
			editing_task_id: this.editingTaskId,
		})
	}

	setEditingTask(taskId: number | null) {
		const wasEditing = this.editingTaskId
		this.editingTaskId = taskId
		// Send immediate heartbeat to update presence
		this.sendHeartbeat()
		// If stopped editing, also send a stop_editing message so others clear the indicator
		if (wasEditing && !taskId) {
			this.send({ type: 'stop_editing', task_id: wasEditing })
		}
	}

	private startVisibilityTracking() {
		this.stopVisibilityTracking()
		this.visibilityHandler = () => {
			if (document.hidden) {
				// Tab/page is hidden — stop heartbeat so presence times out and disconnect
				this.wasConnectedBeforeHide = this.socket?.readyState === WebSocket.OPEN
				this.stopHeartbeat()
				if (this.socket?.readyState === WebSocket.OPEN) {
					this.socket.close(1000, 'Tab hidden')
					this.socket = null
				}
				this.connected.value = false
			} else {
				// Tab/page is visible again — reconnect
				if (this.wasConnectedBeforeHide && !this.connected.value) {
					this.reconnectAttempts = 0
					this.connect()
				}
			}
		}
		document.addEventListener('visibilitychange', this.visibilityHandler)
	}

	private stopVisibilityTracking() {
		if (this.visibilityHandler) {
			document.removeEventListener('visibilitychange', this.visibilityHandler)
			this.visibilityHandler = null
		}
	}

	private handleMessage(message: BoardWebSocketMessage) {
		switch (message.type) {
			case 'current_viewers':
				this.viewers.value = message.viewers || []
				break

			case 'user_joined':
				if (message.user_id && message.user_name) {
					// Add to viewers if not already present
					if (!this.viewers.value.find((v) => v.user_id === message.user_id)) {
						this.viewers.value.push({
							user_id: message.user_id,
							user_name: message.user_name,
						})
					}
					this.onViewerJoined?.({
						user_id: message.user_id,
						user_name: message.user_name,
					})
				}
				break

			case 'user_left':
				if (message.user_id) {
					this.viewers.value = this.viewers.value.filter((v) => v.user_id !== message.user_id)
					this.onViewerLeft?.(message.user_id)
				}
				break

			case 'task_editing':
				if (message.user_id) {
					// Update viewer's editing status (task_id can be null when stopped editing)
					const viewer = this.viewers.value.find((v) => v.user_id === message.user_id)
					if (viewer) {
						viewer.editing_task_id = message.task_id || undefined
					}
					if (message.task_id) {
						this.onTaskEditing?.(message.user_id, message.user_name || '', message.task_id)
					}
				}
				break

			case 'task_created':
				if (message.task_data) {
					this.onTaskCreated?.(message.task_data)
				}
				break

			case 'task_updated':
				if (message.task_data) {
					this.onTaskUpdated?.(message.task_data, message.updated_by || 'Unknown')
				}
				break

			case 'task_deleted':
				if (message.task_id) {
					this.onTaskDeleted?.(message.task_id, message.deleted_by || 'Unknown')
				}
				break

			case 'task_moved':
				if (message.task_id && message.from_status && message.to_status) {
					this.onTaskMoved?.(
						message.task_id,
						message.from_status,
						message.to_status,
						message.moved_by || 'Unknown',
					)
				}
				break
		}
	}

	private send(data: Record<string, unknown>) {
		if (this.socket?.readyState === WebSocket.OPEN) {
			this.socket.send(JSON.stringify(data))
		}
	}

	// Broadcast methods - call these after successful API operations
	notifyTaskCreated(task: CalendarEvent) {
		this.send({ type: 'task_created', task_data: task })
	}

	notifyTaskUpdated(task: CalendarEvent) {
		this.send({ type: 'task_updated', task_id: task.id, task_data: task })
	}

	notifyTaskDeleted(taskId: number) {
		this.send({ type: 'task_deleted', task_id: taskId })
	}

	notifyTaskMoved(taskId: number, fromStatus: string, toStatus: string) {
		this.send({
			type: 'task_moved',
			task_id: taskId,
			from_status: fromStatus,
			to_status: toStatus,
		})
	}
}

/**
 * Task Detail WebSocket connection for comments and editing
 */
export class TaskWebSocket {
	private socket: WebSocket | null = null
	private taskId: number

	// Reactive state
	public connected = ref(false)
	public editors = ref<TaskEditor[]>([])
	public typingUsers = ref<TaskEditor[]>([])

	// Event handlers
	public onCommentAdded: ((comment: TaskComment) => void) | null = null
	public onCommentUpdated: ((commentId: number, newContent: string) => void) | null = null
	public onCommentDeleted: ((commentId: number) => void) | null = null
	public onUserTyping: ((user: TaskEditor, isTyping: boolean) => void) | null = null

	constructor(taskId: number) {
		this.taskId = taskId
	}

	connect() {
		if (this.socket?.readyState === WebSocket.OPEN) {
			return
		}

		try {
			// Authentication is handled automatically via httpOnly cookies
			// sent during WebSocket handshake — no first-message auth needed.
			const wsUrl = `${WS_BASE}/ws/board/task/${this.taskId}/`

			this.socket = new WebSocket(wsUrl)

			this.socket.onopen = () => {
				this.connected.value = true
			}

			this.socket.onmessage = (event) => {
				try {
					const message: TaskWebSocketMessage = JSON.parse(event.data)
					if (message.type === 'auth_error') {
						console.error('[TaskWS] Authentication failed')
						return
					}
					this.handleMessage(message)
				} catch (e) {
					console.error('[TaskWS] Failed to parse message:', e)
				}
			}

			this.socket.onclose = () => {
				this.connected.value = false
			}

			this.socket.onerror = () => {
				// Intentionally silent to avoid leaking token in URL
			}
		} catch {
			// Intentionally silent to avoid leaking token in URL
		}
	}

	disconnect() {
		if (this.socket) {
			this.socket.close(1000, 'User disconnected')
			this.socket = null
		}
		this.connected.value = false
		this.editors.value = []
		this.typingUsers.value = []
	}

	private handleMessage(message: TaskWebSocketMessage) {
		switch (message.type) {
			case 'current_editors':
				this.editors.value = message.editors || []
				break

			case 'comment_added':
				if (message.comment) {
					this.onCommentAdded?.(message.comment)
				}
				break

			case 'comment_updated':
				if (message.comment_id && message.new_content) {
					this.onCommentUpdated?.(message.comment_id, message.new_content)
				}
				break

			case 'comment_deleted':
				if (message.comment_id) {
					this.onCommentDeleted?.(message.comment_id)
				}
				break

			case 'user_typing':
				if (message.user_id && message.user_name) {
					if (message.is_typing) {
						if (!this.typingUsers.value.find((u) => u.user_id === message.user_id)) {
							this.typingUsers.value.push({
								user_id: message.user_id,
								user_name: message.user_name,
							})
						}
					} else {
						this.typingUsers.value = this.typingUsers.value.filter((u) => u.user_id !== message.user_id)
					}
					this.onUserTyping?.(
						{ user_id: message.user_id, user_name: message.user_name },
						message.is_typing || false,
					)
				}
				break
		}
	}

	private send(data: Record<string, unknown>) {
		if (this.socket?.readyState === WebSocket.OPEN) {
			this.socket.send(JSON.stringify(data))
		}
	}

	notifyCommentAdded(comment: TaskComment) {
		this.send({ type: 'comment_added', comment: { ...comment } })
	}

	notifyCommentUpdated(commentId: number, newContent: string) {
		this.send({
			type: 'comment_updated',
			comment_id: commentId,
			new_content: newContent,
		})
	}

	notifyCommentDeleted(commentId: number) {
		this.send({ type: 'comment_deleted', comment_id: commentId })
	}

	sendTyping(isTyping: boolean) {
		this.send({ type: 'typing', is_typing: isTyping })
	}
}

// Singleton instance for board connection
let boardWsInstance: BoardWebSocket | null = null

export function useBoardWebSocket() {
	if (!boardWsInstance) {
		boardWsInstance = new BoardWebSocket()
	}
	return boardWsInstance
}

export function disconnectBoardWebSocket() {
	if (boardWsInstance) {
		boardWsInstance.disconnect()
		boardWsInstance = null
	}
}

// Factory for task-specific WebSocket (caller is responsible for cleanup)
export function useTaskWebSocket(taskId: number) {
	const ws = new TaskWebSocket(taskId)
	return ws
}

/**
 * Calendar WebSocket message shape sent by the server
 */
export interface CalendarWebSocketMessage {
	type: 'calendar_update'
	action: 'created' | 'updated' | 'deleted'
	entity_type: 'holiday' | 'leave'
	data: Record<string, unknown>
	timestamp: string
}

/**
 * Calendar WebSocket connection for PTB Calendar real-time updates.
 * Receives holiday/leave create/update/delete broadcasts from the server.
 */
export class CalendarWebSocket {
	private socket: WebSocket | null = null
	private reconnectAttempts = 0
	private maxReconnectAttempts = 5
	private reconnectDelay = 2000
	private heartbeatInterval: ReturnType<typeof setInterval> | null = null

	// Reactive state
	public connected = ref(false)
	public lastError = ref<string | null>(null)

	// Event handlers — set by the consuming component
	public onCalendarUpdate:
		| ((
				action: 'created' | 'updated' | 'deleted',
				entityType: 'holiday' | 'leave',
				data: Record<string, unknown>,
		  ) => void)
		| null = null

	connect() {
		if (this.socket?.readyState === WebSocket.OPEN) return

		try {
			// Authentication is handled automatically via httpOnly cookies
			// sent during WebSocket handshake — no first-message auth needed.
			const wsUrl = `${WS_BASE}/ws/calendar/`
			this.socket = new WebSocket(wsUrl)

			this.socket.onopen = () => {
				this.connected.value = true
				this.lastError.value = null
				this.reconnectAttempts = 0

				this.startHeartbeat()
			}

			this.socket.onmessage = (event) => {
				try {
					const message = JSON.parse(event.data)
					if (message.type === 'auth_error') {
						this.lastError.value = 'Calendar WebSocket authentication failed'
						return
					}
					if (message.type === 'calendar_update') {
						this.onCalendarUpdate?.(message.action, message.entity_type, message.data)
					}
				} catch (e) {
					console.error('[CalendarWS] Failed to parse message:', e)
				}
			}

			this.socket.onclose = (event) => {
				this.connected.value = false
				this.stopHeartbeat()
				if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
					this.reconnectAttempts++
					setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts)
				}
			}

			this.socket.onerror = () => {
				this.lastError.value = 'Calendar WebSocket connection error'
			}
		} catch {
			this.lastError.value = 'Failed to establish Calendar WebSocket connection'
		}
	}

	disconnect() {
		this.stopHeartbeat()
		this.reconnectAttempts = this.maxReconnectAttempts // Prevent auto-reconnect
		if (this.socket) {
			this.socket.close(1000, 'User disconnected')
			this.socket = null
		}
		this.connected.value = false
	}

	private startHeartbeat() {
		this.stopHeartbeat()
		this.heartbeatInterval = setInterval(() => {
			if (this.socket?.readyState === WebSocket.OPEN) {
				this.socket.send(JSON.stringify({ type: 'heartbeat' }))
			}
		}, 30000)
	}

	private stopHeartbeat() {
		if (this.heartbeatInterval) {
			clearInterval(this.heartbeatInterval)
			this.heartbeatInterval = null
		}
	}
}

// Singleton instance for calendar connection
let calendarWsInstance: CalendarWebSocket | null = null

export function useCalendarWebSocket() {
	if (!calendarWsInstance) {
		calendarWsInstance = new CalendarWebSocket()
	}
	return calendarWsInstance
}

export function disconnectCalendarWebSocket() {
	if (calendarWsInstance) {
		calendarWsInstance.disconnect()
		calendarWsInstance = null
	}
}
