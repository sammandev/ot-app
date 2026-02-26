<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Page Header -->
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ t('pages.superAdmin.title') }}</h1>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        {{ t('pages.superAdmin.subtitle') }}
                    </p>
                </div>
            </div>

            <!-- Tabs -->
            <div class="border-b border-gray-200 dark:border-gray-700">
                <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                    <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
                        :class="[activeTab === tab.key ? 'border-brand-500 text-brand-600 dark:text-brand-400' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
                        {{ tab.label }}
                    </button>
                </nav>
            </div>

            <!-- Tab Panels -->
            <AccessControlTab v-show="activeTab === 'access'" v-model:users="users" />
            <SystemSettingsTab v-show="activeTab === 'settings'" ref="settingsTabRef" />
            <ActivityLogsTab v-show="activeTab === 'activity'" />
            <EventRemindersTab v-show="activeTab === 'reminders'" :users="users" ref="remindersTabRef" />
            <SmbConfigTab v-show="activeTab === 'smb'" ref="smbTabRef" />
            <UserReportsTab v-show="activeTab === 'reports'" ref="reportsTabRef" />

        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import AccessControlTab from '@/components/super-admin/AccessControlTab.vue'
import ActivityLogsTab from '@/components/super-admin/ActivityLogsTab.vue'
import type EventRemindersTab from '@/components/super-admin/EventRemindersTab.vue'
import type SmbConfigTab from '@/components/super-admin/SmbConfigTab.vue'
import type SystemSettingsTab from '@/components/super-admin/SystemSettingsTab.vue'
import type UserReportsTab from '@/components/super-admin/UserReportsTab.vue'
import type { UserAccessControl } from '@/services/api'
import { useConfigStore } from '@/stores/config'

const { t } = useI18n()
const configStore = useConfigStore()

const activeTab = ref(localStorage.getItem('superadmin_tab') || 'access')
const users = ref<UserAccessControl[]>([])

const settingsTabRef = ref<InstanceType<typeof SystemSettingsTab> | null>(null)
const remindersTabRef = ref<InstanceType<typeof EventRemindersTab> | null>(null)
const smbTabRef = ref<InstanceType<typeof SmbConfigTab> | null>(null)
const reportsTabRef = ref<InstanceType<typeof UserReportsTab> | null>(null)

const tabs = [
	{ key: 'access', label: 'Access Control' },
	{ key: 'settings', label: 'System Configuration' },
	{ key: 'activity', label: 'User Activity Logs' },
	{ key: 'reminders', label: 'Event Reminders' },
	{ key: 'smb', label: 'SMB Config' },
	{ key: 'reports', label: 'User Reports' },
]

onMounted(async () => {
	try {
		await configStore.fetchConfig()
		// Initialize child tabs that depend on config
		settingsTabRef.value?.initFromConfig()
		remindersTabRef.value?.initFromConfig()
	} catch (error) {
		console.error('Failed to load system config', error)
	}
})

watch(activeTab, (tab) => {
	localStorage.setItem('superadmin_tab', tab)
})
</script>
