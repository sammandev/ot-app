<template>
	<Teleport to="body">
		<div class="fixed inset-0 z-[100000] flex items-center justify-center p-4">
			<div class="absolute inset-0 bg-black/50" @click="$emit('close')"></div>
			<div
				role="dialog"
				aria-modal="true"
				aria-labelledby="holiday-details-modal-title"
				class="relative z-10 flex max-h-[90vh] w-full max-w-4xl flex-col rounded-3xl border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-900"
			>
				<div class="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4 dark:border-gray-700 dark:bg-gray-900 rounded-t-3xl">
					<div>
						<h2 id="holiday-details-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white">
						{{ t('calendar.holidayDetailsTitle') }}
						</h2>
						<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ holiday.title }}</p>
					</div>
					<button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
						<XIcon class="w-6 h-6" />
					</button>
				</div>

				<div class="flex-1 overflow-y-auto px-6 py-5">
					<div class="space-y-5">
						<div class="rounded-3xl border border-rose-100 bg-[linear-gradient(135deg,_rgba(255,241,242,0.98),_rgba(255,247,237,0.96))] p-5 dark:border-rose-500/20 dark:bg-[linear-gradient(135deg,_rgba(76,5,25,0.35),_rgba(67,20,7,0.4))]">
							<div class="flex items-start justify-between gap-4">
								<div>
									<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-rose-700 dark:text-rose-300">{{ t('calendar.holidayForm.holidayTitle') }}</p>
									<h3 class="mt-2 text-2xl font-semibold text-gray-900 dark:text-white">{{ holiday.title }}</h3>
									<p class="mt-2 text-sm text-gray-600 dark:text-gray-300">{{ holiday.description || '-' }}</p>
								</div>
								<div class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-2xl border border-white/70 bg-white/80 shadow-sm dark:border-white/10 dark:bg-white/10">
									<span class="h-5 w-5 rounded-full border border-gray-200 dark:border-gray-600" :style="{ backgroundColor: holiday.color || '#FFB6C1' }"></span>
								</div>
							</div>
						</div>

						<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
							<div class="rounded-2xl border border-gray-200 bg-white px-4 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
								<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('common.date') }}</p>
								<p class="mt-2 text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(holiday.date) }}</p>
							</div>
							<div class="rounded-2xl border border-gray-200 bg-white px-4 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
								<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('calendar.recurring') }}</p>
								<p class="mt-2 text-sm font-medium text-gray-900 dark:text-white">{{ holiday.is_recurring ? t('common.yes') : '-' }}</p>
							</div>
							<div class="rounded-2xl border border-gray-200 bg-white px-4 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
								<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('calendar.holidayForm.color') }}</p>
								<div class="mt-2 flex items-center gap-2">
									<span class="h-4 w-4 rounded-full border border-gray-200 dark:border-gray-600" :style="{ backgroundColor: holiday.color || '#FFB6C1' }"></span>
									<p class="text-sm font-medium text-gray-900 dark:text-white">{{ holiday.color || '#FFB6C1' }}</p>
								</div>
							</div>
							<div class="rounded-2xl border border-gray-200 bg-white px-4 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
								<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Created By</p>
								<p class="mt-2 text-sm font-medium text-gray-900 dark:text-white">{{ holiday.created_by_username || '-' }}</p>
							</div>
						</div>

						<div v-if="holiday.updated_at" class="rounded-2xl border border-gray-200 bg-white px-4 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
							<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Updated</p>
							<p class="mt-2 text-sm font-medium text-gray-900 dark:text-white">{{ formatDateTime(holiday.updated_at) }}</p>
						</div>
					</div>
				</div>

				<div class="sticky bottom-0 z-10 flex gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-b-2xl">
					<button class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5" @click="$emit('close')">
						{{ t('common.close') }}
					</button>
					<button v-if="canEdit" class="h-11 flex-1 rounded-lg bg-brand-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700" @click="$emit('edit')">
						{{ t('common.edit') }}
					</button>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { XIcon } from '@/icons'
import type { Holiday } from '@/services/api/holiday'

interface Props {
	holiday: Holiday
	canEdit?: boolean
}

defineProps<Props>()

defineEmits<{
	(e: 'close'): void
	(e: 'edit'): void
}>()

const { t } = useI18n()

const formatDate = (dateStr: string) =>
	new Date(dateStr).toLocaleDateString('en-US', {
		weekday: 'short',
		year: 'numeric',
		month: 'short',
		day: 'numeric',
	})

const formatDateTime = (dateStr: string) =>
	new Date(dateStr).toLocaleString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: '2-digit',
	})
</script>