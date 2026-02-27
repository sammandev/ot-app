<template>
    <div class="space-y-6">
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between border-b border-gray-200 px-6 py-5 dark:border-gray-800">
                <div class="flex items-center gap-4">
                    <div class="rounded-xl bg-indigo-100 p-3 dark:bg-indigo-500/20">
                        <svg class="h-6 w-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">SMB / Network Share
                            Configurations</h3>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Manage multiple SMB servers. Mark one as
                            active for file uploads. Passwords are encrypted at rest.</p>
                    </div>
                </div>
                <button @click="openSmbModal(null)"
                    class="h-10 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700">
                    + Add Config
                </button>
            </div>

            <!-- Loading -->
            <div v-if="smbLoading" class="flex justify-center py-12">
                <svg class="animate-spin h-6 w-6 text-brand-500" xmlns="http://www.w3.org/2000/svg" fill="none"
                    viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
            </div>

            <div v-else-if="smbConfigs.length === 0"
                class="flex flex-col items-center justify-center py-12 text-gray-400 dark:text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                    stroke="currentColor" class="h-10 w-10 mb-2">
                    <path stroke-linecap="round" stroke-linejoin="round"
                        d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
                </svg>
                <p class="text-sm">No SMB configurations yet. Click "Add Config" to create one.</p>
            </div>

            <!-- Config list -->
            <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
                <div v-for="cfg in smbConfigs" :key="cfg.id"
                    class="px-6 py-4 flex items-center justify-between gap-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition">
                    <div class="flex items-center gap-4 min-w-0 flex-1">
                        <!-- Active indicator -->
                        <div class="w-3 h-3 rounded-full shrink-0"
                            :class="cfg.is_active ? 'bg-green-500 ring-4 ring-green-100 dark:ring-green-900/40' : 'bg-gray-300 dark:bg-gray-600'">
                        </div>
                        <div class="min-w-0">
                            <div class="flex items-center gap-2">
                                <span class="font-medium text-gray-900 dark:text-white truncate">{{ cfg.name }}</span>
                                <span v-if="cfg.is_active"
                                    class="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
                                    Active
                                </span>
                                <span v-if="cfg.has_password"
                                    class="inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-600 dark:bg-blue-900/30 dark:text-blue-400">
                                    Password Set
                                </span>
                            </div>
                            <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
                                {{ cfg.server || '(no server)' }} / {{ cfg.share_name || '(no share)' }}
                                <span v-if="cfg.path_prefix" class="ml-1 text-gray-400">{{ cfg.path_prefix }}</span>
                            </p>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 shrink-0">
                        <button v-if="!cfg.is_active" @click="activateSmbConfig(cfg.id!)"
                            class="h-8 rounded-lg border border-green-300 bg-white px-3 text-xs font-medium text-green-700 hover:bg-green-50 dark:border-green-700 dark:bg-gray-800 dark:text-green-400 dark:hover:bg-green-900/20 transition"
                            title="Set as Active">
                            Activate
                        </button>
                        <button @click="testSmbConnection(cfg.id!)" :disabled="smbTesting === cfg.id"
                            class="h-8 rounded-lg border border-gray-300 bg-white px-3 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700 disabled:opacity-50 transition"
                            title="Test Connection">
                            {{ smbTesting === cfg.id ? 'Testing...' : 'Test' }}
                        </button>
                        <button @click="openSmbModal(cfg)"
                            class="h-8 rounded-lg border border-gray-300 bg-white px-3 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700 transition"
                            title="Edit">
                            Edit
                        </button>
                        <button @click="deleteSmbConfig(cfg.id!)"
                            class="h-8 rounded-lg border border-red-300 bg-white px-3 text-xs font-medium text-red-600 hover:bg-red-50 dark:border-red-700 dark:bg-gray-800 dark:text-red-400 dark:hover:bg-red-900/20 transition"
                            title="Delete">
                            Delete
                        </button>
                    </div>
                </div>
            </div>

            <!-- Test result banner -->
            <div v-if="smbTestResult" class="mx-6 mb-4 rounded-xl p-4 text-sm flex items-start gap-3"
                :class="smbTestResult.success ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400' : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                    stroke="currentColor" class="h-5 w-5 shrink-0 mt-0.5">
                    <path v-if="smbTestResult.success" stroke-linecap="round" stroke-linejoin="round"
                        d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round"
                        d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
                <span>{{ smbTestResult.message || smbTestResult.error }}</span>
                <button @click="smbTestResult = null" class="ml-auto text-current hover:opacity-70">&times;</button>
            </div>
        </div>

        <!-- SMB Edit/Create Modal -->
        <div v-if="showSmbModal" class="fixed inset-0 z-[99999] flex items-center justify-center bg-black/50 p-4">
            <div role="dialog" aria-modal="true" aria-labelledby="smb-modal-title"
                class="w-full max-w-xl max-h-[90vh] flex flex-col rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-900"
                @click.stop>
                <!-- Sticky Header -->
                <div
                    class="sticky top-0 z-10 flex items-center justify-between px-6 pt-5 pb-4 bg-white dark:bg-gray-900 rounded-t-2xl border-b border-gray-200 dark:border-gray-700">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                        {{ smbEditId ? 'Edit SMB Configuration' : 'New SMB Configuration' }}
                    </h3>
                    <button @click="showSmbModal = false"
                        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-xl">&times;</button>
                </div>

                <!-- Scrollable Body -->
                <div class="flex-1 overflow-y-auto px-6 py-5 space-y-5">
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Config
                            Name</label>
                        <input v-model="smbForm.name" type="text" placeholder="e.g., Production Server"
                            class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div>
                            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Server
                                Host</label>
                            <input v-model="smbForm.server" type="text" placeholder="e.g., 192.168.1.100"
                                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                        </div>
                        <div>
                            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Main Folder
                                Name</label>
                            <input v-model="smbForm.share_name" type="text" placeholder="e.g., ATS_DataCenter"
                                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                        </div>
                        <div>
                            <label
                                class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
                            <input v-model="smbForm.username" type="text" placeholder="SMB Username"
                                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                        </div>
                        <div>
                            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                Password
                                <span v-if="smbForm.has_password"
                                    class="text-xs text-green-600 dark:text-green-400 ml-1">(stored)</span>
                            </label>
                            <input v-model="smbForm.new_password" type="password"
                                :placeholder="smbEditId ? 'Leave blank to keep current' : 'Enter password'"
                                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                        </div>
                        <div>
                            <label
                                class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Domain</label>
                            <input v-model="smbForm.domain" type="text" placeholder="WORKGROUP"
                                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                        </div>
                        <div>
                            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Port
                                (Default: 445)</label>
                            <input v-model.number="smbForm.port" type="number" placeholder="445"
                                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                        </div>
                    </div>
                    <div>
                        <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Path Prefix
                            (Sub Folder Path within the Main Folder)</label>
                        <input v-model="smbForm.path_prefix" type="text"
                            placeholder="Management\PTB\AST_Portal_Overtime\"
                            class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                    </div>
                </div>

                <!-- Sticky Footer -->
                <div
                    class="sticky bottom-0 z-10 flex justify-end gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-b-2xl">
                    <button @click="showSmbModal = false"
                        class="h-11 rounded-lg border border-gray-300 bg-white px-5 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                        Cancel
                    </button>
                    <button @click="saveSmbConfig" :disabled="smbSaving"
                        class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed">
                        {{ smbSaving ? 'Saving...' : (smbEditId ? 'Update Config' : 'Create Config') }}
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
import { type SMBConfigData, smbConfigAPI } from '@/services/api/config'

