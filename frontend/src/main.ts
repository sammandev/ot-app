import './assets/main.css'
import 'flatpickr/dist/flatpickr.css'

import { createApp } from 'vue'
import App from './App.vue'
import i18n from './i18n'
import router from './router'
import pinia from './stores'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

app.use(pinia)
app.use(i18n)

// Initialize auth store from localStorage/sessionStorage
const authStore = useAuthStore()
authStore.initFromStorage()

// Start WebSocket-based permission sync for real-time updates
// This ensures users see permission changes made by superadmin instantly
if (authStore.isAuthenticated) {
	authStore.startPermissionWebSocket()

	// Sync latest user data (role, permissions) from the backend on app mount.
	// This ensures role changes made while the user was offline or on page
	// refresh are picked up immediately, not only on tab visibility change.
	authStore.fetchUser().catch(() => {
		// Silent fail — stale localStorage data will be used until next sync
	})
}

// Auto-refresh user data when tab becomes visible (to get updated permissions)
// This is a backup for cases where WebSocket connection was interrupted
if (typeof document !== 'undefined') {
	document.addEventListener('visibilitychange', async () => {
		if (document.visibilityState === 'visible' && authStore.isAuthenticated) {
			try {
				await authStore.fetchUser()
			} catch {
				// Silent fail - user data couldn't be refreshed, but that's okay
			}
		}
	})
}

app.use(router)

app.mount('#app')
