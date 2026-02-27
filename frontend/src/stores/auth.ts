/**
 * Auth Store
 * Manages authentication state, user session, and tokens
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { type SupportedLocale, setLocale } from '@/i18n'
import { authAPI, type User } from '@/services/api/auth'
import {
	disconnectBoardWebSocket,
	disconnectPermissionWebSocket,
	usePermissionWebSocket,
} from '@/services/websocket'
import { getCookie } from '@/utils/cookies'
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

/**
 * Default permission policy for regular users (no explicit menu_permissions set).
 * 'all' = full CRUD, 'read' = read-only, absent = denied.
 */
const DEFAULT_PERMISSION_POLICY: Record<string, 'all' | 'read'> = {
	ot_form: 'all',
	overtime_form: 'all',
	ot_history: 'read',
	overtime_history: 'read',
	ot_summary: 'read',
	overtime_summary: 'read',
	projects: 'read',
	admin_projects: 'read',
	departments: 'read',
	admin_departments: 'read',
	calendar: 'all',
	kanban: 'all',
	purchasing: 'all',
	request_purchase: 'all',
	assets: 'all',
	report: 'all',
	release_notes: 'read',
	personal_notes: 'all',
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

type CookieStoreLike = {
	delete: (cookieNameOrOptions: string | { name: string; path?: string }) => Promise<void>
}

async function clearExternalAccessTokenCookie() {
	const store = (window as Window & { cookieStore?: CookieStoreLike }).cookieStore
	if (!store) {
		console.warn('[Auth] Cookie Store API unavailable; unable to clear external access_token cookie')
		return
	}

	await store.delete({ name: 'access_token', path: '/' })
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

			// Regular User Defaults — use declarative policy map
			const policy = DEFAULT_PERMISSION_POLICY[resource]
			if (!policy) return false
			return policy === 'all' || action === 'read'
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

			// Regular user defaults — use declarative policy map
			return !!DEFAULT_PERMISSION_POLICY[resource]
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

		// Quick local expiry check — avoid wasting a round-trip for clearly expired JWTs
		try {
			const payload = JSON.parse(atob(externalToken.split('.')[1] ?? '')) as { exp?: number }
			if (payload.exp && payload.exp * 1000 < Date.now()) {
				await clearExternalAccessTokenCookie()
				return false
			}
		} catch {
			// Token is not a valid JWT — let the server decide
		}

		loading.value = true
		error.value = null

		try {
			// Exchange the non-httpOnly external cookie for httpOnly session cookies
			const response = await authAPI.exchangeExternalToken(externalToken)

			user.value = response.user
			setToStorage('user', JSON.stringify(user.value))

			await clearExternalAccessTokenCookie()

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
			import('@/stores/notification')
				.then(({ useNotificationStore }) => {
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
				.catch((err: unknown) => {
					console.error('[Auth] Failed to load notification store:', err)
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
