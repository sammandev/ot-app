<template>
    <!-- Info Card with improved styling -->
    <div v-if="showInfoCard" :class="[
        'rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100/50 shadow-sm dark:border-blue-900/50 dark:from-blue-900/20 dark:to-blue-800/10 transition-shadow duration-300',
        isCollapsed ? 'p-3' : 'p-5'
    ]">
        <div class="flex items-start justify-between gap-4">
            <div class="flex-1">
                <div :class="['flex flex-wrap items-center gap-3', isCollapsed ? 'mb-0' : 'mb-4']">
                    <div class="flex items-center gap-2">
                        <div class="rounded-full bg-blue-600 p-1 dark:bg-blue-500">
                            <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <strong class="text-base font-semibold text-blue-900 dark:text-blue-100">{{ t('otForm.regulations.title') }}</strong>
                    </div>
                    <div class="flex items-center gap-2">
                        <button @click="openModal"
                            class="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 hover:shadow dark:bg-blue-600 dark:hover:bg-blue-500">
                            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            {{ t('otForm.regulations.viewFullPolicy') }}
                        </button>
                        <span
                            class="rounded-md bg-blue-200/50 px-2 py-1 text-xs font-medium text-blue-700 dark:bg-blue-800/30 dark:text-blue-300">{{
                                formattedDate }}</span>
                    </div>
                </div>
                <div v-if="!isCollapsed" class="transition-[max-height,opacity] duration-300">
                    <ul class="space-y-2.5 text-sm leading-relaxed text-blue-900 dark:text-blue-100">
                        <li v-for="regulation in enabledRegulations" :key="regulation.id"
                            class="flex items-start gap-3">
                            <div
                                class="mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-600/10 dark:bg-blue-500/20">
                                <svg class="h-3 w-3 text-blue-600 dark:text-blue-400" fill="currentColor"
                                    viewBox="0 0 20 20">
                                    <path fill-rule="evenodd"
                                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                        clip-rule="evenodd" />
                                </svg>
                            </div>
                            <span>{{ regulation.content }}</span>
                        </li>
                        <li v-if="enabledRegulations.length === 0"
                            class="text-center text-gray-500 dark:text-gray-400 py-2">
                            {{ t('otForm.regulations.noRegulations') }}
                        </li>
                    </ul>
                </div>
            </div>
            <div class="flex flex-shrink-0 gap-1">
                <button @click="toggleCollapse"
                    class="rounded-lg p-1.5 text-blue-600 transition-colors hover:bg-blue-200/50 dark:text-blue-400 dark:hover:bg-blue-800/30"
                    :title="isCollapsed ? t('otForm.regulations.expand') : t('otForm.regulations.collapse')">
                    <svg class="h-5 w-5 transition-transform duration-300" :class="{ 'rotate-180': isCollapsed }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                </button>
                <button @click="hideInfoCard"
                    class="rounded-lg p-1.5 text-blue-600 transition-colors hover:bg-blue-200/50 dark:text-blue-400 dark:hover:bg-blue-800/30"
                    :title="t('otForm.regulations.dismiss')">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <!-- PDF Modal - Teleported to body to escape overflow-x-clip -->
    <Teleport to="body">
    <div v-if="showRegulationModal"
        class="fixed inset-0 z-[100000] flex items-center justify-center overflow-hidden"
        :class="isFullscreen ? '' : 'p-4'" @click.self="closeModal">
        <!-- Backdrop covers full viewport -->
        <div class="fixed inset-0 bg-black/60" aria-hidden="true"></div>

        <!-- Modal Container -->
        <div :class="[
            'relative z-10 flex flex-col bg-white dark:bg-gray-900 transition-[width,height,border-radius] duration-300',
            isFullscreen
                ? 'fixed inset-0 h-full w-full'
                : 'h-[95vh] w-[95vw] max-w-[1400px] rounded-2xl border border-gray-200 shadow-2xl dark:border-gray-800'
        ]">
            <!-- Modal Header -->
            <div
                class="flex flex-shrink-0 items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-800">
                <div class="flex items-center gap-3">
                    <div class="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/30">
                        <svg class="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <div>
                        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ t('otForm.regulations.policyTitle') }}
                        </h2>
                        <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('otForm.regulations.updated') }} {{ formattedDate }}</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button @click="toggleFullscreen"
                        class="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                        :title="isFullscreen ? t('otForm.regulations.exitFullscreen') : t('otForm.regulations.enterFullscreen')">
                        <svg v-if="!isFullscreen" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                        </svg>
                        <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                        </svg>
                    </button>
                    <button @click="closeModal"
                        class="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                        :title="t('otForm.regulations.close')">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Modal Body - PDF Viewer with overflow control -->
            <div class="flex-1 overflow-hidden bg-gray-100 dark:bg-gray-950 min-h-0">
                <embed :src="pdfUrl" type="application/pdf" class="h-full w-full min-h-[600px]" />
            </div>
        </div>
    </div>
    </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { regulationAPI, regulationDocumentAPI } from '@/services/api'
import type { OvertimeRegulation } from '@/types/admin'

const { t } = useI18n()

const showRegulationModal = ref(false)
const showInfoCard = ref(true)
const isCollapsed = ref(false)
const isFullscreen = ref(false)
const regulations = ref<OvertimeRegulation[]>([])
const isLoading = ref(false)

// Path to PDF document - will be loaded from API
const pdfUrl = ref('/docs/PTB_AST1_RD_Organization_Policy_20250319.pdf')
const hasPdfDocument = ref(false)
const documentDate = ref<string | null>(null)

