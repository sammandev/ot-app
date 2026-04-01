<template>
	<div class="space-y-6">
		<div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
			<div class="flex items-center gap-4 border-b border-gray-200 px-6 py-5 dark:border-gray-800">
				<div class="rounded-xl bg-sky-100 p-3 dark:bg-sky-500/20">
					<svg class="h-6 w-6 text-sky-600 dark:text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8m-18 8h18a2 2 0 002-2V8a2 2 0 00-2-2H3a2 2 0 00-2 2v6a2 2 0 002 2z" />
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Email Notifications</h3>
					<p class="text-sm text-gray-500 dark:text-gray-400">Manage SMTP delivery, leave recipient routing, and reusable email templates.</p>
				</div>
			</div>

			<div class="p-6 space-y-6">
				<div class="grid grid-cols-1 gap-6 xl:grid-cols-[1.12fr_0.88fr]">
					<div class="space-y-6">
						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<div class="flex items-start justify-between gap-4">
								<div>
									<h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600 dark:text-sky-400">SMTP Connection</h4>
									<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">This host and port are used when notification emails are sent from the backend.</p>
								</div>
								<div class="rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700 dark:border-sky-500/30 dark:bg-sky-500/10 dark:text-sky-300">
									Live config
								</div>
							</div>
							<div class="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
								<div class="sm:col-span-2">
									<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">SMTP Host</label>
									<input v-model="form.notification_email_host" type="text" placeholder="mail.pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400" />
								</div>
								<div>
									<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">SMTP Port</label>
									<input v-model.number="form.notification_email_port" type="number" min="1" max="65535" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
								</div>
								<div>
									<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Sender Name</label>
									<input v-model="form.leave_notification_sender_name" type="text" placeholder="OMS" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400" />
								</div>
							</div>
							<p class="mt-4 text-xs text-gray-500 dark:text-gray-400">Email preview sender: {{ form.leave_notification_sender_name || 'OMS' }} &lt;no-reply@pegatroncorp.com&gt;</p>
						</div>

						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600 dark:text-sky-400">Leave Recipient Routing</h4>
							<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Select one routing mode for leave emails. Department mode resolves recipients using the leave employee department.</p>
							<div class="mt-5 grid grid-cols-1 gap-3 lg:grid-cols-3">
								<button v-for="mode in recipientModes" :key="mode.value" type="button" @click="form.leave_notification_recipient_mode = mode.value" :class="[
									'rounded-2xl border p-4 text-left transition',
									form.leave_notification_recipient_mode === mode.value
										? 'border-sky-500 bg-sky-50 shadow-sm dark:border-sky-400 dark:bg-sky-500/10'
										: 'border-gray-200 bg-white hover:border-sky-300 dark:border-gray-700 dark:bg-gray-900 dark:hover:border-sky-500/40'
								]">
									<div class="text-sm font-semibold text-gray-900 dark:text-white">{{ mode.label }}</div>
									<p class="mt-1 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ mode.description }}</p>
								</button>
							</div>

							<div v-if="form.leave_notification_recipient_mode === 'global'" class="mt-5">
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Global Recipients</label>
								<textarea v-model="globalRecipientsText" rows="5" placeholder="hr@pegatroncorp.com&#10;manager@pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400"></textarea>
								<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">These addresses receive every leave notification when Global mode is active.</p>
							</div>

							<div v-if="form.leave_notification_recipient_mode === 'custom'" class="mt-5">
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Custom Recipients</label>
								<textarea v-model="customRecipientsText" rows="5" placeholder="director@pegatroncorp.com&#10;assistant@pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400"></textarea>
								<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">Use Custom mode when leave notifications should follow a leave-only recipient list.</p>
							</div>

							<div v-if="form.leave_notification_recipient_mode === 'department'" class="mt-5 space-y-4">
								<div class="flex items-center justify-between gap-3">
									<div>
										<label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Department Recipient Mapping</label>
										<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Leave a department blank if it should not send email in department mode.</p>
									</div>
									<div class="text-xs text-gray-400">{{ enabledDepartments.length }} department{{ enabledDepartments.length === 1 ? '' : 's' }}</div>
								</div>
								<div class="grid grid-cols-1 gap-3 xl:grid-cols-2">
									<div v-for="department in enabledDepartments" :key="department.code" class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
										<div class="flex items-start justify-between gap-3">
											<div>
												<h5 class="text-sm font-semibold text-gray-900 dark:text-white">{{ department.name }}</h5>
												<p class="mt-1 text-xs uppercase tracking-[0.16em] text-gray-400">{{ department.code }}</p>
											</div>
											<span class="rounded-full bg-gray-100 px-2.5 py-1 text-[11px] font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">Department mode</span>
										</div>
										<textarea v-model="departmentRecipientTexts[department.code]" rows="4" class="mt-3 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:placeholder-gray-400" :placeholder="`${department.code.toLowerCase()}@pegatroncorp.com`"></textarea>
									</div>
								</div>
							</div>

							<p class="mt-4 text-xs text-gray-500 dark:text-gray-400">Enter one address per line or separate multiple addresses with commas. Only @pegatroncorp.com addresses are allowed.</p>
						</div>
					</div>

					<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
						<h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600 dark:text-sky-400">Template Variables</h4>
						<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Use these placeholders inside subject, body, and footer to keep emails polished and reusable.</p>
						<div class="mt-5 flex flex-wrap gap-2">
							<span v-for="variable in templateVariables" :key="variable" class="rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700 dark:border-sky-500/30 dark:bg-sky-500/10 dark:text-sky-300">{{ variable }}</span>
						</div>
					</div>
				</div>

				<div class="space-y-6">
					<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
						<h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600 dark:text-sky-400">Email Templates</h4>
						<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Shape the leave subject, body, and footer into a professional message that can grow with future notification types. Details and preview links are appended automatically by the system.</p>
						<div class="mt-5 space-y-4">
							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Subject</label>
								<input v-model="form.leave_notification_subject_template" type="text" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
							</div>
							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Body</label>
								<textarea v-model="form.leave_notification_body_template" rows="12" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white"></textarea>
								<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">Do not add manual <span class="font-semibold">Details:</span> or <span class="font-semibold">Preview:</span> lines here. The backend appends those links automatically.</p>
							</div>
							<div>
								<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Footer</label>
								<textarea v-model="form.leave_notification_footer_template" rows="6" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white"></textarea>
							</div>
						</div>
					</div>

					<div class="rounded-2xl border border-sky-200 bg-sky-50/70 p-5 dark:border-sky-500/20 dark:bg-sky-500/10">
						<h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700 dark:text-sky-300">Professional Format Guidance</h4>
						<ul class="mt-3 space-y-2 text-sm text-sky-900 dark:text-sky-100">
							<li>Lead with a direct subject that shows the action and the employee immediately.</li>
							<li>Keep the body operational: who, department, dates, day count, coverage, and note.</li>
							<li>Use the footer for consistent sign-off text that can be reused across future notification features.</li>
						</ul>
					</div>
				</div>
			</div>

			<div class="flex justify-end gap-3 border-t border-gray-200 pt-6 dark:border-gray-800">
				<button @click="initFromConfig" type="button" class="h-11 rounded-lg border border-gray-300 bg-white px-5 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-gray-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">Reset</button>
				<button @click="saveSettings" :disabled="configStore.loading || departmentStore.loading" type="button" class="h-11 rounded-lg bg-sky-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-sky-700 focus:outline-hidden focus:ring-3 focus:ring-sky-500/20 disabled:cursor-not-allowed disabled:opacity-50">
					<span v-if="!configStore.loading">Save Email Notifications</span>
					<span v-else>Saving...</span>
				</button>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfigStore } from '@/stores/config'
