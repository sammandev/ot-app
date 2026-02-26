/**
 * Auth Store
 * Manages authentication state, user session, and tokens
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { type SupportedLocale, setLocale } from '@/i18n'
import { authAPI, type User } from '@/services/api'
import {
	disconnectBoardWebSocket,
	disconnectPermissionWebSocket,
	usePermissionWebSocket,
} from '@/services/websocket'
import { extractApiError } from '@/utils/extractApiError'

interface LoginCredentials {
	username: string
	password: string
}

/**
 * Map sidebar menu keys to their permission key aliases.
 * Shared between hasPermission and hasAnyPermission to avoid duplication.
 */
const PERMISSION_KEY_ALIASES: Record<string, string[]> = {
	ot_form: ['ot_form', 'overtime_form'],
	overtime_form: ['ot_form', 'overtime_form'],
	ot_history: ['ot_history', 'overtime_history'],
	overtime_history: ['ot_history', 'overtime_history'],
	ot_summary: ['ot_summary', 'overtime_summary'],
	overtime_summary: ['ot_summary', 'overtime_summary'],
	employees: ['employees', 'admin_employees'],
	admin_employees: ['employees', 'admin_employees'],
	regulations: ['regulations', 'admin_regulations'],
	admin_regulations: ['regulations', 'admin_regulations'],
}

// Storage helper — persists the *user* object only (tokens are httpOnly cookies)
const STORAGE_KEY_REMEMBER = 'rememberMe'

function getStorage(): Storage {
	const rememberMe = localStorage.getItem(STORAGE_KEY_REMEMBER) === 'true'
	return rememberMe ? localStorage : sessionStorage
}

function setToStorage(key: string, value: string) {
	getStorage().setItem(key, value)
}

function getFromStorage(key: string): string | null {
	return getStorage().getItem(key)
}

function removeFromStorage(key: string) {
	localStorage.removeItem(key)
	sessionStorage.removeItem(key)
}

