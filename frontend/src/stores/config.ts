import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/services/api/client'

interface SystemConfig {
	app_name?: string
	app_acronym?: string
	version?: string
	build_date?: string
	tab_icon_url?: string | null
	event_reminders_disabled_globally?: boolean
	event_reminders_disabled_roles?: string[]
	event_reminders_disabled_users?: number[]
}

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

	// Cache TTL — config rarely changes
	const lastFetch = ref<number | null>(null)
	const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

	async function fetchConfig(force = false) {
		if (!force && lastFetch.value && Date.now() - lastFetch.value < CACHE_DURATION) {
			return
		}

		loading.value = true

		try {
			const response = await apiClient.get<SystemConfig>('/v1/system/config/')
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
			lastFetch.value = Date.now()
		} catch (err) {
			error.value = 'Failed to fetch system config'
			console.error('Failed to fetch system config:', err)
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
			const response = await apiClient.patch<SystemConfig>('/v1/system/config/', newConfig)

			const data = response.data
			if (data) {
				appName.value = data.app_name ?? appName.value
				appAcronym.value = data.app_acronym ?? appAcronym.value
				version.value = data.version ?? version.value
				buildDate.value = data.build_date ?? buildDate.value
				tabIconUrl.value = data.tab_icon_url || null
			}
			lastFetch.value = Date.now()
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