import { useDepartmentStore } from '@/stores/department'
import { extractApiError } from '@/utils/extractApiError'

const configStore = useConfigStore()
const departmentStore = useDepartmentStore()
const { showToast } = useToast()

const recipientModes = [
	{ value: 'global' as const, label: 'Global', description: 'One shared recipient list is used for every leave notification.' },
	{ value: 'department' as const, label: 'Department', description: 'Recipients are resolved from the leave employee department.' },
	{ value: 'custom' as const, label: 'Custom', description: 'Use a dedicated leave-only recipient list outside the department mapping.' },
]

const templateVariables = [
	'{action_label}',
	'{action_label_lower}',
	'{employee_name}',
	'{employee_id}',
	'{department_name}',
	'{department_code}',
	'{leave_dates}',
	'{leave_day_count}',
	'{leave_day_label}',
	'{agents}',
	'{note}',
	'{submitted_by}',
	'{updated_by}',
	'{updated_by_line}',
	'{sender_name}',
]

const form = reactive({
	notification_email_host: 'mail.pegatroncorp.com',
	notification_email_port: 25,
	leave_notification_sender_name: 'OMS',
	leave_notification_recipient_mode: 'global' as 'global' | 'department' | 'custom',
	leave_notification_subject_template: '',
	leave_notification_body_template: '',
	leave_notification_footer_template: '',
})

