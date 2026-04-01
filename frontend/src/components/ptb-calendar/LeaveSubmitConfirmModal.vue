<template>
	<Teleport to="body">
		<div v-if="visible" class="fixed inset-0 z-[100001] flex items-center justify-center bg-black/55 p-4" @click.self="$emit('cancel')">
			<div class="w-full max-w-xl overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-900">
				<div class="border-b border-gray-200 bg-[linear-gradient(135deg,_rgba(16,185,129,0.12),_rgba(59,130,246,0.08))] px-6 py-5 dark:border-gray-700 dark:bg-[linear-gradient(135deg,_rgba(16,185,129,0.18),_rgba(30,41,59,0.95))]">
					<p class="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-700 dark:text-emerald-300">Leave Confirmation</p>
					<h3 class="mt-2 text-xl font-semibold text-gray-900 dark:text-white">
						{{ mode === 'update' ? 'Review leave update before sending' : 'Review leave request before sending' }}
					</h3>
					<p class="mt-2 text-sm leading-6 text-gray-600 dark:text-gray-300">
						The system will email the leave notification to leaders and assigned agents. Please confirm these details are correct before continuing.
					</p>
				</div>

				<div class="space-y-5 px-6 py-5">
					<div class="grid gap-3 md:grid-cols-2">
						<div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800/70">
							<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Employee</p>
							<p class="mt-2 text-sm font-semibold text-gray-900 dark:text-white">{{ employeeLabel }}</p>
						</div>
						<div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800/70">
							<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Leave Days</p>
							<p class="mt-2 text-sm font-semibold text-gray-900 dark:text-white">{{ summary.dates.length }} {{ summary.dates.length === 1 ? 'day' : 'days' }}</p>
						</div>
					</div>

					<section class="rounded-2xl border border-gray-200 bg-white px-4 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
						<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Dates</p>
						<p class="mt-2 text-sm leading-7 text-gray-900 dark:text-white">{{ formattedDates }}</p>
					</section>

					<section class="rounded-2xl border px-4 py-4 shadow-sm" :class="hasAgents ? 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800/70' : 'border-amber-200 bg-amber-50 dark:border-amber-500/40 dark:bg-amber-500/10'">
						<div class="flex items-start justify-between gap-4">
							<div>
								<p class="text-[11px] font-semibold uppercase tracking-[0.18em]" :class="hasAgents ? 'text-gray-500 dark:text-gray-400' : 'text-amber-700 dark:text-amber-300'">Agents</p>
								<p class="mt-2 text-sm leading-7" :class="hasAgents ? 'text-gray-900 dark:text-white' : 'font-semibold text-amber-900 dark:text-amber-100'">{{ agentLabel }}</p>
							</div>
							<span v-if="!hasAgents" class="rounded-full bg-amber-200 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-amber-800 dark:bg-amber-400/20 dark:text-amber-200">No agent yet</span>
						</div>
						<p v-if="!hasAgents" class="mt-3 text-sm leading-6 text-amber-800 dark:text-amber-100">
							You can still continue, but the confirmation is highlighting this because no coverage agent has been entered yet.
						</p>
					</section>

					<section class="rounded-2xl border border-gray-200 bg-white px-4 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800/70">
						<p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Notes</p>
						<p class="mt-2 text-sm leading-7 text-gray-900 dark:text-white">{{ summary.notes?.trim() || '-' }}</p>
					</section>
				</div>

				<div class="flex gap-3 border-t border-gray-200 bg-gray-50 px-6 py-4 dark:border-gray-700 dark:bg-gray-900/80">
					<button type="button" class="h-11 flex-1 rounded-xl border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700" @click="$emit('cancel')">
						Go Back
					</button>
					<button type="button" class="h-11 flex-1 rounded-xl bg-emerald-600 px-4 text-sm font-semibold text-white transition hover:bg-emerald-700" @click="$emit('confirm')">
						{{ mode === 'update' ? 'Confirm Update' : 'Confirm Submission' }}
					</button>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface LeaveConfirmationSummary {
	employeeName: string
	employeeId?: string
	dates: string[]
	agents: string[]
	notes?: string
}

interface Props {
	visible: boolean
	mode: 'create' | 'update'
	summary: LeaveConfirmationSummary
}

const props = defineProps<Props>()

defineEmits<{
	(e: 'confirm'): void
	(e: 'cancel'): void
}>()

const employeeLabel = computed(() =>
	props.summary.employeeId?.trim()
		? `${props.summary.employeeName} (${props.summary.employeeId.trim()})`
		: props.summary.employeeName,
)

const formattedDates = computed(() =>
	props.summary.dates
		.map((dateValue) =>
			new Intl.DateTimeFormat(undefined, {
				weekday: 'short',
				month: 'short',
				day: 'numeric',
				year: 'numeric',
			}).format(new Date(dateValue)),
		)
		.join(', '),
)

const hasAgents = computed(() => props.summary.agents.length > 0)
const agentLabel = computed(() => (hasAgents.value ? props.summary.agents.join(', ') : 'No agent entered'))
</script>