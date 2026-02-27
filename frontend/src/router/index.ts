import { createRouter, createWebHistory } from 'vue-router'
import { MAX_PAGE_VIEW_CACHE_SIZE } from '@/constants/ui'
import { apiClient } from '@/services/api/client'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	scrollBehavior(_to, _from, savedPosition) {
		return savedPosition || { left: 0, top: 0 }
	},
	routes: [
		{
			path: '/login',
			name: 'Login',
			component: () => import('../views/Auth/Login.vue'),
			meta: {
				title: 'Login',
				requiresAuth: false,
			},
		},
		{
			path: '/',
			redirect: '/ot/form',
		},
		{
			path: '/ot/form',
			name: 'OvertimeForm',
			component: () => import('../views/OvertimeForm.vue'),
			meta: {
				title: 'Overtime Form',
			},
		},
		{
			path: '/ot/history',
			name: 'OvertimeHistory',
			component: () => import('../views/OvertimeHistory.vue'),
			meta: {
				title: 'Overtime History',
			},
		},
		{
			path: '/notifications',
			name: 'Notifications',
			component: () => import('../views/Notifications.vue'),
			meta: {
				title: 'Notifications',
				requiresAuth: true,
			},
		},
		{
			path: '/ot/summary',
			name: 'OvertimeSummary',
			component: () => import('../views/OvertimeSummary.vue'),
			meta: {
				title: 'Overtime Summary',
				requiresAuth: true,
				requiresAdmin: true,
				resource: 'ot_summary',
			},
		},
		{
			path: '/ot/employee/:id/:slug',
			name: 'EmployeeOvertimeDetail',
			component: () => import('../views/EmployeeOvertimeDetail.vue'),
			meta: {
				title: 'Employee Overtime Detail',
			},
		},
		{
			path: '/ot/project/:id/:slug',
			name: 'ProjectOvertimeDetail',
			component: () => import('../views/ProjectOvertimeDetail.vue'),
			meta: {
				title: 'Project Overtime Detail',
			},
		},
		{
			path: '/calendar',
			name: 'OvertimeCalendar',
			component: () => import('../views/OvertimeCalendar.vue'),
			meta: {
				title: 'Calendar',
				resource: 'calendar',
			},
		},
		{
			path: '/ptb-calendar',
			name: 'PTBCalendar',
			component: () => import('../views/PtbCalendar.vue'),
			meta: {
				title: 'PTB Calendar',
				resource: 'calendar',
			},
		},
		{
			path: '/kanban',
			name: 'KanbanBoard',
			component: () => import('../views/KanbanBoard.vue'),
			meta: {
				title: 'Task Board',
				resource: 'kanban',
			},
		},
		{
			path: '/notes',
			name: 'PersonalNotes',
			component: () => import('../views/PersonalNotesBoard.vue'),
			meta: {
				title: 'Personal Notes',
				requiresAuth: true,
				resource: 'personal_notes',
			},
		},
		{
			path: '/admin/departments',
			name: 'AdminDepartment',
			component: () => import('../views/AdminDepartment.vue'),
			meta: {
				title: 'Departments',
				resource: 'departments',
			},
		},
		{
			path: '/admin/employees',
			name: 'AdminEmployee',
			component: () => import('../views/AdminEmployee.vue'),
			meta: {
				title: 'Employees',
				requiresAdmin: true,
				resource: 'employees',
			},
		},
		{
			path: '/admin/projects',
			name: 'AdminProject',
			component: () => import('../views/AdminProject.vue'),
			meta: {
				title: 'Projects',
				resource: 'projects',
			},
		},
		{
			path: '/admin/ot-regulations',
			name: 'AdminOvertimeRegulations',
			component: () => import('../views/AdminOvertimeRegulations.vue'),
			meta: {
				title: 'Overtime Regulations',
				requiresAdmin: true,
				resource: 'regulations',
			},
		},
		{
			path: '/purchasing',
			redirect: '/purchasing/list',
		},
		{
			path: '/purchasing/list',
			name: 'PurchasingList',
			component: () => import('../views/PurchasingList.vue'),
			meta: {
				title: 'Purchasing List',
				resource: 'purchasing',
			},
		},
		{
			path: '/purchasing/request',
			name: 'PurchasingRequest',
			component: () => import('../views/PurchasingRequest.vue'),
			meta: {
				title: 'Request Purchase',
				resource: 'purchasing',
			},
		},
		{
			path: '/asset-management',
			name: 'Assets',
			component: () => import('../views/Assets.vue'),
			meta: {
				title: 'Assets',
				resource: 'assets',
			},
		},
		{
			path: '/super-admin/access-control',
			name: 'SuperAdminAccessControl',
			component: () => import('../views/SuperAdminAccessControl.vue'),
			meta: {
				title: 'Access Control Management',
				requiresSuperAdmin: true,
			},
		},
		{
			path: '/profile',
			name: 'UserProfile',
			component: () => import('../views/UserProfile.vue'),
			meta: {
				title: 'User Profile',
				requiresAuth: true,
			},
		},
		{
			path: '/about',
			name: 'AboutPage',
			component: () => import('../views/AboutPage.vue'),
			meta: {
				title: 'About OMS',
				requiresAuth: true,
			},
		},
		{
			path: '/release-notes',
			name: 'ReleaseNotes',
			component: () => import('../views/ReleaseNotes.vue'),
			meta: {
				title: 'Release Notes',
				requiresAuth: true,
				resource: 'release_notes',
			},
		},
		{
			path: '/report',
			name: 'UserReport',
			component: () => import('../views/UserReport.vue'),
			meta: {
				title: 'Submit Report',
				requiresAuth: true,
				resource: 'report',
			},
		},
		{
			path: '/:pathMatch(.*)*',
			name: 'NotFound',
			component: () => import('../views/Errors/FourZeroFour.vue'),
			meta: {
				title: 'Not Found',
			},
		},
	],
})