const { showToast } = useToast()
const confirmDialog = useConfirmDialog()

const smbLoading = ref(false)
const smbSaving = ref(false)
const smbTesting = ref<number | null>(null)
const smbTestResult = ref<{
	success: boolean
	message?: string
	error?: string
} | null>(null)
const smbConfigs = ref<SMBConfigData[]>([])
const showSmbModal = ref(false)
const smbEditId = ref<number | null>(null)
const smbForm = reactive({
	name: 'Default',
	server: '',
	share_name: '',
	username: '',
	new_password: '',
	domain: 'WORKGROUP',
	port: 445,
	path_prefix: '',
	has_password: false,
})

const resetSmbForm = () => {
	smbForm.name = 'Default'
	smbForm.server = ''
	smbForm.share_name = ''
	smbForm.username = ''
	smbForm.new_password = ''
	smbForm.domain = 'WORKGROUP'
	smbForm.port = 445
	smbForm.path_prefix = ''
	smbForm.has_password = false
}

const openSmbModal = (cfg: SMBConfigData | null) => {
	smbTestResult.value = null
	if (cfg) {
		smbEditId.value = cfg.id!
		smbForm.name = cfg.name || ''
		smbForm.server = cfg.server || ''
		smbForm.share_name = cfg.share_name || ''
		smbForm.username = cfg.username || ''
		smbForm.domain = cfg.domain || 'WORKGROUP'
		smbForm.port = cfg.port || 445
		smbForm.path_prefix = cfg.path_prefix || ''
		smbForm.has_password = cfg.has_password || false
		smbForm.new_password = ''
	} else {
		smbEditId.value = null
		resetSmbForm()
	}
	showSmbModal.value = true
}

