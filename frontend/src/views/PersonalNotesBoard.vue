<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.personalNotes.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">📝 {{ t('pages.personalNotes.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.personalNotes.subtitle') }}</p>
                </div>

                <div class="flex items-center gap-3">
                    <!-- View Toggle -->
                    <div
                        class="flex bg-white dark:bg-gray-900 rounded-lg p-1 shadow-theme-xs border border-gray-200 dark:border-gray-700">
                        <button @click="viewMode = 'grid'" :class="['px-3 py-1.5 rounded text-sm transition',
                            viewMode === 'grid'
                                ? 'bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300'
                                : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']">
                            📦 Grid
                        </button>
                        <button @click="viewMode = 'list'" :class="['px-3 py-1.5 rounded text-sm transition',
                            viewMode === 'list'
                                ? 'bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300'
                                : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']">
                            📋 List
                        </button>
                    </div>

                    <!-- Add Note Button -->
                    <button @click="openCreateModal"
                        class="flex h-11 items-center justify-center gap-2 rounded-lg bg-brand-600 px-5 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10">
                        <span class="text-lg">+</span>
                        <span>New Note</span>
                    </button>
                </div>
            </div>

            <!-- Filters -->
            <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex flex-wrap gap-2">
                    <button @click="filter = 'all'"
                        :class="['px-4 py-2 rounded-lg text-sm font-medium transition shadow-theme-xs',
                            filter === 'all'
                                ? 'bg-brand-600 text-white'
                                : 'border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800']">
                        All Notes ({{ notes.length }})
                    </button>
                    <button @click="filter = 'pinned'"
                        :class="['px-4 py-2 rounded-lg text-sm font-medium transition shadow-theme-xs',
                            filter === 'pinned'
                                ? 'bg-brand-600 text-white'
                                : 'border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800']">
                        📌 Pinned ({{notes.filter(n => n.is_pinned).length}})
                    </button>
                    <button @click="filter = 'active'"
                        :class="['px-4 py-2 rounded-lg text-sm font-medium transition shadow-theme-xs',
                            filter === 'active'
                                ? 'bg-brand-600 text-white'
                                : 'border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800']">
                        🔵 Active ({{notes.filter(n => !n.is_completed).length}})
                    </button>
                    <button @click="filter = 'completed'"
                        :class="['px-4 py-2 rounded-lg text-sm font-medium transition shadow-theme-xs',
                            filter === 'completed'
                                ? 'bg-brand-600 text-white'
                                : 'border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800']">
                        ✅ Completed ({{notes.filter(n => n.is_completed).length}})
                    </button>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="flex items-center justify-center py-20">
                <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-600"></div>
            </div>

            <!-- Empty State -->
            <div v-else-if="filteredNotes.length === 0"
                class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] text-center py-20">
                <div class="text-6xl mb-4">📝</div>
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">No notes yet</h3>
                <p class="text-gray-500 dark:text-gray-400 mb-6">Create your first note to get started!</p>
                <button @click="openCreateModal"
                    class="px-6 py-3 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition font-semibold">
                    Create Note
                </button>
            </div>

            <!-- Grid View -->
            <div v-else-if="viewMode === 'grid'"
                class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <div v-for="note in filteredNotes" :key="note.id"
                    :style="{ backgroundColor: note.color + '20', borderLeftColor: note.color }" :class="['relative p-4 rounded-xl border-l-4 shadow-theme-xs cursor-pointer transition hover:shadow-md group',
                        note.is_completed ? 'opacity-60' : '']" @click="openEditModal(note)">

                    <!-- Pin Icon -->
                    <button v-if="note.is_pinned" @click.stop="togglePin(note)" class="absolute top-2 right-2 text-lg">
                        📌
                    </button>

                    <!-- Completed Check -->
                    <div v-if="note.is_completed" class="absolute top-2 right-2 text-lg">
                        ✅
                    </div>

                    <!-- Title -->
                    <h3 :class="['font-semibold text-gray-900 dark:text-white mb-2 pr-8',
                        note.is_completed ? 'line-through' : '']">
                        {{ note.title }}
                    </h3>

                    <!-- Content Preview -->
                    <p v-if="note.content" class="text-sm text-gray-600 dark:text-gray-400 line-clamp-3 mb-3">
                        {{ note.content }}
                    </p>

                    <!-- Due Date -->
                    <div v-if="note.due_date" class="text-xs text-gray-500 flex items-center gap-1">
                        <span>📅</span>
                        <span :class="isOverdue(note.due_date) && !note.is_completed ? 'text-red-500 font-medium' : ''">
                            {{ formatDate(note.due_date) }}
                        </span>
                    </div>

                    <!-- Actions (visible on hover) -->
                    <div class="absolute bottom-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition">
                        <button @click.stop="togglePin(note)"
                            class="p-1.5 hover:bg-white/50 dark:hover:bg-gray-700/50 rounded text-sm"
                            :title="note.is_pinned ? 'Unpin' : 'Pin'">
                            {{ note.is_pinned ? '📌' : '📍' }}
                        </button>
                        <button @click.stop="toggleComplete(note)"
                            class="p-1.5 hover:bg-white/50 dark:hover:bg-gray-700/50 rounded text-sm"
                            :title="note.is_completed ? 'Mark Active' : 'Mark Complete'">
                            {{ note.is_completed ? '🔄' : '✅' }}
                        </button>
                        <button @click.stop="deleteNote(note.id)"
                            class="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded text-sm text-red-500">
                            🗑️
                        </button>
                    </div>
                </div>
            </div>

            <!-- List View -->
            <div v-else class="space-y-2">
                <div v-for="note in filteredNotes" :key="note.id" :class="['rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/[0.03] shadow-theme-xs p-4 flex items-start gap-4 cursor-pointer transition hover:shadow-md group',
                    note.is_completed ? 'opacity-60' : '']" @click="openEditModal(note)">

                    <!-- Color Indicator -->
                    <div :style="{ backgroundColor: note.color }" class="w-3 h-3 rounded-full mt-1.5 flex-shrink-0">
                    </div>

                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2">
                            <h3 :class="['font-semibold text-gray-900 dark:text-white',
                                note.is_completed ? 'line-through' : '']">
                                {{ note.title }}
                            </h3>
                            <span v-if="note.is_pinned" class="text-sm">📌</span>
                            <span v-if="note.is_completed" class="text-sm">✅</span>
                        </div>
                        <p v-if="note.content" class="text-sm text-gray-600 dark:text-gray-400 truncate mt-1">
                            {{ note.content }}
                        </p>
                    </div>

                    <!-- Due Date -->
                    <div v-if="note.due_date" class="text-sm text-gray-500 flex-shrink-0">
                        <span :class="isOverdue(note.due_date) && !note.is_completed ? 'text-red-500 font-medium' : ''">
                            {{ formatDate(note.due_date) }}
                        </span>
                    </div>

                    <!-- Actions -->
                    <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition">
                        <button @click.stop="togglePin(note)"
                            class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded text-sm">
                            {{ note.is_pinned ? '📌' : '📍' }}
                        </button>
                        <button @click.stop="toggleComplete(note)"
                            class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded text-sm">
                            {{ note.is_completed ? '🔄' : '✅' }}
                        </button>
                        <button @click.stop="deleteNote(note.id)"
                            class="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded text-sm text-red-500">
                            🗑️
                        </button>
                    </div>
                </div>
            </div>

            <!-- Create/Edit Modal -->
            <Teleport to="body">
                <Transition name="fade">
                    <div v-if="showModal" class="fixed inset-0 z-[100000] flex items-center justify-center p-4">
                        <!-- Backdrop -->
                        <div class="absolute inset-0 bg-black/50" @click="closeModal"></div>

                        <!-- Modal -->
                        <div
                            class="relative rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 shadow-2xl w-full max-w-lg">
                            <!-- Header -->
                            <div
                                class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                                    {{ editingNote ? 'Edit Note' : 'New Note' }}
                                </h3>
                                <button @click="closeModal"
                                    class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
                                    ✕
                                </button>
                            </div>

                            <!-- Form -->
                            <div class="p-4 space-y-4">
                                <!-- Title -->
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title
                                        *</label>
                                    <input v-model="form.title" type="text" placeholder="Note title..."
                                        class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm text-gray-800 dark:text-white shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10" />
                                </div>

                                <!-- Content -->
                                <div>
                                    <label
                                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Content</label>
                                    <textarea v-model="form.content" rows="4" placeholder="Write your note..."
                                        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm text-gray-800 dark:text-white shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 resize-none">
                                </textarea>
                                </div>

                                <!-- Color -->
                                <div>
                                    <label
                                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Color</label>
                                    <div class="flex gap-2">
                                        <button v-for="color in colors" :key="color" @click="form.color = color"
                                            :style="{ backgroundColor: color }"
                                            :class="['w-8 h-8 rounded-full transition transform',
                                                form.color === color ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : 'hover:scale-105']">
                                        </button>
                                    </div>
                                </div>

                                <!-- Due Date -->
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Due
                                        Date (optional)</label>
                                    <input v-model="form.due_date" type="date"
                                        class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm text-gray-800 dark:text-white shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10" />
                                </div>
                            </div>

                            <!-- Footer -->
                            <div class="flex justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
                                <button @click="closeModal"
                                    class="h-11 whitespace-nowrap rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-5 text-sm font-semibold text-gray-800 dark:text-gray-300 shadow-theme-xs transition hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10">
                                    Cancel
                                </button>
                                <button @click="saveNote" :disabled="!form.title.trim() || saving"
                                    class="h-11 rounded-lg bg-brand-600 px-5 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:opacity-50 disabled:cursor-not-allowed">
                                    {{ saving ? 'Saving...' : (editingNote ? 'Update' : 'Create') }}
                                </button>
                            </div>
                        </div>
                    </div>
                </Transition>
            </Teleport>
        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { type PersonalNote, personalNoteAPI } from '@/services/api'