router.beforeEach(async (to) => {
	const authStore = useAuthStore()
	const requiresAuth = to.meta.requiresAuth !== false // Default to true unless explicitly false
	const requiresSuperAdmin = to.meta.requiresSuperAdmin === true

	// Check for external token if not authenticated and not on login page
	const enableExternalAuth = import.meta.env.VITE_ENABLE_EXTERNAL_AUTH === 'true'

	if (!authStore.isAuthenticated && to.name !== 'Login' && enableExternalAuth) {
		const hasExternalToken = await authStore.checkExternalToken()

		// If no valid external token and not on login page, redirect to external login
		if (!hasExternalToken && requiresAuth) {
			// Redirect to external login page
			const externalAuthUrl =
				import.meta.env.VITE_EXTERNAL_AUTH_URL || 'http://172.18.220.56:8081/ptbot'
			window.location.href = externalAuthUrl
			return false
		}
	}

	// If route requires authentication and user is not authenticated
	if (requiresAuth && !authStore.isAuthenticated) {
		// Clear any stale auth data before redirecting to login
		authStore.clearAuth()

		// Redirect to login with return url
		return {
			name: 'Login',
			query: { redirect: to.fullPath },
		}
	}
	// If route requires super admin and user is not super admin
	if (requiresSuperAdmin && !authStore.isSuperAdmin) {
		// Redirect to home with access denied
		return {
			path: '/',
			query: { error: 'super_admin_required' },
		}
	}
	// If route requires admin and user is not PTB admin
	if (to.meta.requiresAdmin === true && !authStore.isPtbAdmin) {
		// Check if they have specific resource permission to override
		const resource = to.meta.resource as string | undefined
		if (resource && authStore.hasPermission(resource)) {
			return true
		}
		return {
			path: '/',
			query: { error: 'admin_required' },
		}
	}
	// If route has resource-based permission and user is not PTB admin
	// We check if they have specific resource permission to override
	if (to.meta.resource && !authStore.isPtbAdmin) {
		const resource = to.meta.resource as string

		// Permission data is kept fresh via WebSocket-based permission sync
		// and the visibilitychange listener in main.ts — no need to fetchUser() here.

		const hasAccess = authStore.hasPermission(resource)

		if (!hasAccess) {
			// Redirect to home with access denied
			return {
				path: '/',
				query: { error: 'access_denied' },
			}
		}
		return true
	}
	// If user is authenticated and trying to access auth pages
	if (
		authStore.isAuthenticated &&
		['Login', 'Signup', 'ResetPassword'].includes(to.name as string)
	) {
		// Redirect to home
		return { path: '/' }
	}
})

// Page view dedup: skip logging the same page within 30 seconds
const _pageViewCache = new Map<string, number>()
const PAGE_VIEW_COOLDOWN = 30_000
let _configLoaded = false

router.afterEach(async (to) => {
	const configStore = useConfigStore()
	if (!_configLoaded) {
		try {
			await configStore.fetchConfig()
			_configLoaded = true

			// Apply custom tab icon (favicon) if configured
			if (configStore.tabIconUrl) {
				let link = document.querySelector<HTMLLinkElement>("link[rel~='icon']")
				if (!link) {
					link = document.createElement('link')
					link.rel = 'icon'
					document.head.appendChild(link)
				}
				link.href = configStore.tabIconUrl
			}
		} catch {
			// Allow retry on next navigation
		}
	}

	const appName = configStore.appAcronym || 'OMS'
	document.title = to.meta.title ? `${to.meta.title} | ${appName}` : appName

	// Log page view for activity tracking (fire-and-forget, with dedup)
	const authStore = useAuthStore()
	if (authStore.isAuthenticated && to.name !== 'Login') {
		const now = Date.now()
		const lastLog = _pageViewCache.get(to.path)
		if (lastLog && now - lastLog < PAGE_VIEW_COOLDOWN) return
		_pageViewCache.set(to.path, now)

		// Evict stale entries to prevent unbounded growth in long sessions
		if (_pageViewCache.size > MAX_PAGE_VIEW_CACHE_SIZE) {
			for (const [key, ts] of _pageViewCache) {
				if (now - ts > PAGE_VIEW_COOLDOWN) _pageViewCache.delete(key)
			}
		}

		const token = authStore.isAuthenticated
		if (token) {
			apiClient
				.post('/v1/activity-logs/log-page-view/', {
					page: to.path,
					title: (to.meta.title as string) || '',
				})
				.catch(() => {
					/* silent */
				})
		}
	}
})

export default router
