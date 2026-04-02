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

			<div class="space-y-6 p-6">
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

						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<div class="flex items-start justify-between gap-4">
								<div>
									<h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600 dark:text-sky-400">Employee Groups</h4>
									<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Create reusable employee groups with their own notification recipients. These group recipients are merged with the selected routing mode and the assigned leave agents.</p>
								</div>
								<button type="button" @click="addEmployeeGroup" class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-700">
									Add Group
								</button>
							</div>

							<div v-if="employeeGroupForms.length === 0" class="mt-5 rounded-xl border border-dashed border-gray-300 px-4 py-6 text-sm text-gray-500 dark:border-gray-700 dark:text-gray-400">
								No custom employee groups configured.
							</div>

							<div v-else class="mt-5 space-y-4">
								<div v-for="(group, index) in employeeGroupForms" :key="group.id" class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
									<div class="flex items-start justify-between gap-3">
										<div>
											<p class="text-sm font-semibold text-gray-900 dark:text-white">Group {{ index + 1 }}</p>
											<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ group.employee_ids.length }} employee{{ group.employee_ids.length === 1 ? '' : 's' }} selected</p>
										</div>
										<button type="button" @click="removeEmployeeGroup(index)" class="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-50 dark:border-red-500/30 dark:text-red-300 dark:hover:bg-red-500/10">
											Remove
										</button>
									</div>
									<div class="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
										<div>
											<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Group Name</label>
											<input v-model="group.name" type="text" placeholder="Night Shift Team" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white" />
										</div>
										<div>
											<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Group Recipients</label>
											<textarea v-model="group.recipientsText" rows="4" placeholder="teamlead@pegatroncorp.com&#10;backup@pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white"></textarea>
										</div>
									</div>
									<div class="mt-4">
										<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Employees in Group</label>
										<select v-model="group.employee_ids" multiple class="block min-h-40 w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white">
											<option v-for="employee in availableEmployees" :key="employee.id" :value="employee.id">
												{{ formatEmployeeLabel(employee) }}
											</option>
										</select>
										<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">Hold Ctrl or Cmd to select multiple employees.</p>
									</div>
								</div>
							</div>
						</div>

						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<div class="flex items-start justify-between gap-4">
								<div>
									<h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600 dark:text-sky-400">Employee-Specific Recipients</h4>
									<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Add direct recipients for specific employees and optionally attach one or more custom employee groups. These recipients are merged with the active routing mode and default agent recipients.</p>
								</div>
								<button type="button" @click="addEmployeeRecipientMapping" class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-700">
									Add Employee Rule
								</button>
							</div>

							<div v-if="employeeRecipientForms.length === 0" class="mt-5 rounded-xl border border-dashed border-gray-300 px-4 py-6 text-sm text-gray-500 dark:border-gray-700 dark:text-gray-400">
								No employee-specific leave recipient rules configured.
							</div>

							<div v-else class="mt-5 space-y-4">
								<div v-for="(mapping, index) in employeeRecipientForms" :key="mapping.key" class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
									<div class="flex items-start justify-between gap-3">
										<p class="text-sm font-semibold text-gray-900 dark:text-white">Employee Rule {{ index + 1 }}</p>
										<button type="button" @click="removeEmployeeRecipientMapping(index)" class="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-50 dark:border-red-500/30 dark:text-red-300 dark:hover:bg-red-500/10">
											Remove
										</button>
									</div>
									<div class="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
										<div>
											<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Employee</label>
											<select v-model="mapping.employee_id" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white">
												<option :value="null">Select employee</option>
												<option v-for="employee in availableEmployees" :key="employee.id" :value="employee.id">
													{{ formatEmployeeLabel(employee) }}
												</option>
											</select>
										</div>
										<div>
											<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Direct Recipients</label>
											<textarea v-model="mapping.recipientsText" rows="4" placeholder="manager@pegatroncorp.com&#10;delegate@pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white"></textarea>
										</div>
									</div>
									<div class="mt-4">
										<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Linked Custom Groups</label>
										<select v-model="mapping.group_ids" multiple :disabled="employeeGroupForms.length === 0" class="block min-h-32 w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-700 dark:bg-gray-950 dark:text-white">
											<option v-for="group in employeeGroupForms" :key="group.id" :value="group.id">
												{{ group.name.trim() || 'Untitled group' }}
											</option>
										</select>
										<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">Link groups when this employee should receive the recipients defined on those reusable group rules.</p>
									</div>
								</div>
							</div>
						</div>
					</div>

					<div class="space-y-6">
						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600 dark:text-sky-400">Template Variables</h4>
							<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Use these placeholders inside subject, body, and footer to keep emails polished and reusable.</p>
							<div class="mt-5 flex flex-wrap gap-2">
								<span v-for="variable in templateVariables" :key="variable" class="rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700 dark:border-sky-500/30 dark:bg-sky-500/10 dark:text-sky-300">{{ variable }}</span>
							</div>
						</div>

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
					<button @click="saveSettings" :disabled="configStore.loading || departmentStore.loading || employeeLoading" type="button" class="h-11 rounded-lg bg-sky-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-sky-700 focus:outline-hidden focus:ring-3 focus:ring-sky-500/20 disabled:cursor-not-allowed disabled:opacity-50">
						<span v-if="!configStore.loading">Save Email Notifications</span>
						<span v-else>Saving...</span>
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useToast } from '@/composables/useToast'
import { type Employee, employeeAPI } from '@/services/api/employee'
import {
	type LeaveNotificationEmployeeGroup,
	type LeaveNotificationEmployeeRecipient,
	useConfigStore,
} from '@/stores/config'
import { useDepartmentStore } from '@/stores/department'
import { extractApiError } from '@/utils/extractApiError'