// State
const { t } = useI18n()
const notes = ref<PersonalNote[]>([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editingNote = ref<PersonalNote | null>(null)
const viewMode = ref<'grid' | 'list'>('grid')
const filter = ref<'all' | 'pinned' | 'active' | 'completed'>('all')

// Form
const form = ref({
	title: '',
	content: '',
	color: '#FFEB3B',
	due_date: '',
})

// Color options
const colors = [
	'#FFEB3B', // Yellow
	'#FF9800', // Orange
	'#F44336', // Red
	'#E91E63', // Pink
	'#9C27B0', // Purple
	'#673AB7', // Deep Purple
	'#3F51B5', // Indigo
	'#2196F3', // Blue
	'#00BCD4', // Cyan
	'#009688', // Teal
	'#4CAF50', // Green
	'#8BC34A', // Light Green
]

// Computed
const filteredNotes = computed(() => {
	let result = [...notes.value]

	switch (filter.value) {
		case 'pinned':
			result = result.filter((n) => n.is_pinned)
			break
		case 'active':
			result = result.filter((n) => !n.is_completed)
			break
		case 'completed':
			result = result.filter((n) => n.is_completed)
			break
	}

	// Sort: pinned first, then by order
	return result.sort((a, b) => {
		if (a.is_pinned && !b.is_pinned) return -1
		if (!a.is_pinned && b.is_pinned) return 1
		return a.order - b.order
	})
})

// Load notes
onMounted(async () => {
	await loadNotes()
})

async function loadNotes() {
	loading.value = true
	try {
		notes.value = await personalNoteAPI.list()
	} catch (error) {
		console.error('Failed to load notes:', error)
	} finally {
		loading.value = false
	}
}

// Modal functions
function openCreateModal() {
	editingNote.value = null
	form.value = {
		title: '',
		content: '',
		color: '#FFEB3B',
		due_date: '',
	}
	showModal.value = true
}

function openEditModal(note: PersonalNote) {
	editingNote.value = note
	form.value = {
		title: note.title,
		content: note.content || '',
		color: note.color,
		due_date: note.due_date || '',
	}
	showModal.value = true
}

function closeModal() {
	showModal.value = false
	editingNote.value = null
}

async function saveNote() {
	if (!form.value.title.trim()) return

	saving.value = true
	try {
		if (editingNote.value) {
			// Update existing note
			const updated = await personalNoteAPI.update(editingNote.value.id, {
				title: form.value.title,
				content: form.value.content || undefined,
				color: form.value.color,
				due_date: form.value.due_date || undefined,
			})

			const index = notes.value.findIndex((n) => n.id === editingNote.value?.id)
			if (index !== -1) {
				notes.value[index] = updated
			}
		} else {
			// Create new note
			const created = await personalNoteAPI.create({
				title: form.value.title,
				content: form.value.content || undefined,
				color: form.value.color,
				due_date: form.value.due_date || undefined,
			})
			notes.value.unshift(created)
		}

		closeModal()
	} catch (error) {
		console.error('Failed to save note:', error)
	} finally {
		saving.value = false
	}
}

async function deleteNote(id: number) {
	if (!confirm('Delete this note?')) return

	try {
		await personalNoteAPI.delete(id)
		notes.value = notes.value.filter((n) => n.id !== id)
	} catch (error) {
		console.error('Failed to delete note:', error)
	}
}

async function togglePin(note: PersonalNote) {
	try {
		const updated = await personalNoteAPI.togglePin(note.id)
		const index = notes.value.findIndex((n) => n.id === note.id)
		if (index !== -1) {
			notes.value[index] = updated
		}
	} catch (error) {
		console.error('Failed to toggle pin:', error)
	}
}

async function toggleComplete(note: PersonalNote) {
	try {
		const updated = await personalNoteAPI.toggleComplete(note.id)
		const index = notes.value.findIndex((n) => n.id === note.id)
		if (index !== -1) {
			notes.value[index] = updated
		}
	} catch (error) {
		console.error('Failed to toggle complete:', error)
	}
}

// Helpers
function formatDate(dateStr: string): string {
	return new Date(dateStr).toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
	})
}

function isOverdue(dateStr: string): boolean {
	return new Date(dateStr) < new Date()
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>
