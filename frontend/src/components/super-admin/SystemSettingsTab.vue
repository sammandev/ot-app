<template>
    <div class="space-y-6">
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <!-- Header -->
            <div class="flex items-center gap-4 border-b border-gray-200 px-6 py-5 dark:border-gray-800">
                <div class="rounded-xl bg-brand-100 p-3 dark:bg-brand-500/20">
                    <SettingsIcon class="h-6 w-6 text-brand-600 dark:text-brand-400" />
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">System Configuration</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Manage application settings and metadata</p>
                </div>
            </div>

            <!-- Form Body -->
            <div class="p-6">
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <!-- App Name -->
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Application Name
                        </label>
                        <input v-model="settingsForm.app_name" type="text"
                            placeholder="e.g., Overtime Management System"
                            class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-brand-500 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400" />
                    </div>

                    <!-- App Acronym -->
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Application Acronym
                        </label>
                        <input v-model="settingsForm.app_acronym" type="text" placeholder="e.g., OMS"
                            class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-brand-500 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400" />
                    </div>

                    <!-- Version (auto-synced from Release Notes) -->
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Version
                            <span class="ml-1 text-xs font-normal text-gray-400">(auto-synced)</span>
                        </label>
                        <input :value="configStore.version" type="text" disabled readonly
                            class="block w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm text-gray-500 cursor-not-allowed dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400" />
                    </div>

                    <!-- Build Date (auto-synced from Release Notes) -->
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Build Date
                            <span class="ml-1 text-xs font-normal text-gray-400">(auto-synced)</span>
                        </label>
                        <input :value="configStore.buildDate" type="text" disabled readonly
                            class="block w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm text-gray-500 cursor-not-allowed dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400" />
                    </div>
                </div>

                <!-- Tab Icon Upload -->
                <div class="mt-6">
                    <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Browser Tab Icon (Favicon)
                    </label>
                    <div class="flex items-center gap-4">
                        <!-- Current icon preview -->
                        <div class="flex h-16 w-16 items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 dark:border-gray-600 dark:bg-gray-800">
                            <img v-if="tabIconPreview || configStore.tabIconUrl" :src="tabIconPreview || configStore.tabIconUrl!" alt="Tab icon" class="h-10 w-10 object-contain" />
                            <svg v-else class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <div class="flex flex-col gap-2">
                            <div class="flex gap-2">
                                <label class="cursor-pointer rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                                    Choose File
                                    <input type="file" accept=".ico,.svg,.png" class="hidden" @change="handleTabIconSelect" />
                                </label>
                                <button v-if="configStore.tabIconUrl" @click="removeTabIcon" type="button"
                                    class="rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 transition hover:bg-red-100 dark:border-red-500/40 dark:bg-red-500/10 dark:text-red-300">
                                    Remove
                                </button>
                            </div>
                            <p class="text-xs text-gray-500 dark:text-gray-400">Accepted: .ico, .svg, .png (max 512KB)</p>
                            <p v-if="tabIconFile" class="text-xs font-medium text-brand-600 dark:text-brand-400">
                                Selected: {{ tabIconFile.name }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Info Banner -->
                <div
                    class="mt-6 flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 dark:border-blue-900/40 dark:bg-blue-900/20">
                    <InfoCircleIcon class="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-600 dark:text-blue-400" />
                    <div class="text-sm text-blue-700 dark:text-blue-300">
                        <p class="mb-1 font-medium">Configuration Information</p>
                        <p>Application name and acronym can be changed here. <strong>Version</strong> and
                            <strong>Build Date</strong> are automatically synced from the latest
                            <router-link to="/release-notes" class="font-medium underline hover:text-blue-900 dark:hover:text-blue-200">Release Note</router-link>.</p>
                    </div>
                </div>

                <!-- Actions -->
                <div class="mt-6 flex justify-end gap-3 border-t border-gray-200 pt-6 dark:border-gray-800">
                    <button @click="loadConfigFromStore" type="button"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-5 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-gray-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                        Reset to Defaults
                    </button>
                    <button @click="saveSettings" :disabled="configStore.loading" type="button"
                        class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 disabled:cursor-not-allowed disabled:opacity-50">
                        <span v-if="!configStore.loading">Save Configuration</span>
                        <span v-else class="flex items-center gap-2">
                            <svg class="h-4 w-4 animate-spin text-white" xmlns="http://www.w3.org/2000/svg"
                                fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                </path>
                            </svg>
                            Saving...
                        </span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToast } from '@/composables/useToast'