export const useAuthStore = defineStore('auth', () => {
	// State — tokens live exclusively in httpOnly cookies (not accessible to JS)
	const user = ref<User | null>(null)
	const loading = ref(false)
	const error = ref<string | null>(null)

	// Computed
	const isAuthenticated = computed(() => !!user.value)
	const isAdmin = computed(() => user.value?.is_staff || user.value?.is_superuser || false)
	const isPtbAdmin = computed(() => user.value?.is_ptb_admin || false)
	const isSuperAdmin = computed(() => {
		const role = user.value?.role
		return role === 'developer' || role === 'superadmin'
	})

	const isDeveloper = computed(() => {
		const role = user.value?.role
		return role === 'developer'
	})
	const fullName = computed(() =>
		user.value ? `${user.value.first_name} ${user.value.last_name}`.trim() : '',
	)

	const hasPermission = computed(() => {
		return (resource: string, action: 'create' | 'read' | 'update' | 'delete' = 'read') => {
			// Guard: if user is not loaded, deny access by default
			if (!user.value) return false

			// 1. Hardcoded super admins have full access
			if (isSuperAdmin.value) return true

			// Note: users with is_superuser flag from backend are NOT necessarily the hardcoded superadmin.
			// They might be just API superusers. If you want them to have full access too, keep this check.
			// But per instruction "is_superuser ... is not the same as superadmin user", we should rely on explicit permissions or defaults for them.
			// However, usually superuser implies full access. I will COMMENT OUT the generic is_superuser check to strict compliance with "Superadmin is hardcoded".
			// if (user.value?.is_superuser) return true

			const perms = user.value?.menu_permissions

			// Get all possible keys to check (include aliases)
			const keysToCheck = PERMISSION_KEY_ALIASES[resource] || [resource]

			// 2. Explicit Permissions Check (Dictionary)
			// If explicit permissions exist for this resource, they take precedence
			if (perms && typeof perms === 'object' && !Array.isArray(perms)) {
				for (const key of keysToCheck) {
					if ((perms as Record<string, string[]>)[key]) {
						const allowedActions = (perms as Record<string, string[]>)[key]
						if (Array.isArray(allowedActions) && allowedActions.includes(action)) {
							return true
						}
					}
				}
			}

			// 3. Fallback: Legacy List Format (Backwards Compatibility)
			if (Array.isArray(perms)) {
				for (const key of keysToCheck) {
					if (perms.includes(key)) {
						return true // Assume full access if in legacy list
					}
				}
			}

			// 4. Default Role-Based Access (If no explicit permission set)

			// PTB Admin: Full Access to everything (except Superadmin pages, which are guarded by isSuperAdmin above)
			if (isPtbAdmin.value) {
				return true
			}

			// Regular User Defaults
			switch (resource) {
				case 'ot_form':
				case 'overtime_form':
					// a) OT Form: create, read, update, delete (own records only - enforced by backend)
					return true

				case 'ot_history':
				case 'overtime_history':
					// b) OT History: read only (own records only - enforced by backend)
					return action === 'read'

				case 'ot_summary':
				case 'overtime_summary':
					// c) OT Summary: read only (own records only - enforced by backend)
					return action === 'read'

				case 'projects':
				case 'admin_projects':
					// d) Projects: read only
					return action === 'read'

				case 'departments':
				case 'admin_departments':
					// e) Departments: read only
					return action === 'read'

				case 'calendar':
					// f) Calendar: create, read, update, delete (own events only - enforced by backend)
					return true

				case 'kanban':
					// g) Task Board: create, read, update, delete (assigned tasks only - enforced by backend)
					return true

				case 'purchasing':
				case 'request_purchase':
					// h) Purchasing: create, read, update, delete
					return true

				case 'assets':
					// i) Assets: create, read, update, delete
					return true

				case 'report':
					// j) Submit a Report: create, read, update, delete (own reports only)
					return true

				case 'release_notes':
					// k) Release Notes: read only
					return action === 'read'

				case 'personal_notes':
					// l) Personal Notes: create, read, update, delete (own notes only)
					return true

				default:
					return false
			}
		}
	})

	// Check if user has any permission (create, read, update, or delete) for a resource
	// This is used for menu visibility - if they have ANY access, show the menu
	const hasAnyPermission = computed(() => {
		return (resource: string) => {
			// Guard: if user is not loaded, deny access by default
			if (!user.value) return false

			// Super admins have full access
			if (isSuperAdmin.value) return true

			const perms = user.value?.menu_permissions

			// Get all possible keys to check (include aliases)
			const keysToCheck = PERMISSION_KEY_ALIASES[resource] || [resource]

			// Check explicit permissions (dictionary format)
			if (perms && typeof perms === 'object' && !Array.isArray(perms)) {
				for (const key of keysToCheck) {
					if ((perms as Record<string, string[]>)[key]) {
						const allowedActions = (perms as Record<string, string[]>)[key]
						// Has access if any action is allowed
						if (Array.isArray(allowedActions) && allowedActions.length > 0) {
							return true
						}
					}
				}
			}

			// Legacy list format
			if (Array.isArray(perms)) {
				for (const key of keysToCheck) {
					if (perms.includes(key)) {
						return true
					}
				}
			}

			// PTB Admin has full access
			if (isPtbAdmin.value) {
				return true
			}

			// Regular user defaults - these menus are accessible to all users by default
			// Resources NOT listed here (admin_employees, admin_regulations, etc.)
			// require explicit permissions to be visible for regular users
			switch (resource) {
				case 'ot_form':
				case 'overtime_form':
				case 'calendar':
				case 'kanban':
				case 'purchasing':
				case 'request_purchase':
				case 'assets':
				case 'report':
				case 'personal_notes':
					return true

				case 'ot_history':
				case 'overtime_history':
				case 'ot_summary':
				case 'overtime_summary':
				case 'projects':
				case 'admin_projects':
				case 'departments':
				case 'admin_departments':
				case 'release_notes':
					return true // Has read access by default

				// Resources that require explicit permissions for regular users:
				// admin_employees, admin_regulations, super_admin_access
				// These will return false unless explicit permissions are granted above

				default:
					return false
			}
		}
	})

	// Actions
	function initFromStorage() {
		const storedUser = getFromStorage('user')

		if (storedUser) {
			try {
				user.value = JSON.parse(storedUser)
			} catch (err) {
				console.error('Failed to parse stored auth data:', err)
				clearAuth()
			}
		}
	}

	async function login(credentials: LoginCredentials, useExternal = true, rememberMe = false) {
		loading.value = true
		error.value = null

		try {
			// Store rememberMe preference FIRST (so storage helper uses correct storage)
			localStorage.setItem(STORAGE_KEY_REMEMBER, rememberMe ? 'true' : 'false')

			// Login — server sets httpOnly cookies; we only keep user data
			const response = useExternal
				? await authAPI.loginExternal(credentials)
				: await authAPI.loginLocal(credentials)

			user.value = response.user

			// Apply user's preferred language
			if (response.user.preferred_language) {
				setLocale(response.user.preferred_language as SupportedLocale)
			}

			// Persist user to storage for page-refresh detection
			setToStorage('user', JSON.stringify(user.value))

			return user.value
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Login failed')
			clearAuth()
			throw err
		} finally {
			loading.value = false
		}
	}

	async function logout() {
		loading.value = true
		error.value = null

		try {
			// Disconnect WebSockets
			disconnectPermissionWebSocket()
			disconnectBoardWebSocket()

			// Call logout endpoint to clear httpOnly cookies and server sessions
			try {
				await authAPI.logout()
			} catch {
				// Best effort — server may be unreachable
			}
		} catch (err) {
			console.error('Logout error:', err)
		} finally {
			clearAuth()
			loading.value = false
		}
	}

	async function refreshToken() {
		// Refresh token is in the httpOnly cookie, sent automatically
		if (!user.value) {
			throw new Error('No active session')
		}

		loading.value = true
		error.value = null

		try {
			await authAPI.refreshToken()
			// New access cookie is set by the server response
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Token refresh failed')
			clearAuth()
			throw err
		} finally {
			loading.value = false
		}
	}

	async function fetchUser() {
		loading.value = true
		error.value = null

		try {
			const userData = await authAPI.getCurrentUser()

			// Check if user is deactivated
			if (userData.is_active === false) {
				console.warn('[Auth] User has been deactivated, forcing logout')
				clearAuth()
				window.location.href = '/login?reason=account_deactivated'
				return null
			}

			// Check for permission changes - update local state without forcing logout
			const storedPermissionUpdatedAt = user.value?.permission_updated_at
			const newPermissionUpdatedAt = userData.permission_updated_at

			if (
				storedPermissionUpdatedAt &&
				newPermissionUpdatedAt &&
				storedPermissionUpdatedAt !== newPermissionUpdatedAt
			) {
				console.info('[Auth] Permissions updated by admin, refreshing local state')
			}

			// Update local user data (including new permissions)
			user.value = userData
			setToStorage('user', JSON.stringify(user.value))

			// Apply user's preferred language
			if (userData.preferred_language) {
				setLocale(userData.preferred_language as SupportedLocale)
			}

			return user.value
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to fetch user')
			throw err
		} finally {
			loading.value = false
		}
	}

	function clearAuth() {
		user.value = null
		// Clear persisted user from both storages
		removeFromStorage('user')
		// Clean up legacy token storage from previous versions
		removeFromStorage('tokens')
		// Don't remove rememberMe preference - keep it for next login
	}

	function setUser(userData: User) {
		user.value = userData
		setToStorage('user', JSON.stringify(userData))
	}

	/**
	 * Get cookie value by name
	 */
	function getCookie(name: string): string | null {
		const value = `; ${document.cookie}`
		const parts = value.split(`; ${name}=`)
		if (parts.length === 2) {
			return parts.pop()?.split(';').shift() || null
		}
		return null
	}

	/**
	 * Check for external access token in cookies and exchange it
	 * for httpOnly session cookies.
	 */
	async function checkExternalToken(): Promise<boolean> {
		const externalToken = getCookie('access_token')

		if (!externalToken) {
			return false
		}

		// Already authenticated
		if (user.value) {
			return true
		}

		loading.value = true
		error.value = null

		try {
			// Exchange the non-httpOnly external cookie for httpOnly session cookies
			const response = await authAPI.exchangeExternalToken(externalToken)

			user.value = response.user
			setToStorage('user', JSON.stringify(user.value))

			document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'

			return true
		} catch (err) {
			console.error('External token exchange failed:', err)
			return false
		} finally {
			loading.value = false
		}
	}

	function forceLogout(
		reason: 'permission_changed' | 'account_deactivated' | 'session_expired' = 'session_expired',
	) {
		console.warn(`[Auth] Force logout triggered: ${reason}`)
		disconnectPermissionWebSocket()
		disconnectBoardWebSocket()
		clearAuth()
		window.location.href = `/login?reason=${reason}`
	}

	// WebSocket-based permission sync and real-time notifications
	function startPermissionWebSocket() {
		const permissionWs = usePermissionWebSocket()

		// Handle permission updates from admin
		permissionWs.onPermissionUpdate = (updatedUser: User) => {
			console.info('[Auth] Received real-time permission update via WebSocket')
			user.value = updatedUser
			setToStorage('user', JSON.stringify(user.value))
		}

		// Handle account deactivation
		permissionWs.onAccountDeactivated = () => {
			console.warn('[Auth] Account deactivated via WebSocket')
			forceLogout('account_deactivated')
		}

		// Handle new notifications in real-time
		permissionWs.onNewNotification = (data: Record<string, unknown>) => {
			// Import notification store dynamically to avoid circular dependency
			import('@/stores/notification').then(({ useNotificationStore }) => {
				const notificationStore = useNotificationStore()
				notificationStore.addNotification({
					id: data.id as number,
					title: data.title as string,
					message: data.message as string,
					event_type: data.event_type as string,
					event_id: data.event_id as number | null,
					is_read: data.is_read as boolean,
					created_at: data.created_at as string,
				})
				console.info('[Auth] New notification received via WebSocket:', data.title)
			})
		}

		// Connect
		permissionWs.connect()
	}

	function stopPermissionWebSocket() {
		disconnectPermissionWebSocket()
		disconnectBoardWebSocket()
	}

	return {
		// State
		user,
		loading,
		error,

		// Computed
		isAuthenticated,
		isAdmin,
		isPtbAdmin,
		isSuperAdmin,
		isDeveloper,
		fullName,
		hasPermission,
		hasAnyPermission,

		// Actions
		initFromStorage,
		login,
		logout,
		refreshToken,
		fetchUser,
		clearAuth,
		setUser,
		checkExternalToken,
		forceLogout,
		startPermissionWebSocket,
		stopPermissionWebSocket,
	}
})