const selectLatestDoc = (
	docs:
		| Array<{
				file: string
				created_at: string
		  }>
		| undefined
		| null,
) => {
	if (!docs) return null
	return (
		[...docs].sort(
			(a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
		)[0] || null
	)
}

// Load regulations from API (always fetch fresh data, no caching, no fallback to hardcoded values)
const loadRegulations = async () => {
	try {
		isLoading.value = true
		// Fetch all active regulations (set high page_size to get all)
		const response = await regulationAPI.list({
			is_active: true,
			page_size: 100,
		})

		if (response.results && response.results.length > 0) {
			// Map API response to match the expected OvertimeRegulation type
			// Only show regulations that are active from the API
			regulations.value = response.results.map((item) => ({
				id: item.id,
				content: item.description || item.title,
				order: item.order || 0,
				is_active: item.is_active,
			}))
		} else {
			// No regulations from API - show empty list
			regulations.value = []
		}
	} catch (error) {
		console.error('Failed to load overtime regulations:', error)
		// On API error, show empty list instead of hardcoded defaults
		regulations.value = []
	} finally {
		isLoading.value = false
	}
}

// Load PDF document from API
const loadPdfDocument = async () => {
	try {
		// Fetch all active documents (set high page_size to get all)
		const response = await regulationDocumentAPI.list({
			is_active: true,
			page_size: 100,
		})
		if (response.results && response.results.length > 0) {
			const doc = selectLatestDoc(response.results)
			if (doc) {
				// Store the document's date for display
				documentDate.value = doc.created_at

				// Ensure PDF URL is absolute
				if (doc.file.startsWith('http')) {
					pdfUrl.value = doc.file
				} else {
					// Start with base URL from environment or default
					// Then strip '/api' suffix to get root
					const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
					const serverRoot = apiBase.replace(/\/api\/?$/, '')
					// Ensure doc.file starts with /
					const filePath = doc.file.startsWith('/') ? doc.file : `/${doc.file}`
					pdfUrl.value = `${serverRoot}${filePath}`
				}

				hasPdfDocument.value = true
				return
			}
		}
		// Use default PDF if no uploaded document
		pdfUrl.value = '/docs/PTB_AST1_RD_Organization_Policy_20250319.pdf'
		hasPdfDocument.value = false
	} catch (error) {
		console.error('Failed to load PDF document:', error)
		// Use default PDF on error
		pdfUrl.value = '/docs/PTB_AST1_RD_Organization_Policy_20250319.pdf'
		hasPdfDocument.value = false
	}
}

// Get only active regulations sorted by order
const enabledRegulations = computed(() => {
	return regulations.value.filter((reg) => reg.is_active).sort((a, b) => a.order - b.order)
})

// Extract the date from the document metadata or filename pattern
const formattedDate = computed(() => {
	// 1. Try to extract 8-digit date from the filename (e.g. _20250319.pdf)
	const m = pdfUrl.value.match(/(\d{8})(?=\.pdf)/i)
	if (m?.[1]) {
		const d = m[1]
		return `${d.slice(0, 4)}/${d.slice(4, 6)}/${d.slice(6)}`
	}
	// 2. Fall back to the document's created_at date from the API
	if (documentDate.value) {
		const d = new Date(documentDate.value)
		if (!Number.isNaN(d.getTime())) {
			const yyyy = d.getFullYear()
			const mm = String(d.getMonth() + 1).padStart(2, '0')
			const dd = String(d.getDate()).padStart(2, '0')
			return `${yyyy}/${mm}/${dd}`
		}
	}
	return ''
})

// Keyboard event handler
const handleKeydown = (event: KeyboardEvent) => {
	if (showRegulationModal.value) {
		if (event.key === ' ' || event.code === 'Space') {
			event.preventDefault()
			toggleFullscreen()
		} else if (event.key === 'Escape' || event.code === 'Escape') {
			closeModal()
		}
	}
}

// Set up event listeners when the component mounts
onMounted(() => {
	window.addEventListener('keydown', handleKeydown)

	const hideCard = localStorage.getItem('hideOvertimeInfoCard')
	if (hideCard === 'true') {
		showInfoCard.value = false
	}

	// Load collapse state from localStorage
	const collapsed = localStorage.getItem('overtimeRegulationsCollapsed')
	if (collapsed === 'true') {
		isCollapsed.value = true
	}

	// Load regulations and PDF document from API
	loadRegulations()
	loadPdfDocument()
})

// Clean up event listeners when the component unmounts
onUnmounted(() => {
	window.removeEventListener('keydown', handleKeydown)
	// Ensure body overflow is restored
	document.body.style.overflow = ''
})

// Helper methods
const toggleCollapse = () => {
	isCollapsed.value = !isCollapsed.value
	localStorage.setItem('overtimeRegulationsCollapsed', String(isCollapsed.value))
}

const hideInfoCard = () => {
	showInfoCard.value = false
	localStorage.setItem('hideOvertimeInfoCard', 'true')
}

const openModal = () => {
	// Check if PDF exists (this is a simple check, in production you'd verify the file actually exists)
	if (!pdfUrl.value) {
		alert(t('otForm.regulations.noPolicyAvailable'))
		return
	}
	showRegulationModal.value = true
}

const toggleFullscreen = () => {
	isFullscreen.value = !isFullscreen.value
}

const closeModal = () => {
	showRegulationModal.value = false
	isFullscreen.value = false
}

// Manage body scroll lock and provide console hint when opened
watch(showRegulationModal, (newValue) => {
	document.body.style.overflow = newValue ? 'hidden' : ''
	if (newValue) {
		console.log('PDF Viewer opened. Use SPACEBAR to toggle fullscreen, ESC to close.')
	}
})
</script>
