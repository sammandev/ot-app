<template>
    <admin-layout>
        <div class="space-y-6">
            <!-- Page Header -->
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.releaseNotes.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.releaseNotes.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.releaseNotes.subtitle', { appAcronym: configStore.appAcronym }) }}</p>
                </div>
                <div class="flex items-center gap-3">
                    <!-- Super Admin: Add Release Note -->
                    <button v-if="authStore.isSuperAdmin" @click="openModal(null)"
                        class="h-10 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700">
                        + Add Release
                    </button>
                    <nav>
                        <ol class="flex items-center gap-2 text-sm">
                            <li><router-link
                                    class="font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                                    to="/">Home</router-link></li>
                            <li class="text-gray-400 dark:text-gray-500">/</li>
                            <li class="font-medium text-brand-500">Release Notes</li>
                        </ol>
                    </nav>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading"
                class="flex flex-col items-center justify-center py-16 rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
                <svg class="animate-spin h-8 w-8 text-brand-500 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none"
                    viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <p class="text-sm text-gray-500 dark:text-gray-400">Loading release notes...</p>
            </div>

            <!-- Empty state -->
            <div v-else-if="releases.length === 0"
                class="flex flex-col items-center justify-center py-16 rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                    stroke="currentColor" class="h-12 w-12 text-gray-300 dark:text-gray-600 mb-3">
                    <path stroke-linecap="round" stroke-linejoin="round"
                        d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                </svg>
                <p class="text-sm text-gray-500 dark:text-gray-400">No release notes available yet.</p>
            </div>

            <!-- Release Notes Timeline -->
            <div v-else class="space-y-6">
                <div v-for="(release, index) in releases" :key="release.id"
                    class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden transition-shadow"
                    :class="{ 'ring-2 ring-brand-500/30': index === 0 }">
                    <!-- Release Header -->
                    <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800 cursor-pointer select-none"
                        :class="index === 0 ? 'bg-gradient-to-r from-brand-50 to-transparent dark:from-brand-900/20 dark:to-transparent' : 'bg-gray-50/50 dark:bg-gray-900/30'"
                        @click="toggleRelease(release.id!)">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <!-- Version Badge -->
                                <span
                                    class="inline-flex items-center rounded-lg px-3 py-1.5 text-sm font-bold"
                                    :class="getStatusBadgeClass(release.status)">
                                    v{{ release.version }}
                                </span>
                                <!-- Latest badge -->
                                <span v-if="index === 0"
                                    class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
                                    Latest
                                </span>
                                <!-- Status badge (beta, hotfix) -->
                                <span v-if="release.status !== 'stable'"
                                    class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                                    :class="release.status === 'beta' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'">
                                    {{ release.status_display }}
                                </span>
                            </div>
                            <div class="flex items-center gap-3">
                                <!-- Admin actions -->
                                <template v-if="authStore.isSuperAdmin">
                                    <button @click.stop="openModal(release)"
                                        class="h-7 rounded-md border border-gray-300 px-2.5 text-xs font-medium text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 transition"
                                        title="Edit">
                                        Edit
                                    </button>
                                    <button @click.stop="deleteRelease(release.id!)"
                                        class="h-7 rounded-md border border-red-300 px-2.5 text-xs font-medium text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400 dark:hover:bg-red-900/20 transition"
                                        title="Delete">
                                        Delete
                                    </button>
                                </template>
                                <span class="text-sm text-gray-500 dark:text-gray-400">
                                    {{ formatDate(release.release_date) }}
                                </span>
                                <!-- Expand/collapse chevron -->
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="2" stroke="currentColor"
                                    class="h-4 w-4 text-gray-400 transition-transform duration-200"
                                    :class="{ 'rotate-180': expandedReleases.has(release.id!) }">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                                </svg>
                            </div>
                        </div>
                        <!-- Summary -->
                        <p v-if="release.summary" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                            {{ release.summary }}
                        </p>
                    </div>

                    <!-- Release Content (collapsible) -->
                    <div v-show="expandedReleases.has(release.id!)" class="px-6 py-5 space-y-5">
                        <!-- New Features -->
                        <div v-if="release.new_features?.length">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-base">🚀</span>
                                <h4 class="text-sm font-semibold text-gray-900 dark:text-white">New Features</h4>
                                <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">{{ release.new_features.length }}</span>
                            </div>
                            <ul class="space-y-1.5 pl-7">
                                <li v-for="(item, i) in release.new_features" :key="i" class="text-sm text-gray-600 dark:text-gray-400 relative before:content-['•'] before:absolute before:-left-4 before:text-gray-400 dark:before:text-gray-600">{{ item }}</li>
                            </ul>
                        </div>

                        <!-- Improvements -->
                        <div v-if="release.improvements?.length">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-base">✨</span>
                                <h4 class="text-sm font-semibold text-gray-900 dark:text-white">Improvements</h4>
                                <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{{ release.improvements.length }}</span>
                            </div>
                            <ul class="space-y-1.5 pl-7">
                                <li v-for="(item, i) in release.improvements" :key="i" class="text-sm text-gray-600 dark:text-gray-400 relative before:content-['•'] before:absolute before:-left-4 before:text-gray-400 dark:before:text-gray-600">{{ item }}</li>
                            </ul>
                        </div>

                        <!-- Bug Fixes -->
                        <div v-if="release.bug_fixes?.length">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-base">🐛</span>
                                <h4 class="text-sm font-semibold text-gray-900 dark:text-white">Bug Fixes</h4>
                                <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">{{ release.bug_fixes.length }}</span>
                            </div>
                            <ul class="space-y-1.5 pl-7">
                                <li v-for="(item, i) in release.bug_fixes" :key="i" class="text-sm text-gray-600 dark:text-gray-400 relative before:content-['•'] before:absolute before:-left-4 before:text-gray-400 dark:before:text-gray-600">{{ item }}</li>
                            </ul>
                        </div>

                        <!-- Breaking Changes -->
                        <div v-if="release.breaking_changes?.length">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-base">⚠️</span>
                                <h4 class="text-sm font-semibold text-gray-900 dark:text-white">Breaking Changes</h4>
                                <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">{{ release.breaking_changes.length }}</span>
                            </div>
                            <ul class="space-y-1.5 pl-7">
                                <li v-for="(item, i) in release.breaking_changes" :key="i" class="text-sm text-gray-600 dark:text-gray-400 relative before:content-['•'] before:absolute before:-left-4 before:text-gray-400 dark:before:text-gray-600">{{ item }}</li>
                            </ul>
                        </div>

                        <!-- Security -->
                        <div v-if="release.security?.length">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-base">🔒</span>
                                <h4 class="text-sm font-semibold text-gray-900 dark:text-white">Security</h4>
                                <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">{{ release.security.length }}</span>
                            </div>
                            <ul class="space-y-1.5 pl-7">
                                <li v-for="(item, i) in release.security" :key="i" class="text-sm text-gray-600 dark:text-gray-400 relative before:content-['•'] before:absolute before:-left-4 before:text-gray-400 dark:before:text-gray-600">{{ item }}</li>
                            </ul>
                        </div>

                        <!-- Known Issues -->
                        <div v-if="release.known_issues?.length">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-base">⚡</span>
                                <h4 class="text-sm font-semibold text-gray-900 dark:text-white">Known Issues</h4>
                                <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">{{ release.known_issues.length }}</span>
                            </div>
                            <ul class="space-y-1.5 pl-7">
                                <li v-for="(item, i) in release.known_issues" :key="i" class="text-sm text-gray-600 dark:text-gray-400 relative before:content-['•'] before:absolute before:-left-4 before:text-gray-400 dark:before:text-gray-600">{{ item }}</li>
                            </ul>
                        </div>

                        <!-- Contributors -->
                        <div v-if="release.contributors?.length" class="pt-3 border-t border-gray-100 dark:border-gray-800">
                            <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="1.5" stroke="currentColor" class="h-4 w-4">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-1.997M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Z" />
                                </svg>
                                <span>Contributors: {{ release.contributors.join(', ') }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ========== Create/Edit Modal ========== -->
            <div v-if="showModal" class="fixed inset-0 z-[99999] flex items-center justify-center bg-black/50 p-4">
                <div class="w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-900"
                    @click.stop>
                    <!-- Sticky Header -->
                    <div class="sticky top-0 z-10 flex items-center justify-between px-6 pt-5 pb-4 bg-white dark:bg-gray-900 rounded-t-2xl border-b border-gray-200 dark:border-gray-700">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                            {{ editId ? 'Edit Release Note' : 'New Release Note' }}
                        </h3>
                        <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-xl">&times;</button>
                    </div>

                    <!-- Scrollable Body -->
                    <div class="flex-1 overflow-y-auto px-6 py-5 space-y-5">

                    <!-- Basic info -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Version *</label>
                            <input v-model="form.version" type="text" placeholder="e.g., 2.3.0"
                                class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                        </div>
                        <div>
                            <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Release Date *</label>
                            <input v-model="form.release_date" type="date"
                                class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                        </div>
                        <div>
                            <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Status</label>
                            <select v-model="form.status"
                                class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
                                <option value="stable">Stable</option>
                                <option value="beta">Beta</option>
                                <option value="hotfix">Hotfix</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Summary</label>
                        <textarea v-model="form.summary" rows="2" placeholder="Brief summary of this release"
                            class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white" />
                    </div>

                    <!-- Category editors -->
                    <div v-for="cat in categories" :key="cat.key" class="space-y-2">
                        <div class="flex items-center justify-between">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                                {{ cat.emoji }} {{ cat.label }}
                                <span class="text-xs text-gray-400 ml-1">({{ (form[cat.key] as string[]).length }})</span>
                            </label>
                            <button @click="addCategoryItem(cat.key)" type="button"
                                class="text-xs text-brand-600 hover:text-brand-700 dark:text-brand-400 font-medium">
                                + Add Item
                            </button>
                        </div>
                        <div v-for="(_, idx) in (form[cat.key] as string[])" :key="idx" class="flex items-center gap-2">
                            <input v-model="(form[cat.key] as string[])[idx]" type="text"
                                class="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                                :placeholder="`${cat.label} item`" />
                            <button @click="removeCategoryItem(cat.key, idx)" type="button"
                                class="h-8 w-8 rounded-lg border border-red-300 text-red-500 hover:bg-red-50 flex items-center justify-center dark:border-red-700 dark:hover:bg-red-900/20 transition text-sm">
                                &times;
                            </button>
                        </div>
                    </div>

                    <!-- Published toggle -->
                    <div class="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                        <div>
                            <h4 class="font-medium text-gray-900 dark:text-white">Published</h4>
                            <p class="text-sm text-gray-500 dark:text-gray-400">When unpublished, only super admin can see this release</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" v-model="form.published" class="sr-only peer">
                            <div class="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-brand-300 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-transform dark:border-gray-600 peer-checked:bg-brand-500"></div>
                        </label>
                    </div>
                    </div>

                    <!-- Sticky Footer -->
                    <div class="sticky bottom-0 z-10 flex justify-end gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-b-2xl">
                        <button @click="showModal = false"
                            class="h-11 rounded-lg border border-gray-300 bg-white px-5 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                            Cancel
                        </button>
                        <button @click="saveRelease" :disabled="saving"
                            class="h-11 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed">
                            {{ saving ? 'Saving...' : (editId ? 'Update' : 'Create') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </admin-layout>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToast } from '@/composables/useToast'
import { type ReleaseNoteData, releaseNoteAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
const { t } = useI18n()
const authStore = useAuthStore()
const { showToast } = useToast()
const confirmDialog = useConfirmDialog()

const loading = ref(true)
const saving = ref(false)
const releases = ref<ReleaseNoteData[]>([])
const expandedReleases = ref<Set<number>>(new Set())

// Modal state
const showModal = ref(false)
const editId = ref<number | null>(null)

type CategoryKey =
	| 'new_features'
	| 'improvements'
	| 'bug_fixes'
	| 'breaking_changes'
	| 'security'
	| 'known_issues'

interface FormData {
	version: string
	release_date: string
	status: string
	summary: string
	new_features: string[]
	improvements: string[]
	bug_fixes: string[]
	breaking_changes: string[]
	security: string[]
	known_issues: string[]
	published: boolean
	[key: string]: string | string[] | boolean
}

const form = reactive<FormData>({
	version: '',
	release_date: new Date().toISOString().split('T')[0] ?? '',
	status: 'stable',
	summary: '',
	new_features: [],
	improvements: [],
	bug_fixes: [],
	breaking_changes: [],
	security: [],
	known_issues: [],
	published: true,
})

const categories: { key: CategoryKey; label: string; emoji: string }[] = [
	{ key: 'new_features', label: 'New Features', emoji: '🚀' },
	{ key: 'improvements', label: 'Improvements', emoji: '✨' },
	{ key: 'bug_fixes', label: 'Bug Fixes', emoji: '🐛' },
	{ key: 'breaking_changes', label: 'Breaking Changes', emoji: '⚠️' },
	{ key: 'security', label: 'Security', emoji: '🔒' },
	{ key: 'known_issues', label: 'Known Issues', emoji: '⚡' },
]

function resetForm() {
	form.version = ''
	form.release_date = new Date().toISOString().split('T')[0] ?? ''
	form.status = 'stable'
	form.summary = ''
	form.new_features = []
	form.improvements = []
	form.bug_fixes = []
	form.breaking_changes = []
	form.security = []
	form.known_issues = []
	form.published = true
}

function openModal(release: ReleaseNoteData | null) {
	if (release) {
		editId.value = release.id!
		form.version = release.version
		form.release_date = release.release_date
		form.status = release.status
		form.summary = release.summary || ''
		form.new_features = [...(release.new_features || [])]
		form.improvements = [...(release.improvements || [])]
		form.bug_fixes = [...(release.bug_fixes || [])]
		form.breaking_changes = [...(release.breaking_changes || [])]
		form.security = [...(release.security || [])]
		form.known_issues = [...(release.known_issues || [])]
		form.published = release.published
	} else {
		editId.value = null
		resetForm()
	}
	showModal.value = true
}

function addCategoryItem(key: string) {
	;(form[key] as string[]).push('')
}

function removeCategoryItem(key: string, idx: number) {
	;(form[key] as string[]).splice(idx, 1)
}

function cleanArrays(data: Partial<ReleaseNoteData>): Partial<ReleaseNoteData> {
	for (const key of [
		'new_features',
		'improvements',
		'bug_fixes',
		'breaking_changes',
		'security',
		'known_issues',
	]) {
		const arr = data[key as keyof ReleaseNoteData]
		if (Array.isArray(arr)) {
			;(data as Record<string, unknown>)[key] = arr.filter((s: string) => s.trim())
		}
	}
	return data
}

async function saveRelease() {
	if (!form.version || !form.release_date) {
		showToast('Version and Release Date are required.', 'warning')
		return
	}
	saving.value = true
	try {
		const payload = cleanArrays({
			version: form.version,
			release_date: form.release_date,
			status: form.status,
			summary: form.summary,
			new_features: [...form.new_features],
			improvements: [...form.improvements],
			bug_fixes: [...form.bug_fixes],
			breaking_changes: [...form.breaking_changes],
			security: [...form.security],
			known_issues: [...form.known_issues],
			published: form.published,
		})
		if (editId.value) {
			await releaseNoteAPI.update(editId.value, payload)
		} else {
			await releaseNoteAPI.create(payload)
		}
		showModal.value = false
		await fetchReleaseNotes()
		// Re-fetch system config so version/build date updates immediately
		await configStore.fetchConfig()
	} catch (err) {
		console.error('Failed to save release note:', err)
		showToast('Failed to save release note.', 'error')
	} finally {
		saving.value = false
	}
}

async function deleteRelease(id: number) {
	const ok = await confirmDialog.confirm({
		title: 'Delete Release Note',
		message: 'Are you sure you want to delete this release note? This action cannot be undone.',
		type: 'danger',
		confirmLabel: 'Delete',
	})
	if (!ok) return
	try {
		await releaseNoteAPI.delete(id)
		await fetchReleaseNotes()
		// Re-fetch system config so version/build date updates immediately
		await configStore.fetchConfig()
		showToast('Release note deleted', 'success')
	} catch (err) {
		console.error('Failed to delete release note:', err)
		showToast('Failed to delete release note.', 'error')
	}
}

function toggleRelease(id: number) {
	if (expandedReleases.value.has(id)) {
		expandedReleases.value.delete(id)
	} else {
		expandedReleases.value.add(id)
	}
}

function getStatusBadgeClass(status: string) {
	switch (status) {
		case 'beta':
			return 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
		case 'hotfix':
			return 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
		default:
			return 'bg-brand-100 text-brand-800 dark:bg-brand-900/40 dark:text-brand-300'
	}
}

function formatDate(dateStr: string) {
	if (!dateStr) return ''
	const d = new Date(dateStr + 'T00:00:00')
	return d.toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'long',
		day: 'numeric',
	})
}

async function fetchReleaseNotes() {
	loading.value = true
	try {
		const data = await releaseNoteAPI.list()
		releases.value = data.results || (data as unknown as ReleaseNoteData[])
		// Auto-expand the latest release
		if (releases.value.length > 0 && releases.value[0]?.id) {
			expandedReleases.value.add(releases.value[0].id)
		}
	} catch (err) {
		console.error('Failed to fetch release notes:', err)
	} finally {
		loading.value = false
	}
}

onMounted(fetchReleaseNotes)
</script>
