<template>
	<Teleport to="body">
		<div class="fixed inset-0 z-[100000] flex items-center justify-center p-4">
			<div class="absolute inset-0 bg-black/50" @click="$emit('close')"></div>
			<div
				role="dialog"
				aria-modal="true"
				aria-labelledby="leave-details-modal-title"
				class="relative z-10 flex max-h-[90vh] w-full max-w-4xl flex-col rounded-3xl border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-900"
			>
				<div class="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4 dark:border-gray-700 dark:bg-gray-900 rounded-t-3xl">
					<div>
						<h2 id="leave-details-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white">
						{{ t('calendar.leaveDetailsTitle') }}
						</h2>
						<p class="mt-1 text-sm font-bold text-gray-500 dark:text-gray-400">{{ leave.employee_name }} • {{ leaveMonthLabel }} • {{ relevantDates.length }} {{ t('calendar.daysLabel') }}</p>
					</div>
					<button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
						<XIcon class="w-6 h-6" />
					</button>
				</div>

				<div class="flex-1 overflow-y-auto px-6 py-5">
					<div class="space-y-5">
						<div class="rounded-3xl border border-cyan-100 bg-[linear-gradient(135deg,_rgba(236,254,255,0.95),_rgba(248,250,252,0.98))] p-5 dark:border-cyan-500/20 dark:bg-[linear-gradient(135deg,_rgba(8,47,73,0.38),_rgba(15,23,42,0.92))]">
							<div class="grid gap-4 md:grid-cols-3">
								<div class="rounded-2xl bg-white/80 px-4 py-3 shadow-sm ring-1 ring-white/60 dark:bg-white/5 dark:ring-white/10">
									<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-cyan-700 dark:text-cyan-300">{{ t('calendar.leaveForm.employee') }}</p>
									<p class="mt-2 text-base font-semibold text-gray-900 dark:text-white">{{ leave.employee_name }}</p>
								</div>
								<div class="rounded-2xl bg-white/80 px-4 py-3 shadow-sm ring-1 ring-white/60 dark:bg-white/5 dark:ring-white/10">
									<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-cyan-700 dark:text-cyan-300">Employee ID</p>
									<p class="mt-2 text-base font-medium text-gray-900 dark:text-white">{{ leave.employee_emp_id || '-' }}</p>
								</div>
								<div class="rounded-2xl bg-white/80 px-4 py-3 shadow-sm ring-1 ring-white/60 dark:bg-white/5 dark:ring-white/10">
									<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-cyan-700 dark:text-cyan-300">{{ t('calendar.daysLabel') }}</p>
									<p class="mt-2 text-base font-semibold text-gray-900 dark:text-white">{{ relevantDates.length }}</p>
								</div>
							</div>
						</div>

						<div class="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
							<section class="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
								<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('calendar.leaveForm.dates') }}</p>
								<p class="mt-3 text-sm leading-7 text-gray-900 whitespace-pre-wrap dark:text-white">{{ formattedDates }}</p>
							</section>

							<section class="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
								<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('calendar.agent') }}</p>
								<p class="mt-3 text-sm leading-6 text-gray-900 dark:text-white"><span class="font-bold">{{ agentDisplay }}</span></p>
							</section>
						</div>

						<section class="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
							<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('calendar.leaveForm.notes') }}</p>
							<p class="mt-3 text-sm leading-7 text-gray-900 whitespace-pre-wrap dark:text-white">{{ leave.notes || '-' }}</p>
						</section>
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
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { XIcon } from '@/icons'
import type { EmployeeLeave } from '@/services/api/holiday'
import {
	formatLeaveSummaryDates,
	getLeaveAgentDisplay,
	LEAVE_AGENT_FALLBACK,
} from './leaveSummary'

interface Props {
	leave: EmployeeLeave
	relatedLeaves?: EmployeeLeave[]
	canEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	relatedLeaves: () => [],
	canEdit: false,
})

defineEmits<{
	(e: 'close'): void
	(e: 'edit'): void
}>()

const { t } = useI18n()

const weekdayLabels = computed(() => [
	t('calendar.daySun'),
	t('calendar.dayMon'),
	t('calendar.dayTue'),
	t('calendar.dayWed'),
	t('calendar.dayThu'),
	t('calendar.dayFri'),
	t('calendar.daySat'),
])

const relevantLeaves = computed(() =>
	(props.relatedLeaves.length > 0 ? props.relatedLeaves : [props.leave]).sort(
		(a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
	),
)

const relevantDates = computed(() => Array.from(new Set(relevantLeaves.value.map((leave) => leave.date))))

const agentDisplay = computed(() => {
	const agentNames = new Set<string>()
	for (const relatedLeave of relevantLeaves.value) {
		const display = getLeaveAgentDisplay(relatedLeave, LEAVE_AGENT_FALLBACK)
		if (display !== LEAVE_AGENT_FALLBACK) {
			display
				.split(',')
				.map((part) => part.trim())
				.filter(Boolean)
				.forEach((part) => agentNames.add(part))
		}
	}
	return agentNames.size > 0 ? [...agentNames].join(', ') : LEAVE_AGENT_FALLBACK
})

const formattedDates = computed(() =>
	formatLeaveSummaryDates(relevantDates.value, weekdayLabels.value, relevantDates.value.length || 1),
)

const leaveMonthLabel = computed(() => {
	if (relevantDates.value.length === 0) return '-'

	const labels = Array.from(
		new Set(
			relevantDates.value.map((dateValue) =>
				new Intl.DateTimeFormat(undefined, {
					month: 'short',
					year: 'numeric',
				}).format(new Date(dateValue)),
			),
		),
	)

	return labels.join(' / ')
})
</script>