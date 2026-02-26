import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/services/api'

export const useConfigStore = defineStore('config', () => {
	const appName = ref('OT Management System')
	const appAcronym = ref('OMS')
	const version = ref('2.0.0')
	const buildDate = ref('January 2026')
	const tabIconUrl = ref<string | null>(null)
	const loading = ref(false)
	const error = ref<string | null>(null)

	// Event Reminder Admin Controls
	const eventRemindersDisabledGlobally = ref(false)
	const eventRemindersDisabledRoles = ref<string[]>([])
	const eventRemindersDisabledUsers = ref<number[]>([])

	async function fetchConfig() {
		loading.value = true

		try {
			const response = await apiClient.get('/v1/system/config/')
			const data = response.data

			if (data) {
				appName.value = data.app_name || appName.value
				appAcronym.value = data.app_acronym || appAcronym.value
				version.value = data.version || version.value
				buildDate.value = data.build_date || buildDate.value
				tabIconUrl.value = data.tab_icon_url || null
				// Event reminder settings
				if (data.event_reminders_disabled_globally !== undefined) {
					eventRemindersDisabledGlobally.value = data.event_reminders_disabled_globally
				}
				if (data.event_reminders_disabled_roles) {
					eventRemindersDisabledRoles.value = data.event_reminders_disabled_roles
				}
				if (data.event_reminders_disabled_users) {
					eventRemindersDisabledUsers.value = data.event_reminders_disabled_users
				}
			}
		} catch (err) {
			console.error('Failed to fetch system config:', err)
			// Silently fail to defaults if unauthenticated or error
		} finally {
			loading.value = false
		}
	}

	async function updateConfig(newConfig: {
		app_name: string
		app_acronym: string
		version?: string
		build_date?: string
	}) {
		loading.value = true

		try {
			const response = await apiClient.patch('/v1/system/config/', newConfig)

			const data = response.data
			if (data) {
				appName.value = data.app_name
				appAcronym.value = data.app_acronym
				version.value = data.version
				buildDate.value = data.build_date
				tabIconUrl.value = data.tab_icon_url || null
			}
			return data
		} catch (err: unknown) {
			const axiosErr = err as { response?: { data?: { detail?: string } } }
			error.value = axiosErr.response?.data?.detail || 'Failed to update config'
			throw err
		} finally {
			loading.value = false
		}
	}

	return {
		appName,
		appAcronym,
		version,
		buildDate,
		tabIconUrl,
		eventRemindersDisabledGlobally,
		eventRemindersDisabledRoles,
		eventRemindersDisabledUsers,
		loading,
		error,
		fetchConfig,
		updateConfig,
	}
})
