<template>
    <div class="space-y-6">
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center gap-4 border-b border-gray-200 px-6 py-5 dark:border-gray-800">
                <div class="rounded-xl bg-amber-100 p-3 dark:bg-amber-500/20">
                    <svg class="h-6 w-6 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Event Reminder Controls</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Manage event reminder settings for all
                        users</p>
                </div>
            </div>

            <div class="p-6 space-y-6">
                <!-- Global Toggle -->
                <div
                    class="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                    <div>
                        <h4 class="font-medium text-gray-900 dark:text-white">Disable Reminders Globally</h4>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Turn off event reminders for all
                            users system-wide</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" v-model="reminderSettings.disabled_globally"
                            class="sr-only peer">
                        <div
                            class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-brand-300 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-transform dark:border-gray-600 peer-checked:bg-red-500">
                        </div>
                    </label>
                </div>

                <!-- Disable by Role -->
                <div
                    class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                    <h4 class="font-medium text-gray-900 dark:text-white mb-3">Disable by Role</h4>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">Select roles that should NOT receive
                        event reminders</p>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                        <label v-for="role in availableRoles" :key="role.key"
                            class="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox" :value="role.key"
                                v-model="reminderSettings.disabled_roles"
                                class="rounded border-gray-300 text-brand-600 focus:ring-brand-500">
                            <span class="text-sm text-gray-700 dark:text-gray-300">{{ role.label }}</span>
                        </label>
                    </div>
                </div>

                <!-- Disable by Specific Users -->
                <div
                    class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                    <h4 class="font-medium text-gray-900 dark:text-white mb-3">Disable for Specific Users</h4>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">Select individual users to disable
                        reminders for</p>
                    <div class="mb-3">
                        <input v-model="reminderUserSearch" type="text"
                            placeholder="Search users..."
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-brand-500 focus:border-transparent" />
                    </div>
                    <div class="max-h-48 overflow-y-auto space-y-1">
                        <label v-for="user in filteredReminderUsers" :key="user.id"
                            class="flex items-center gap-2 cursor-pointer p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
                            <input type="checkbox" :value="user.id"
                                v-model="reminderSettings.disabled_users"
                                class="rounded border-gray-300 text-brand-600 focus:ring-brand-500">
                            <span class="text-sm text-gray-700 dark:text-gray-300">{{ user.username }}</span>
                            <span v-if="user.worker_id"
                                class="text-xs text-gray-500">({{ user.worker_id }})</span>
                        </label>
                    </div>
                </div>

                <!-- Save Button -->
                <div class="flex justify-end gap-3 border-t border-gray-200 pt-4 dark:border-gray-800">
                    <button @click="resetReminderSettings"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-5 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                        Reset
                    </button>
                    <button @click="saveReminderSettings" :disabled="reminderSaving"
                        class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed">
                        {{ reminderSaving ? 'Saving...' : 'Save Reminder Settings' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useToast } from '@/composables/useToast'
import type { UserAccessControl } from '@/services/api'
import { apiClient } from '@/services/api'
import { useConfigStore } from '@/stores/config'

const props = defineProps<{
	users: UserAccessControl[]
}>()

const configStore = useConfigStore()
const { showToast } = useToast()

const reminderSettings = reactive({
	disabled_globally: false,
	disabled_roles: [] as string[],
	disabled_users: [] as number[],
})
const reminderSaving = ref(false)
const reminderUserSearch = ref('')

const availableRoles = [
	{ key: 'regular', label: 'Regular Users' },
	{ key: 'staff', label: 'Staff' },
	{ key: 'ptb_admin', label: 'PTB Admin' },
	{ key: 'superuser', label: 'Superuser' },
]

const filteredReminderUsers = computed(() => {
	const validUsers = props.users.filter((u) => u && u.id != null && u.is_active)
	if (!reminderUserSearch.value) return validUsers
	const q = reminderUserSearch.value.toLowerCase()
	return validUsers.filter(
		(u) => u.username?.toLowerCase().includes(q) || u.worker_id?.toLowerCase().includes(q),
	)
})

const resetReminderSettings = () => {
	reminderSettings.disabled_globally = configStore.eventRemindersDisabledGlobally
	reminderSettings.disabled_roles = [...configStore.eventRemindersDisabledRoles]
	reminderSettings.disabled_users = [...configStore.eventRemindersDisabledUsers]
}

const saveReminderSettings = async () => {
	reminderSaving.value = true
	try {
		await apiClient.patch('/v1/system/config/', {
			event_reminders_disabled_globally: reminderSettings.disabled_globally,
			event_reminders_disabled_roles: reminderSettings.disabled_roles,
			event_reminders_disabled_users: reminderSettings.disabled_users,
		})
		await configStore.fetchConfig()
		showToast('Reminder settings saved successfully', 'success')
	} catch (err) {
		console.error('Failed to save reminder settings:', err)
		showToast('Failed to save reminder settings', 'error')
	} finally {
		reminderSaving.value = false
	}
}

/** Initialize settings from config store once it's loaded */
const initFromConfig = () => {
	reminderSettings.disabled_globally = configStore.eventRemindersDisabledGlobally
	reminderSettings.disabled_roles = [...configStore.eventRemindersDisabledRoles]
	reminderSettings.disabled_users = [...configStore.eventRemindersDisabledUsers]
}

defineExpose({ initFromConfig })

onMounted(() => {
	initFromConfig()
})
</script>