interface EmployeeGroupForm {
	id: string
	name: string
	employee_ids: number[]
	recipientsText: string
}

interface EmployeeRecipientForm {
	key: string
	employee_id: number | null
	recipientsText: string
	group_ids: string[]
}

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
const employeeGroupForms = ref<EmployeeGroupForm[]>([])
const employeeRecipientForms = ref<EmployeeRecipientForm[]>([])
const employees = ref<Employee[]>([])
const employeeLoading = ref(false)

const enabledDepartments = computed(() => departmentStore.enabledDepartments)
const availableEmployees = computed(() =>
	employees.value
		.filter((employee) => employee.is_enabled)
		.slice()
		.sort((a, b) => formatEmployeeLabel(a).localeCompare(formatEmployeeLabel(b))),
)

const buildLocalKey = (prefix: string) => `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

const createEmptyEmployeeGroup = (): EmployeeGroupForm => ({
	id: buildLocalKey('group'),
	name: '',
	employee_ids: [],
	recipientsText: '',
})

const createEmptyEmployeeRecipient = (): EmployeeRecipientForm => ({
	key: buildLocalKey('mapping'),
	employee_id: null,
	recipientsText: '',
	group_ids: [],
})

const normalizeRecipientInput = (value: string) =>
	Array.from(
		new Set(
			value
				.split(/[\n,]/)
				.map((email) => email.trim().toLowerCase())
				.filter(Boolean),
		),
	)

const toRecipientText = (recipients: string[]) => recipients.join('\n')

const formatEmployeeLabel = (employee: Employee) => `${employee.name} (${employee.emp_id})`

const loadAllEmployees = async () => {
	employeeLoading.value = true
	try {
		const loadedEmployees: Employee[] = []
		let page = 1
		while (true) {
			const response = await employeeAPI.list({ page, page_size: 500, ordering: 'name' })
			loadedEmployees.push(...response.results)
			if (response.results.length < 500) break
			page += 1
		}
		employees.value = loadedEmployees
	} finally {
		employeeLoading.value = false
	}
}

const addEmployeeGroup = () => {
	employeeGroupForms.value.push(createEmptyEmployeeGroup())
}

const removeEmployeeGroup = (index: number) => {
	const [removed] = employeeGroupForms.value.splice(index, 1)
	if (!removed) return
	for (const mapping of employeeRecipientForms.value) {
		mapping.group_ids = mapping.group_ids.filter((groupId) => groupId !== removed.id)
	}
}

const addEmployeeRecipientMapping = () => {
	employeeRecipientForms.value.push(createEmptyEmployeeRecipient())
}

const removeEmployeeRecipientMapping = (index: number) => {
	employeeRecipientForms.value.splice(index, 1)
}

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

	employeeGroupForms.value = configStore.leaveNotificationEmployeeGroups.map((group) => ({
		id: group.id,
		name: group.name,
		employee_ids: [...group.employee_ids],
		recipientsText: toRecipientText(group.recipients),
	}))
	employeeRecipientForms.value = configStore.leaveNotificationEmployeeRecipients.map((mapping) => ({
		key: buildLocalKey('mapping'),
		employee_id: mapping.employee_id,
		recipientsText: toRecipientText(mapping.recipients),
		group_ids: [...mapping.group_ids],
	}))
}

const validateRecipientDomain = (recipients: string[]) => recipients.filter((email) => !email.endsWith('@pegatroncorp.com'))

const buildEmployeeGroupsPayload = (): LeaveNotificationEmployeeGroup[] => {
	const payload: LeaveNotificationEmployeeGroup[] = []
	for (const group of employeeGroupForms.value) {
		const trimmedName = group.name.trim()
		const recipients = normalizeRecipientInput(group.recipientsText)
		const employeeIds = Array.from(new Set(group.employee_ids.map((employeeId) => Number(employeeId)).filter(Boolean)))
		const isEmpty = !trimmedName && recipients.length === 0 && employeeIds.length === 0
		if (isEmpty) continue
		if (!trimmedName) {
			throw new Error('Each custom employee group must have a name')
		}
		if (employeeIds.length === 0) {
			throw new Error(`Group "${trimmedName}" must include at least one employee`)
		}
		if (recipients.length === 0) {
			throw new Error(`Group "${trimmedName}" must include at least one recipient`)
		}
		payload.push({
			id: group.id,
			name: trimmedName,
			employee_ids: employeeIds,
			recipients,
		})
	}
	return payload
}

const buildEmployeeRecipientPayload = (): LeaveNotificationEmployeeRecipient[] => {
	const payload: LeaveNotificationEmployeeRecipient[] = []
	const seenEmployeeIds = new Set<number>()
	for (const mapping of employeeRecipientForms.value) {
		const recipients = normalizeRecipientInput(mapping.recipientsText)
		const groupIds = Array.from(new Set(mapping.group_ids.map((groupId) => groupId.trim()).filter(Boolean)))
		const isEmpty = mapping.employee_id == null && recipients.length === 0 && groupIds.length === 0
		if (isEmpty) continue
		if (mapping.employee_id == null) {
			throw new Error('Each employee-specific rule must select an employee')
		}
		if (seenEmployeeIds.has(mapping.employee_id)) {
			throw new Error('Each employee can only have one employee-specific rule')
		}
		if (recipients.length === 0 && groupIds.length === 0) {
			throw new Error('Each employee-specific rule must include recipients or linked groups')
		}
		seenEmployeeIds.add(mapping.employee_id)
		payload.push({
			employee_id: mapping.employee_id,
			recipients,
			group_ids: groupIds,
		})
	}
	return payload
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

	let employeeGroups: LeaveNotificationEmployeeGroup[] = []
	let employeeRecipients: LeaveNotificationEmployeeRecipient[] = []
	try {
		employeeGroups = buildEmployeeGroupsPayload()
		employeeRecipients = buildEmployeeRecipientPayload()
	} catch (error) {
		showToast(error instanceof Error ? error.message : 'Invalid employee routing configuration', 'error')
		return
	}

	const activeRecipients =
		form.leave_notification_recipient_mode === 'global'
			? globalRecipients
			: form.leave_notification_recipient_mode === 'custom'
				? customRecipients
				: departmentRecipients.flatMap((entry) => entry.recipients)

	const invalidRecipients = [
		...validateRecipientDomain(activeRecipients),
		...validateRecipientDomain(employeeGroups.flatMap((group) => group.recipients)),
		...validateRecipientDomain(employeeRecipients.flatMap((mapping) => mapping.recipients)),
	]
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
			leave_notification_employee_groups: employeeGroups,
			leave_notification_employee_recipients: employeeRecipients,
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
		await Promise.all([configStore.fetchConfig(), departmentStore.fetchDepartments(), loadAllEmployees()])
	} catch (error) {
		console.error('Failed to load email notification config:', error)
	}
	initFromConfig()
})
</script>