import { MAX_ICON_FILE_SIZE_BYTES } from '@/constants/ui'
import { InfoCircleIcon, SettingsIcon } from '@/icons'
import { apiClient } from '@/services/api/client'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
const { showToast } = useToast()
const confirmDialog = useConfirmDialog()

const settingsForm = reactive({
	app_name: '',
	app_acronym: '',
})

// Tab icon upload state
const tabIconFile = ref<File | null>(null)
const tabIconPreview = ref<string | null>(null)

const handleTabIconSelect = (event: Event) => {
	const input = event.target as HTMLInputElement
	const file = input.files?.[0]
	if (!file) return

	const allowed = ['image/x-icon', 'image/vnd.microsoft.icon', 'image/svg+xml', 'image/png']
	if (!allowed.includes(file.type) && !file.name.endsWith('.ico')) {
		showToast('Only .ico, .svg and .png files are accepted', 'error')
		return
	}

	if (file.size > MAX_ICON_FILE_SIZE_BYTES) {
		showToast('File size must be under 512KB', 'error')
		return
	}

	tabIconFile.value = file
	tabIconPreview.value = URL.createObjectURL(file)
}

const removeTabIcon = async () => {
	const confirmed = await confirmDialog.confirm({
		title: 'Remove Tab Icon',
		message: 'Are you sure you want to remove the custom tab icon?',
		confirmLabel: 'Remove',
		type: 'danger',
	})
	if (!confirmed) return

	try {
		await apiClient.delete('/v1/system/config/')
		tabIconFile.value = null
		tabIconPreview.value = null
		await configStore.fetchConfig()
		updateFavicon(null)
		showToast('Tab icon removed', 'success')
	} catch {
		showToast('Failed to remove tab icon', 'error')
	}
}

const uploadTabIcon = async () => {
	if (!tabIconFile.value) return
	const formData = new FormData()
	formData.append('tab_icon', tabIconFile.value)
	await apiClient.patch('/v1/system/config/', formData, {
		headers: {
			'Content-Type': 'multipart/form-data',
		},
	})
	tabIconFile.value = null
	tabIconPreview.value = null
}

const updateFavicon = (url: string | null) => {
	let link = document.querySelector<HTMLLinkElement>("link[rel~='icon']")
	if (!link) {
		link = document.createElement('link')
		link.rel = 'icon'
		document.head.appendChild(link)
	}
	link.href = url || '/icon5.svg'
}

const saveSettings = async () => {
	try {
		await configStore.updateConfig({
			app_name: settingsForm.app_name,
			app_acronym: settingsForm.app_acronym,
		})

		if (tabIconFile.value) {
			await uploadTabIcon()
			await configStore.fetchConfig()
		}

		settingsForm.app_name = configStore.appName
		settingsForm.app_acronym = configStore.appAcronym

		if (configStore.tabIconUrl) {
			updateFavicon(configStore.tabIconUrl)
		}

		showToast('System configuration updated successfully', 'success')
	} catch (e) {
		console.error(e)
		showToast('Failed to update configuration', 'error')
	}
}

const loadConfigFromStore = () => {
	settingsForm.app_name = configStore.appName
	settingsForm.app_acronym = configStore.appAcronym
}

/** Initialize form values from config store */
const initFromConfig = () => {
	loadConfigFromStore()
}

defineExpose({ initFromConfig })

onMounted(async () => {
	// Ensure config is loaded
	if (!configStore.appName) {
		try {
			await configStore.fetchConfig()
		} catch {
			// Config may already be loading from parent
		}
	}
	loadConfigFromStore()
})
</script>