const loadSmbConfigs = async () => {
	smbLoading.value = true
	try {
		const data = await smbConfigAPI.list()
		smbConfigs.value = data.results || (data as unknown as SMBConfigData[])
	} catch (err) {
		console.error('Failed to load SMB configs:', err)
	} finally {
		smbLoading.value = false
	}
}

const saveSmbConfig = async () => {
	smbSaving.value = true
	try {
		const payload: Record<string, unknown> = {
			name: smbForm.name,
			server: smbForm.server,
			share_name: smbForm.share_name,
			username: smbForm.username,
			domain: smbForm.domain,
			port: smbForm.port,
			path_prefix: smbForm.path_prefix,
		}
		if (smbForm.new_password) {
			payload.new_password = smbForm.new_password
		}
		if (smbEditId.value) {
			await smbConfigAPI.update(smbEditId.value, payload)
		} else {
			await smbConfigAPI.create(payload)
		}
		showSmbModal.value = false
		await loadSmbConfigs()
	} catch (err) {
		console.error('Failed to save SMB config:', err)
		showToast('Failed to save SMB configuration', 'error')
	} finally {
		smbSaving.value = false
	}
}

const activateSmbConfig = async (id: number) => {
	try {
		await smbConfigAPI.activate(id)
		await loadSmbConfigs()
	} catch (err) {
		console.error('Failed to activate SMB config:', err)
		showToast('Failed to activate configuration', 'error')
	}
}

const deleteSmbConfig = async (id: number) => {
	const ok = await confirmDialog.confirm({
		title: 'Delete SMB Configuration',
		message: 'Are you sure you want to delete this SMB configuration? This action cannot be undone.',
		type: 'danger',
		confirmLabel: 'Delete',
	})
	if (!ok) return
	try {
		await smbConfigAPI.delete(id)
		await loadSmbConfigs()
		showToast('SMB configuration deleted', 'success')
	} catch (err) {
		console.error('Failed to delete SMB config:', err)
		showToast('Failed to delete configuration', 'error')
	}
}

const testSmbConnection = async (id: number) => {
	smbTesting.value = id
	smbTestResult.value = null
	try {
		const data = await smbConfigAPI.testConnection(id)
		smbTestResult.value = data
	} catch {
		smbTestResult.value = { success: false, error: 'Connection test failed' }
	} finally {
		smbTesting.value = null
	}
}

defineExpose({ loadSmbConfigs })

onMounted(() => {
	loadSmbConfigs()
})
</script>
