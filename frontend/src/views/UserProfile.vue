<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-semibold text-brand-500">{{ t('pages.userProfile.category') }}</p>
          <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.userProfile.title') }}</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.userProfile.subtitle') }}</p>
        </div>
        <nav>
          <ol class="flex items-center gap-2 text-sm">
            <li><router-link
                class="font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                to="/">{{ t('common.home') }}</router-link></li>
            <li class="text-gray-400 dark:text-gray-500">/</li>
            <li class="font-medium text-brand-500">{{ t('pages.userProfile.title') }}</li>
          </ol>
        </nav>
      </div>

      <!-- Profile Card -->
      <div v-if="!user" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div class="flex items-center justify-center py-16">
          <div class="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent"></div>
          <span class="ml-3 text-gray-500 dark:text-gray-400">{{ t('common.loading') }}</span>
        </div>
      </div>
      <div v-else class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div class="flex flex-col gap-8 lg:flex-row lg:gap-12">
          <!-- Left: Avatar -->
          <div class="w-full lg:w-1/3">
            <div class="flex flex-col items-center justify-center gap-5">
              <div class="relative">
                <div
                  class="flex h-28 w-28 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-brand-400 text-4xl font-bold text-white shadow-lg ring-4 ring-brand-500/20">
                  {{ userInitials }}
                </div>
                <div
                  class="absolute bottom-1 right-1 h-5 w-5 rounded-full border-4 border-white bg-green-500 dark:border-gray-900">
                </div>
              </div>

              <div class="text-center">
                <h3 class="mb-2 text-xl font-bold text-gray-900 dark:text-white">
                  {{ displayName }}
                </h3>
                <span
                  class="inline-block rounded-full bg-brand-500/10 px-4 py-1.5 text-sm font-semibold text-brand-600 dark:text-brand-400">
                  {{ userTypeLabel }}
                </span>
              </div>
            </div>
          </div>

          <!-- Right: Tabbed Content -->
          <div class="w-full lg:w-2/3">
            <!-- Tab Navigation -->
            <div class="mb-6 border-b border-gray-200 dark:border-gray-700">
              <nav class="-mb-px flex gap-6" aria-label="Tabs">
                <button v-for="tab in tabs" :key="tab.key"
                  @click="activeTab = tab.key"
                  :class="[
                    'whitespace-nowrap border-b-2 px-1 pb-3 text-sm font-medium transition-colors',
                    activeTab === tab.key
                      ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  ]">
                  {{ tab.label }}
                </button>
              </nav>
            </div>

            <!-- Tab: Personal Information -->
            <div v-show="activeTab === 'personal'">
              <div class="mb-5">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ t('profile.personalInfo') }}
                </h4>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('profile.personalInfoDesc') }}</p>
              </div>

              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                  <span class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    {{ t('profile.usernameLabel') }}
                  </span>
                  <div class="text-sm font-medium text-gray-900 dark:text-white">{{ displayName }}</div>
                </div>

                <div class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                  <span class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    {{ t('profile.workerId') }}
                  </span>
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ user?.worker_id || 'N/A' }}
                  </div>
                </div>

                <div class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                  <span class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    {{ t('profile.emailAddress') }}
                  </span>
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ user?.email || 'N/A' }}
                  </div>
                </div>

                <div class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                  <span class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    {{ t('profile.dateJoined') }}
                  </span>
                  <div class="text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(user?.date_joined) }}</div>
                </div>

                <div class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                  <span class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    {{ t('profile.lastLogin') }}
                  </span>
                  <div class="text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(user?.last_login) }}</div>
                </div>
              </div>
            </div>

            <!-- Tab: Preferences -->
            <div v-show="activeTab === 'preferences'">
              <div class="mb-5">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ t('profile.preferences') }}
                </h4>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('profile.preferencesDesc') }}</p>
              </div>

              <div class="space-y-4">
                <!-- Language Preference -->
                <div class="rounded-xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
                  <div class="flex items-center justify-between">
                    <div>
                      <h5 class="font-medium text-gray-900 dark:text-white">{{ t('profile.defaultLanguage') }}</h5>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        {{ t('profile.defaultLanguageDesc') }}
                      </p>
                    </div>
                    <select
                      :value="currentLanguage"
                      @change="changeLanguage(($event.target as HTMLSelectElement).value)"
                      :disabled="languageSaving"
                      class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white">
                      <option v-for="loc in supportedLocales" :key="loc.code" :value="loc.code">
                        {{ loc.flag }} {{ loc.name }}
                      </option>
                    </select>
                  </div>
                  <p v-if="languageSaveMsg" class="mt-2 text-xs" :class="languageSaveError ? 'text-red-500' : 'text-green-600 dark:text-green-400'">
                    {{ languageSaveMsg }}
                  </p>
                </div>

                <!-- Event Reminders -->
                <div class="rounded-xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
                  <div class="flex items-center justify-between">
                    <div>
                      <h5 class="font-medium text-gray-900 dark:text-white">{{ t('profile.eventReminders') }}</h5>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        {{ t('profile.eventRemindersDesc') }}
                      </p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" :checked="eventRemindersEnabled" @change="toggleEventReminders"
                        class="sr-only peer" :disabled="remindersSaving">
                      <div
                        class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-brand-300 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-transform dark:border-gray-600 peer-checked:bg-brand-500">
                      </div>
                    </label>
                  </div>
                  <p v-if="remindersSaveMsg" class="mt-2 text-xs" :class="remindersSaveError ? 'text-red-500' : 'text-green-600 dark:text-green-400'">
                    {{ remindersSaveMsg }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Tab: Permissions & Access -->
            <div v-show="activeTab === 'permissions'">
              <div class="mb-5">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ t('profile.permissionsAccess') }}
                </h4>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('profile.permissionsAccessDesc') }}</p>
              </div>

              <div class="rounded-xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
                <div v-if="permissionDetails.length > 0" class="space-y-3">
                  <div v-for="perm in permissionDetails" :key="perm.resource"
                    class="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-3 dark:border-gray-600 dark:bg-gray-800">
                    <span class="font-medium text-gray-900 dark:text-white">{{ formatPermission(perm.resource) }}</span>
                    <div class="flex gap-1">
                      <span v-for="action in perm.actions" :key="action" :class="[
                        'rounded px-2 py-0.5 text-xs font-medium',
                        action === 'create' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                          action === 'read' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                            action === 'update' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                              'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                      ]">
                        {{ action.charAt(0).toUpperCase() + action.slice(1) }}
                      </span>
                    </div>
                  </div>
                </div>
                <p v-else class="text-sm text-gray-500 dark:text-gray-400">{{ t('profile.noPermissions') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { type SupportedLocale, setLocale, supportedLocales } from '@/i18n'
import { authAPI } from '@/services/api/auth'
import { useAuthStore } from '@/stores/auth'
import { formatLocalDateTime } from '@/utils/dateTime'

const authStore = useAuthStore()
const { t, locale } = useI18n()
const user = computed(() => authStore.user)

// Tab state
type TabKey = 'personal' | 'preferences' | 'permissions'
const activeTab = ref<TabKey>('personal')
const tabs = computed(() => [
	{ key: 'personal' as TabKey, label: t('profile.personalInfo') },
	{ key: 'preferences' as TabKey, label: t('profile.preferences') },
	{ key: 'permissions' as TabKey, label: t('profile.permissionsAccess') },
])

// Language preference
const currentLanguage = computed(() => locale.value)
const languageSaving = ref(false)
const languageSaveMsg = ref('')
const languageSaveError = ref(false)

const changeLanguage = async (langCode: string) => {
	languageSaving.value = true
	languageSaveMsg.value = ''
	languageSaveError.value = false
	try {
		// Apply immediately
		setLocale(langCode as SupportedLocale)
		// Persist to backend
		await authAPI.updatePreferences({ preferred_language: langCode })
		// Update local user state
		if (authStore.user) {
			authStore.setUser({
				...authStore.user,
				preferred_language: langCode,
			})
		}
		languageSaveMsg.value = t('profile.languageSaved')
	} catch {
		languageSaveError.value = true
		languageSaveMsg.value = t('profile.languageSaveFailed')
	} finally {
		languageSaving.value = false
		setTimeout(() => {
			languageSaveMsg.value = ''
		}, 3000)
	}
}

// Event Reminders preference
const eventRemindersEnabled = computed(() => authStore.user?.event_reminders_enabled !== false)
const remindersSaving = ref(false)
const remindersSaveMsg = ref('')
const remindersSaveError = ref(false)

const toggleEventReminders = async () => {
	const newValue = !eventRemindersEnabled.value
	remindersSaving.value = true
	remindersSaveMsg.value = ''
	remindersSaveError.value = false
	try {
		await authAPI.updatePreferences({ event_reminders_enabled: newValue })
		if (authStore.user) {
			authStore.setUser({
				...authStore.user,
				event_reminders_enabled: newValue,
			})
		}
		remindersSaveMsg.value = newValue ? t('profile.remindersEnabled') : t('profile.remindersDisabled')
	} catch {
		remindersSaveError.value = true
		remindersSaveMsg.value = t('profile.remindersFailed')
	} finally {
		remindersSaving.value = false
		setTimeout(() => {
			remindersSaveMsg.value = ''
		}, 3000)
	}
}

const displayName = computed(() => {
	if (!user.value) return t('profile.guest')
	const username = user.value.username
	if (username.includes('_')) {
		return username.replace(/_/g, ' ')
	}
	return username
})

const userInitials = computed(() => {
	if (!user.value?.username) return 'GU'
	const username = user.value.username
	const parts = username.split(/[_\s]+/)
	if (parts.length >= 2) {
		return (parts[0]!.charAt(0) + parts[1]!.charAt(0)).toUpperCase()
	} else if (parts.length === 1 && parts[0]!.length >= 2) {
		return parts[0]!.substring(0, 2).toUpperCase()
	} else {
		return parts[0]!.charAt(0).toUpperCase()
	}
})

const userTypeLabel = computed(() => {
	if (!user.value) return t('profile.guest')
	if (authStore.isDeveloper) return t('profile.roleDeveloper')
	if (authStore.isSuperAdmin) return t('profile.roleSuperadmin')
	if (user.value.is_superuser) return t('profile.roleSuperuser')
	if (authStore.isPtbAdmin) return t('profile.rolePtbAdmin')
	if (user.value.is_staff) return t('profile.roleStaff')
	return t('profile.roleRegular')
})

const permissionDetails = computed(() => {
	const perms = user.value?.menu_permissions
	const details: { resource: string; actions: string[] }[] = []
	if (perms && typeof perms === 'object' && !Array.isArray(perms)) {
		Object.entries(perms as Record<string, string[]>).forEach(([resource, actions]) => {
			if (Array.isArray(actions) && actions.length > 0) {
				const orderedActions = ['create', 'read', 'update', 'delete'].filter((a) => actions.includes(a))
				details.push({ resource, actions: orderedActions })
			}
		})
	} else if (Array.isArray(perms)) {
		perms.forEach((resource) => {
			details.push({ resource, actions: ['read'] })
		})
	}
	return details
})

const formatDate = (dateString?: string) => {
	if (!dateString) return t('profile.never')
	try {
		return formatLocalDateTime(dateString)
	} catch {
		return dateString
	}
}

const formatPermission = (perm: string) => {
	return perm
		.split('_')
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(' ')
}
</script>