const globalRecipientsText = ref('')
const customRecipientsText = ref('')
const departmentRecipientTexts = reactive<Record<string, string>>({})
const enabledDepartments = computed(() => departmentStore.enabledDepartments)

const normalizeRecipientInput = (value: string) =>
	Array.from(
		new Set(
			value
				.split(/[\n,]/)
				.map((email) => email.trim().toLowerCase())
				.filter(Boolean),
		),
	)

const initFromConfig = () => {
	form.notification_email_host = configStore.notificationEmailHost
	form.notification_email_port = configStore.notificationEmailPort
	form.leave_notification_sender_name = configStore.leaveNotificationSenderName
	form.leave_notification_recipient_mode = configStore.leaveNotificationRecipientMode
	form.leave_notification_subject_template = configStore.leaveNotificationSubjectTemplate
	form.leave_notification_body_template = configStore.leaveNotificationBodyTemplate
	form.leave_notification_footer_template = configStore.leaveNotificationFooterTemplate
	globalRecipientsText.value = configStore.leaveNotificationRecipients.join('\n')
	customRecipientsText.value = configStore.leaveNotificationCustomRecipients.join('\n')

	for (const key of Object.keys(departmentRecipientTexts)) {
		delete departmentRecipientTexts[key]
	}
	for (const mapping of configStore.leaveNotificationDepartmentRecipients) {
		departmentRecipientTexts[mapping.department_code] = mapping.recipients.join('\n')
	}
	for (const department of enabledDepartments.value) {
		if (!(department.code in departmentRecipientTexts)) {
			departmentRecipientTexts[department.code] = ''
		}
	}
}

const saveSettings = async () => {
	const globalRecipients = normalizeRecipientInput(globalRecipientsText.value)
	const customRecipients = normalizeRecipientInput(customRecipientsText.value)
	const departmentRecipients = enabledDepartments.value
		.map((department) => ({
			department_code: department.code,
			recipients: normalizeRecipientInput(departmentRecipientTexts[department.code] || ''),
		}))
		.filter((entry) => entry.recipients.length > 0)

	const activeRecipients =
		form.leave_notification_recipient_mode === 'global'
			? globalRecipients
			: form.leave_notification_recipient_mode === 'custom'
				? customRecipients
				: departmentRecipients.flatMap((entry) => entry.recipients)

	const invalidRecipients = activeRecipients.filter((email) => !email.endsWith('@pegatroncorp.com'))
	if (invalidRecipients.length > 0) {
		showToast('Notification recipients must use the @pegatroncorp.com domain', 'error')
		return
	}
	if (!form.leave_notification_sender_name.trim()) {
		showToast('Notification sender name is required', 'error')
		return
	}
	if (!form.notification_email_host.trim()) {
		showToast('SMTP host is required', 'error')
		return
	}
	if (form.notification_email_port < 1 || form.notification_email_port > 65535) {
		showToast('SMTP port must be between 1 and 65535', 'error')
		return
	}
	if (form.leave_notification_recipient_mode === 'global' && globalRecipients.length === 0) {
		showToast('Global mode requires at least one recipient', 'error')
		return
	}
	if (form.leave_notification_recipient_mode === 'custom' && customRecipients.length === 0) {
		showToast('Custom mode requires at least one recipient', 'error')
		return
	}
	if (form.leave_notification_recipient_mode === 'department' && departmentRecipients.length === 0) {
		showToast('Department mode requires at least one department recipient mapping', 'error')
		return
	}

	try {
		await configStore.updateConfig({
			notification_email_host: form.notification_email_host.trim(),
			notification_email_port: form.notification_email_port,
			leave_notification_sender_name: form.leave_notification_sender_name.trim(),
			leave_notification_recipient_mode: form.leave_notification_recipient_mode,
			leave_notification_recipients: globalRecipients,
			leave_notification_custom_recipients: customRecipients,
			leave_notification_department_recipients: departmentRecipients,
			leave_notification_subject_template: form.leave_notification_subject_template,
			leave_notification_body_template: form.leave_notification_body_template,
			leave_notification_footer_template: form.leave_notification_footer_template,
		})
		await configStore.fetchConfig(true)
		initFromConfig()
		showToast('Email notification settings saved successfully', 'success')
	} catch (err) {
		console.error('Failed to save email notification settings:', err)
		showToast(extractApiError(err, 'Failed to save email notification settings'), 'error', 5000)
	}
}

defineExpose({ initFromConfig })

onMounted(async () => {
	try {
		await Promise.all([configStore.fetchConfig(), departmentStore.fetchDepartments()])
	} catch (error) {
		console.error('Failed to load email notification config:', error)
	}
	initFromConfig()
})
</script>