/**
 * Core API Client
 * Axios instance with interceptors for auth refresh, retry, and request deduplication
 */

import axios, {
	type AxiosError,
	type AxiosInstance,
	type AxiosRequestConfig,
	type AxiosResponse,
	type InternalAxiosRequestConfig,
} from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
export const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000', 10)

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
	baseURL: API_BASE_URL,
	timeout: API_TIMEOUT,
	headers: {
		'Content-Type': 'application/json',
	},
	withCredentials: true, // Send httpOnly cookies with every request
})

// --- Request Deduplication for concurrent identical GET requests ---
const pendingGets = new Map<string, Promise<AxiosResponse>>()

const _originalGet = apiClient.get.bind(apiClient) as typeof apiClient.get
;(apiClient as { get: typeof apiClient.get }).get = function dedupedGet<
	T = unknown,
	R = AxiosResponse<T>,
	D = unknown,
>(url: string, config?: AxiosRequestConfig<D>): Promise<R> {
	// Don't dedup requests with custom abort signals (caller wants control)
	if (config?.signal) return _originalGet<T, R, D>(url, config)

	const key = `${url}:${JSON.stringify(config?.params ?? {})}`
	const existing = pendingGets.get(key)
	if (existing) return existing as Promise<R>

	const promise = _originalGet<T, R, D>(url, config).finally(() => pendingGets.delete(key))
	pendingGets.set(key, promise as Promise<AxiosResponse>)
	return promise
}

// Request interceptor - no-op (httpOnly cookies are sent automatically)
apiClient.interceptors.request.use(
	(config: InternalAxiosRequestConfig) => config,
	(error) => Promise.reject(error),
)

// --- Retry logic for transient server errors (5xx) and network failures ---
const MAX_RETRIES = 2
const RETRY_BASE_DELAY_MS = 1000

apiClient.interceptors.response.use(
	(response) => response,
	async (error: AxiosError) => {
		const config = error.config as InternalAxiosRequestConfig & { _retryCount?: number }
		if (!config) return Promise.reject(error)

		const status = error.response?.status
		const isServerError = status !== undefined && status >= 500
		const isNetworkError = !error.response && error.code !== 'ERR_CANCELED'
		const isSafeMethod = ['get', 'head', 'options'].includes(config.method?.toLowerCase() ?? '')
		const isRetryable = isSafeMethod && (isServerError || isNetworkError)

		if (isRetryable) {
			config._retryCount = (config._retryCount || 0) + 1
			if (config._retryCount <= MAX_RETRIES) {
				await new Promise((resolve) => setTimeout(resolve, RETRY_BASE_DELAY_MS * config._retryCount!))
				return apiClient(config)
			}
		}

		return Promise.reject(error)
	},
)

// --- Auth token refresh on 401 ---
let isLoggingOut = false
let logoutResetTimer: ReturnType<typeof setTimeout> | null = null

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

				// Safety: reset flag after 5 seconds to prevent getting permanently stuck
				if (logoutResetTimer) clearTimeout(logoutResetTimer)
				logoutResetTimer = setTimeout(() => {
					isLoggingOut = false
					logoutResetTimer = null
				}, 5000)

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
// Common Types
// ============================================================================

export interface PaginatedResponse<T> {
	count: number
	next: string | null
	previous: string | null
	results: T[]
}

export default apiClient
