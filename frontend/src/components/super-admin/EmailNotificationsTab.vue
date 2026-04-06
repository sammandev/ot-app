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
					<p class="text-sm text-gray-500 dark:text-gray-400">SMTP delivery, leave routing, and email templates.</p>
				</div>
			</div>

			<div class="space-y-6 p-6">
				<div class="grid grid-cols-1 gap-6 xl:grid-cols-[1.12fr_0.88fr]">
					<div class="space-y-6">
						<!-- SMTP Connection -->
						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<h4 class="text-sm font-semibold uppercase tracking-wider text-sky-600 dark:text-sky-400">SMTP Connection</h4>
							<div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
								<div class="sm:col-span-2">
									<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">SMTP Host</label>
									<input v-model="form.notification_email_host" type="text" placeholder="mail.pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400" />
								</div>
								<div>
									<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Port</label>
									<input v-model.number="form.notification_email_port" type="number" min="1" max="65535" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
								</div>
								<div>
									<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Sender Name</label>
									<input v-model="form.leave_notification_sender_name" type="text" placeholder="OMS" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400" />
								</div>
							</div>
							<p class="mt-3 text-xs text-gray-400 dark:text-gray-500">Sender: {{ form.leave_notification_sender_name || 'OMS' }} &lt;no-reply@pegatroncorp.com&gt;</p>
						</div>

						<!-- Leave Recipient Routing -->
						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<h4 class="text-sm font-semibold uppercase tracking-wider text-sky-600 dark:text-sky-400">Leave Recipient Routing</h4>

							<!-- Mode Selector -->
							<div class="mt-4 grid grid-cols-3 gap-2">
								<button v-for="mode in recipientModes" :key="mode.value" type="button" @click="form.leave_notification_recipient_mode = mode.value" :class="[
									'rounded-lg border px-3 py-2.5 text-center transition',
									form.leave_notification_recipient_mode === mode.value
										? 'border-sky-500 bg-sky-50 shadow-sm dark:border-sky-400 dark:bg-sky-500/10'
										: 'border-gray-200 bg-white hover:border-sky-300 dark:border-gray-700 dark:bg-gray-900 dark:hover:border-sky-500/40'
								]">
									<div class="text-sm font-semibold text-gray-900 dark:text-white">{{ mode.label }}</div>
									<p class="mt-0.5 text-[11px] leading-4 text-gray-500 dark:text-gray-400">{{ mode.hint }}</p>
								</button>
							</div>

							<!-- Global Mode -->
							<div v-if="form.leave_notification_recipient_mode === 'global'" class="mt-4">
								<div class="mb-1.5 flex items-center justify-between">
									<label class="text-xs font-medium text-gray-600 dark:text-gray-300">Recipients (one per line)</label>
									<span class="text-[11px] text-gray-400">{{ globalRecipientCount }} recipient{{ globalRecipientCount === 1 ? '' : 's' }}</span>
								</div>
								<textarea v-model="globalRecipientsText" rows="4" placeholder="hr@pegatroncorp.com&#10;manager@pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:placeholder-gray-400"></textarea>
							</div>

							<!-- Department Mode -->
							<div v-if="form.leave_notification_recipient_mode === 'department'" class="mt-4">
								<div class="mb-2 flex items-center justify-between">
									<label class="text-xs font-medium text-gray-600 dark:text-gray-300">Department Mapping</label>
									<span class="text-[11px] text-gray-400">{{ enabledDepartments.length }} department{{ enabledDepartments.length === 1 ? '' : 's' }}</span>
								</div>
								<div class="space-y-1.5">
									<div v-for="department in enabledDepartments" :key="department.code" class="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-950">
										<!-- Collapsed summary row -->
										<button type="button" @click="toggleExpandedDepartment(department.code)" class="flex w-full items-center justify-between px-3 py-2.5 text-left">
											<div class="flex items-center gap-2 min-w-0">
												<svg :class="['h-3.5 w-3.5 shrink-0 text-gray-400 transition-transform duration-150', expandedDepartments.has(department.code) && 'rotate-90']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
												</svg>
												<span class="truncate text-sm font-medium text-gray-900 dark:text-white">{{ department.name }}</span>
												<span class="shrink-0 text-[11px] text-gray-400">{{ department.code }}</span>
											</div>
											<span class="shrink-0 rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800 dark:text-gray-400">{{ getDepartmentRecipientCount(department.code) }} rcpt</span>
										</button>
										<!-- Expanded form -->
										<div v-if="expandedDepartments.has(department.code)" class="border-t border-gray-200 px-3 pb-3 pt-2 dark:border-gray-700">
											<textarea v-model="departmentRecipientTexts[department.code]" rows="3" class="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400" :placeholder="`${department.code.toLowerCase()}@pegatroncorp.com`"></textarea>
										</div>
									</div>
								</div>
							</div>

							<!-- Custom Mode -->
							<div v-if="form.leave_notification_recipient_mode === 'custom'" class="mt-4 space-y-3">
								<p class="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800 dark:bg-amber-500/10 dark:text-amber-200">
									Only employees matched by a group or rule below receive leave emails. No fallback.
								</p>

								<!-- Sub-tab toggle: Groups / Rules -->
								<div class="flex items-center gap-1 rounded-lg border border-gray-200 bg-white p-1 dark:border-gray-700 dark:bg-gray-900">
									<button type="button" @click="customSubTab = 'groups'" :class="[
										'flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition',
										customSubTab === 'groups'
											? 'bg-sky-600 text-white shadow-sm'
											: 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
									]">
										Groups ({{ employeeGroupForms.length }})
									</button>
									<button type="button" @click="customSubTab = 'rules'" :class="[
										'flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition',
										customSubTab === 'rules'
											? 'bg-sky-600 text-white shadow-sm'
											: 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
									]">
										Rules ({{ employeeRecipientForms.length }})
									</button>
								</div>

								<!-- Employee Groups Panel -->
								<div v-if="customSubTab === 'groups'">
									<div class="flex items-center justify-between">
										<h6 class="text-xs font-semibold text-gray-800 dark:text-gray-200">Employee Groups</h6>
										<button type="button" @click="addEmployeeGroup" class="rounded-md bg-sky-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-sky-700">
											Add Group
										</button>
									</div>

									<div v-if="employeeGroupForms.length === 0" class="mt-2 rounded-lg border border-dashed border-gray-300 bg-white px-4 py-4 text-center text-xs text-gray-400 dark:border-gray-700 dark:bg-gray-900">
										No groups yet.
									</div>

									<div v-else class="mt-2 space-y-1.5">
										<div v-for="(group, index) in employeeGroupForms" :key="group.id" class="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
											<!-- Collapsed summary row -->
											<button type="button" @click="toggleExpandedGroup(group.id)" class="flex w-full items-center justify-between px-3 py-2.5 text-left">
												<div class="flex items-center gap-2 min-w-0">
													<svg :class="['h-3.5 w-3.5 shrink-0 text-gray-400 transition-transform duration-150', expandedGroups.has(group.id) && 'rotate-90']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
													</svg>
													<span class="truncate text-sm font-medium text-gray-900 dark:text-white">{{ group.name.trim() || `Group ${Number(index) + 1}` }}</span>
													<span class="shrink-0 rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800 dark:text-gray-400">{{ group.employee_ids.length }} emp · {{ normalizeRecipientInput(group.recipientsText).length }} rcpt</span>
												</div>
												<button type="button" @click.stop="removeEmployeeGroup(index)" class="shrink-0 ml-2 text-xs text-red-500 transition hover:text-red-700 dark:text-red-400 dark:hover:text-red-300">
													Remove
												</button>
											</button>
											<!-- Expanded form -->
											<div v-if="expandedGroups.has(group.id)" class="border-t border-gray-200 px-3 pb-3 pt-3 dark:border-gray-700">
												<div class="grid grid-cols-1 gap-3 xl:grid-cols-2">
													<div>
														<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Name</label>
														<input v-model="group.name" type="text" placeholder="Night Shift Team" class="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white" />
													</div>
													<div>
														<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Recipients</label>
														<textarea v-model="group.recipientsText" rows="3" placeholder="teamlead@pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white"></textarea>
													</div>
												</div>
												<div class="mt-3">
													<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Employees</label>
													<MultipleSelect
														:model-value="toSelectedOptions(group.employee_ids, employeePickerOptions)"
														:options="employeePickerOptions"
														placeholder="Search employees"
														searchable
														search-placeholder="Search by name or worker ID"
														empty-text="No matching employees"
														:show-checkboxes="true"
														@update:model-value="updateGroupEmployeeSelection(group, $event)"
													/>
												</div>
											</div>
										</div>
									</div>
								</div>

								<!-- Employee Rules Panel -->
								<div v-if="customSubTab === 'rules'">
									<div class="flex items-center justify-between">
										<h6 class="text-xs font-semibold text-gray-800 dark:text-gray-200">Employee Rules</h6>
										<button type="button" @click="addEmployeeRecipientMapping" class="rounded-md bg-sky-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-sky-700">
											Add Rule
										</button>
									</div>

									<div v-if="employeeRecipientForms.length === 0" class="mt-2 rounded-lg border border-dashed border-gray-300 bg-white px-4 py-4 text-center text-xs text-gray-400 dark:border-gray-700 dark:bg-gray-900">
										No employee rules yet.
									</div>

									<div v-else class="mt-2 space-y-1.5">
										<div v-for="(mapping, index) in employeeRecipientForms" :key="mapping.key" class="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
											<!-- Collapsed summary row -->
											<button type="button" @click="toggleExpandedRule(mapping.key)" class="flex w-full items-center justify-between px-3 py-2.5 text-left">
												<div class="flex items-center gap-2 min-w-0">
													<svg :class="['h-3.5 w-3.5 shrink-0 text-gray-400 transition-transform duration-150', expandedRules.has(mapping.key) && 'rotate-90']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
													</svg>
													<span class="truncate text-sm font-medium text-gray-900 dark:text-white">{{ getEmployeeLabelById(mapping.employee_id) || `Rule ${Number(index) + 1}` }}</span>
													<span class="shrink-0 rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800 dark:text-gray-400">{{ normalizeRecipientInput(mapping.recipientsText).length }} rcpt · {{ mapping.group_ids.length }} grp</span>
												</div>
												<button type="button" @click.stop="removeEmployeeRecipientMapping(index)" class="shrink-0 ml-2 text-xs text-red-500 transition hover:text-red-700 dark:text-red-400 dark:hover:text-red-300">
													Remove
												</button>
											</button>
											<!-- Expanded form -->
											<div v-if="expandedRules.has(mapping.key)" class="border-t border-gray-200 px-3 pb-3 pt-3 dark:border-gray-700">
												<div class="grid grid-cols-1 gap-3 xl:grid-cols-2">
													<div>
														<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Employee</label>
														<div class="flex items-end gap-2">
															<div class="min-w-0 flex-1">
																<SearchableDropdown
																	:model-value="mapping.employee_id == null ? '' : String(mapping.employee_id)"
																	:items="employeeDropdownItems"
																	placeholder="Select employee"
																	search-placeholder="Search by name or worker ID"
																	no-results-text="No matching employees"
																	@update:model-value="updateMappingEmployeeSelection(mapping, $event)"
																/>
															</div>
															<button
																v-if="mapping.employee_id != null"
																type="button"
																@click="mapping.employee_id = null"
																class="h-[38px] rounded-lg border border-gray-300 px-2.5 text-xs text-gray-500 transition hover:text-gray-700 dark:border-gray-700 dark:text-gray-400 dark:hover:text-white"
															>
																Clear
															</button>
														</div>
													</div>
													<div>
														<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Direct Recipients</label>
														<textarea v-model="mapping.recipientsText" rows="3" placeholder="manager@pegatroncorp.com" class="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white"></textarea>
													</div>
												</div>
												<div class="mt-3">
													<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Linked Groups</label>
													<div v-if="groupPickerOptions.length === 0" class="rounded-lg border border-dashed border-gray-300 bg-gray-50 px-3 py-2 text-xs text-gray-400 dark:border-gray-700 dark:bg-gray-950">
														Create a group first to link it here.
													</div>
													<MultipleSelect
														v-else
														:model-value="toSelectedOptions(mapping.group_ids, groupPickerOptions)"
														:options="groupPickerOptions"
														placeholder="Link groups"
														searchable
														search-placeholder="Search groups"
														empty-text="No matching groups"
														:show-checkboxes="true"
														@update:model-value="updateMappingGroupSelection(mapping, $event)"
													/>
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>

							<p class="mt-4 text-xs text-gray-400 dark:text-gray-500">One address per line or comma-separated. Only @pegatroncorp.com addresses.</p>
						</div>
					</div>

					<div class="space-y-6">
						<!-- Template Variables -->
						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<h4 class="text-sm font-semibold uppercase tracking-wider text-sky-600 dark:text-sky-400">Template Variables</h4>
							<div class="mt-3 flex flex-wrap gap-1.5">
								<span v-for="variable in templateVariables" :key="variable" class="rounded-md border border-sky-200 bg-sky-50 px-2 py-0.5 text-[11px] font-medium text-sky-700 dark:border-sky-500/30 dark:bg-sky-500/10 dark:text-sky-300">{{ variable }}</span>
							</div>
						</div>

						<!-- Email Templates -->
						<div class="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-700 dark:bg-gray-800/50">
							<h4 class="text-sm font-semibold uppercase tracking-wider text-sky-600 dark:text-sky-400">Email Templates</h4>
							<div class="mt-4 space-y-4">
								<div>
									<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Subject</label>
									<input v-model="form.leave_notification_subject_template" type="text" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white" />
								</div>
								<div>
									<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Body</label>
									<textarea v-model="form.leave_notification_body_template" rows="10" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white"></textarea>
									<p class="mt-1.5 text-[11px] text-gray-400">Details and preview links are appended automatically.</p>
								</div>
								<div>
									<label class="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-300">Footer</label>
									<textarea v-model="form.leave_notification_footer_template" rows="4" class="block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-theme-xs transition focus:border-sky-500 focus:outline-hidden focus:ring-3 focus:ring-sky-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white"></textarea>
								</div>
							</div>
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
import MultipleSelect from '@/components/forms/FormElements/MultipleSelect.vue'
import SearchableDropdown, { type DropdownItem } from '@/components/ui/SearchableDropdown.vue'
import { useToast } from '@/composables/useToast'
import type { Department } from '@/services/api/department'
import { type Employee, employeeAPI } from '@/services/api/employee'
import {
	type LeaveNotificationDepartmentRecipient,
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

interface SelectOption {
	value: number | string
	label: string
}

interface RecipientModeOption {
	value: 'global' | 'department' | 'custom'
	label: string
	hint: string
}

const configStore = useConfigStore()
const departmentStore = useDepartmentStore()
const { showToast } = useToast()

const recipientModes: RecipientModeOption[] = [
	{ value: 'global' as const, label: 'Global', hint: 'All leave requests' },
	{ value: 'department' as const, label: 'Department', hint: 'Per department' },
	{ value: 'custom' as const, label: 'Custom', hint: 'Per employee / group' },
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
const departmentRecipientTexts = reactive<Record<string, string>>({})
const employeeGroupForms = ref<EmployeeGroupForm[]>([])
const employeeRecipientForms = ref<EmployeeRecipientForm[]>([])
const employees = ref<Employee[]>([])
const employeeLoading = ref(false)

const customSubTab = ref<'groups' | 'rules'>('groups')
const expandedDepartments = reactive(new Set<string>())
const expandedGroups = reactive(new Set<string>())
const expandedRules = reactive(new Set<string>())

const globalRecipientCount = computed(() => normalizeRecipientInput(globalRecipientsText.value).length)

const getDepartmentRecipientCount = (code: string) => normalizeRecipientInput(departmentRecipientTexts[code] || '').length

const toggleExpandedDepartment = (code: string) => {
	if (expandedDepartments.has(code)) expandedDepartments.delete(code)
	else expandedDepartments.add(code)
}

const toggleExpandedGroup = (id: string) => {
	if (expandedGroups.has(id)) expandedGroups.delete(id)
	else expandedGroups.add(id)
}

const toggleExpandedRule = (key: string) => {
	if (expandedRules.has(key)) expandedRules.delete(key)
	else expandedRules.add(key)
}

const enabledDepartments = computed(() => departmentStore.enabledDepartments)
const availableEmployees = computed(() =>
	employees.value
		.filter((employee: Employee) => employee.is_enabled)
		.slice()
		.sort((left: Employee, right: Employee) => formatEmployeeLabel(left).localeCompare(formatEmployeeLabel(right))),
)
const employeePickerOptions = computed<SelectOption[]>(() =>
	availableEmployees.value.map((employee: Employee) => ({
		value: employee.id,
		label: formatEmployeeLabel(employee),
	})),
)
const employeeDropdownItems = computed<DropdownItem[]>(() =>
	availableEmployees.value.map((employee: Employee) => ({
		id: String(employee.id),
		name: formatEmployeeLabel(employee),
	})),
)
const groupPickerOptions = computed<SelectOption[]>(() =>
	employeeGroupForms.value.map((group: EmployeeGroupForm, index: number) => ({
		value: group.id,
		label: group.name.trim() || `Group ${index + 1}`,
	})),
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

const getEmployeeLabelById = (employeeId: number | null) => {
	if (employeeId == null) return ''
	const employee = availableEmployees.value.find((entry: Employee) => entry.id === employeeId)
	return employee ? formatEmployeeLabel(employee) : `Employee ${employeeId}`
}

const toSelectedOptions = (values: Array<number | string>, options: SelectOption[]) => {
	const selected = new Set(values.map((value) => String(value)))
	return options.filter((option) => selected.has(String(option.value)))
}

const updateGroupEmployeeSelection = (group: EmployeeGroupForm, selectedOptions: SelectOption[]) => {
	group.employee_ids = selectedOptions.map((option) => Number(option.value))
}

const updateMappingEmployeeSelection = (mapping: EmployeeRecipientForm, value: string) => {
	mapping.employee_id = value ? Number(value) : null
}

const updateMappingGroupSelection = (mapping: EmployeeRecipientForm, selectedOptions: SelectOption[]) => {
	mapping.group_ids = selectedOptions.map((option) => String(option.value))
}

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
	const group = createEmptyEmployeeGroup()
	employeeGroupForms.value.push(group)
	expandedGroups.add(group.id)
}

const removeEmployeeGroup = (index: number) => {
	const [removed] = employeeGroupForms.value.splice(index, 1)
	if (!removed) return
	expandedGroups.delete(removed.id)
	for (const mapping of employeeRecipientForms.value) {
		mapping.group_ids = mapping.group_ids.filter((groupId: string) => groupId !== removed.id)
	}
}

const addEmployeeRecipientMapping = () => {
	const mapping = createEmptyEmployeeRecipient()
	employeeRecipientForms.value.push(mapping)
	expandedRules.add(mapping.key)
}

const removeEmployeeRecipientMapping = (index: number) => {
	const [removed] = employeeRecipientForms.value.splice(index, 1)
	if (removed) expandedRules.delete(removed.key)
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

	employeeGroupForms.value = configStore.leaveNotificationEmployeeGroups.map((group: LeaveNotificationEmployeeGroup) => ({
		id: group.id,
		name: group.name,
		employee_ids: [...group.employee_ids],
		recipientsText: toRecipientText(group.recipients),
	}))
	employeeRecipientForms.value = configStore.leaveNotificationEmployeeRecipients.map((mapping: LeaveNotificationEmployeeRecipient) => ({
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
		const employeeIds = Array.from(
			new Set<number>(group.employee_ids.map((employeeId: number) => Number(employeeId)).filter((employeeId: number) => employeeId > 0)),
		)
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
		const groupIds = Array.from(
			new Set<string>(mapping.group_ids.map((groupId: string) => groupId.trim()).filter((groupId: string) => groupId.length > 0)),
		)
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
	const departmentRecipients: LeaveNotificationDepartmentRecipient[] = enabledDepartments.value
		.map((department: Department) => ({
			department_code: department.code,
			recipients: normalizeRecipientInput(departmentRecipientTexts[department.code] || ''),
		}))
		.filter((entry: LeaveNotificationDepartmentRecipient) => entry.recipients.length > 0)

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
			: departmentRecipients.flatMap((entry: LeaveNotificationDepartmentRecipient) => entry.recipients)

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
	if (form.leave_notification_recipient_mode === 'custom' && employeeGroups.length === 0 && employeeRecipients.length === 0) {
		showToast('Custom mode requires at least one employee group or employee-specific rule', 'error')
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
