<template>
	<AdminLayout>
		<div class="space-y-6">
			<div class="grid gap-4 sm:grid-cols-3">
				<div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
					<p class="text-sm text-gray-500 dark:text-gray-400">{{ t('otForm.weeklyOvertime') }} - {{
						selectedEmployeeName
					}}</p>
					<div class="flex items-baseline gap-2 mt-2">
						<p :class="weeklyStatusColor" class="text-lg font-semibold">{{ weeklyAppliedHours.toFixed(2) }}
							/ {{ WEEKLY_LIMIT }} <span class="text-sm font-normal">{{ t('otForm.hours') }}</span></p>
					</div>
					<p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ t('otForm.appliedLimit') }}</p>
					<p v-if="weeklyWarning" :class="weeklyWarningClass" class="mt-1 text-xs">{{ weeklyWarning }}</p>
				</div>
				<div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
					<p class="text-sm text-gray-500 dark:text-gray-400">{{ t('otForm.monthlyOvertime') }} - {{
						selectedEmployeeName }}
					</p>
					<div class="flex items-baseline gap-2 mt-2">
						<p :class="monthlyStatusColor" class="text-lg font-semibold">{{ monthlyAppliedHours.toFixed(2)
						}}
							/ {{ MONTHLY_LIMIT }} <span class="text-sm font-normal">{{ t('otForm.hours') }}</span></p>
					</div>
					<p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ t('otForm.appliedLimit') }}</p>
					<p v-if="monthlyWarning" :class="monthlyWarningClass" class="mt-1 text-xs">{{ monthlyWarning }}</p>
				</div>
				<div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
					<p class="text-sm text-gray-500 dark:text-gray-400">{{ t('otForm.remainingApplicable') }}
						<span v-if="overtimePeriod" class="text-xs text-gray-400 dark:text-gray-500">{{ overtimePeriod
						}} </span>
					</p>
					<div class="flex items-baseline gap-2 mt-2">
						<p class="text-lg font-semibold">
							<span :class="weeklyRemainingColor">{{ weeklyRemainingHours.toFixed(2) }}</span> <span
								class="text-gray-900 dark:text-white">/</span>
							<span :class="monthlyRemainingColor">{{ monthlyRemainingHours.toFixed(2) }}</span>
							<span class="text-sm font-normal text-gray-900 dark:text-white"> {{ t('otForm.hours')
							}}</span>
						</p>
					</div>
					<p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ t('otForm.weeklyMonthly') }}</p>
					<p v-if="remainingWarning" :class="remainingWarningClass" class="mt-1 text-xs">{{ remainingWarning
					}}</p>
				</div>
			</div>

			<!-- Overtime Regulations -->
			<OvertimeRegulations />

			<!-- Overtime Request Form Card -->
			<ComponentCard :title="t('otForm.requestDetails')" :desc="t('otForm.requestDetailsDesc')">
				<template #header-extra>
					<span class="px-4 py-1.5 text-sm font-semibold rounded-full border" :class="dayTypeChipClass">
						{{ dayTypeLabel }}
					</span>
				</template>
				<!-- Alert Section -->
				<div class="space-y-4" v-if="submitSuccess || submitError">
					<div v-if="submitSuccess"
						class="flex items-center justify-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800 dark:border-emerald-900/50 dark:bg-emerald-900/30 dark:text-emerald-100">
						<span class="flex-1 text-center">{{ successMessage }}</span>
						<button type="button" class="text-emerald-600 hover:text-emerald-800 flex-shrink-0"
							@click="submitSuccess = false">
							<XIcon />
						</button>
					</div>
					<div v-if="submitError"
						class="flex items-center justify-center gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-800 dark:border-rose-900/50 dark:bg-rose-900/30 dark:text-rose-100">
						<span class="flex-1 text-center">{{ submitError }}</span>
						<button type="button" class="text-rose-600 hover:text-rose-800 flex-shrink-0"
							@click="submitError = null">
							<XIcon />
						</button>
					</div>
				</div>

				<form class="space-y-5" @submit.prevent="handleSubmit">
					<div class="grid gap-4 lg:grid-cols-2">
						<div class="space-y-2">
							<label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
								t('otForm.employeeName') }}</label>
							<SearchableDropdown v-model="form.selectedEmployee" :items="filteredEmployees"
								:placeholder="t('otForm.selectEmployee')"
								:search-placeholder="t('otForm.searchEmployee')"
								:no-results-text="t('otForm.noResults')" :error="validationErrors.employee" />
							<p v-if="validationErrors.employee" class="mt-1.5 text-xs text-error-500">{{
								validationErrors.employee }}
							</p>
						</div>
						<div class="space-y-2">
							<label class="text-sm font-medium text-gray-300 dark:text-white/15">{{ t('otForm.workerId')
							}}</label>
							<input :value="selectedEmployeeCode" type="text"
								class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:shadow-focus-ring focus:outline-hidden disabled:border-gray-100 disabled:bg-gray-50 disabled:placeholder:text-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-gray-400 dark:focus:border-brand-300 dark:disabled:border-gray-800 dark:disabled:bg-white/[0.03] dark:disabled:placeholder:text-white/15"
								disabled />
						</div>
					</div>

					<div class="grid gap-4 lg:grid-cols-8">
						<div class="space-y-2 lg:col-span-4">
							<label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
								t('otForm.projectName') }}</label>
							<SearchableDropdown v-model="form.selectedProject" :items="enabledProjects"
								:placeholder="t('otForm.selectProject')" :search-placeholder="t('otForm.searchProject')"
								:no-results-text="t('otForm.noResults')" :disabled="isApprovedRequest"
								:error="validationErrors.project">
								<template #extra-items>
									<li v-if="form.selectedProject && !enabledProjects.find(p => p.id === form.selectedProject)"
										class="cursor-pointer px-4 py-2 text-sm text-center text-gray-400 italic">
										{{projects.find(p => p.id === form.selectedProject)?.name}} {{
											t('otForm.disabled') }}
									</li>
								</template>
							</SearchableDropdown>
							<p v-if="validationErrors.project" class="mt-1.5 text-xs text-error-500">{{
								validationErrors.project }}</p>
						</div>
						<div class="space-y-2 lg:col-span-2">
							<label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
								t('otForm.overtimeDate') }}</label>
							<flat-pickr v-model="selectedDate" :config="datePickerOptions" :class="[
								validationErrors.date ? 'border-error-300 focus:border-error-300 focus:ring-error-500/10 dark:border-error-700 dark:focus:border-error-800' : 'border-gray-300 focus:border-brand-300 focus:ring-brand-500/10 dark:border-gray-700 dark:focus:border-brand-800'
							]" class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30" />
							<p v-if="validationErrors.date" class="mt-1.5 text-xs text-error-500">{{
								validationErrors.date }}</p>
						</div>
						<div class="space-y-2 lg:col-span-2">
							<label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
								t('otForm.overtimeOnHoliday')
							}}</label>
							<label :class="isApprovedRequest ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'"
								class="flex items-center text-sm font-medium text-gray-700 select-none dark:text-gray-200">
								<div class="relative">
									<input v-model="isHoliday" type="checkbox" class="sr-only"
										:disabled="isApprovedRequest" />
									<div :class="isHoliday ? 'border-brand-500 bg-brand-500' : 'bg-transparent border-gray-300 dark:border-gray-700'"
										class="mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] hover:border-brand-500 dark:hover:border-brand-500">
										<span :class="isHoliday ? '' : 'opacity-0'">
											<svg width="14" height="14" viewBox="0 0 14 14" fill="none"
												xmlns="http://www.w3.org/2000/svg">
												<path d="M11.6666 3.5L5.24992 9.91667L2.33325 7" stroke="white"
													stroke-width="1.94437" stroke-linecap="round"
													stroke-linejoin="round" />
											</svg>
										</span>
									</div>
								</div>
								{{ t('otForm.applyHolidayRules') }}
							</label>
						</div>
					</div>

					<div class="grid gap-4 items-end lg:grid-cols-6">
						<div class="space-y-2 lg:col-span-2">
							<label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('otForm.timeStart')
							}}</label>
							<flat-pickr v-model="timeStart" :config="timePickerOptions" :disabled="isApprovedRequest"
								:class="[
									validationErrors.timeStart ? 'border-error-300 focus:border-error-300 focus:ring-error-500/10 dark:border-error-700 dark:focus:border-error-800' : 'border-gray-300 focus:border-brand-300 focus:ring-brand-500/10 dark:border-gray-700 dark:focus:border-brand-800',
									isApprovedRequest ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''
								]" class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30" />
							<p v-if="validationErrors.timeStart" class="mt-1.5 text-xs text-error-500">{{
								validationErrors.timeStart }}
							</p>
						</div>
						<div class="flex items-center justify-between gap-3 lg:col-span-2">
							<button type="button" class="btn-secondary" @click="adjustDuration(-0.5)"
								:disabled="isApprovedRequest">-
								0.5h</button>
							<div class="flex flex-col items-center text-center">
								<span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
									t('otForm.rawHours') }}</span>
								<span class="text-xl font-semibold text-gray-900 dark:text-white">{{ rawHours.toFixed(2)
								}} h</span>
							</div>
							<button type="button" class="btn-secondary" @click="adjustDuration(0.5)"
								:disabled="isApprovedRequest">+
								0.5h</button>
						</div>
						<div class="space-y-2 lg:col-span-2">
							<label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('otForm.timeEnd')
							}}</label>
							<flat-pickr v-model="timeEnd" :config="timePickerOptions" :disabled="isApprovedRequest"
								:class="[
									validationErrors.timeEnd ? 'border-error-300 focus:border-error-300 focus:ring-error-500/10 dark:border-error-700 dark:focus:border-error-800' : 'border-gray-300 focus:border-brand-300 focus:ring-brand-500/10 dark:border-gray-700 dark:focus:border-brand-800',
									isApprovedRequest ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''
								]" class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30" />
							<p v-if="validationErrors.timeEnd" class="mt-1.5 text-xs text-error-500">{{
								validationErrors.timeEnd }}</p>
						</div>
					</div>

					<BreakSchedulerSection v-model:has-break="hasBreak" v-model:break-start="breakStart"
						v-model:break-end="breakEnd" v-model:break-start2="breakStart2" v-model:break-end2="breakEnd2"
						v-model:break-start3="breakStart3" v-model:break-end3="breakEnd3"
						:show-second-break="showSecondBreak" :show-third-break="showThirdBreak"
						:total-break-hours="totalBreakHours" :total-hours="totalHours"
						:time-picker-config="timePickerOptions" :disabled="isApprovedRequest" />

					<div class="space-y-4">
						<div class="space-y-2">
							<label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
								t('otForm.overtimeReason')
							}}</label>
							<input v-model="reason" type="text" maxlength="20" :disabled="isApprovedRequest" :class="[
								validationErrors.reason ? 'border-error-300 focus:border-error-300 focus:ring-error-500/10 dark:border-error-700 dark:focus:border-error-800' : 'border-gray-300 focus:border-brand-300 focus:ring-brand-500/10 dark:border-gray-700 dark:focus:border-brand-800',
								isApprovedRequest ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''
							]" class="dark:bg-dark-900 h-11 w-full rounded-lg border bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
								:placeholder="t('otForm.reasonPlaceholder')" />
							<p v-if="validationErrors.reason" class="mt-1.5 text-xs text-error-500">{{
								validationErrors.reason }}</p>
						</div>
						<div class="space-y-2">
							<label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
								t('otForm.overtimeDetails')
							}}</label>
							<textarea v-model="details" rows="3" :disabled="isApprovedRequest" :class="[
								validationErrors.details ? 'border-error-300 focus:border-error-300 focus:ring-error-500/10 dark:border-error-700 dark:focus:border-error-800' : 'border-gray-300 focus:border-brand-300 focus:ring-brand-500/10 dark:border-gray-700 dark:focus:border-brand-800',
								isApprovedRequest ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''
							]" class="dark:bg-dark-900 w-full rounded-lg border bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
								:placeholder="t('otForm.detailsPlaceholder')"></textarea>
							<p v-if="validationErrors.details" class="mt-1.5 text-xs text-error-500">{{
								validationErrors.details }}</p>
						</div>
					</div>

					<div class="grid gap-3 md:grid-cols-3" v-if="!submittedRequestId">
						<button type="button"
							class="h-11 rounded-lg border border-brand-200 bg-transparent px-4 text-sm font-semibold text-brand-700 shadow-theme-xs transition hover:bg-brand-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/15 disabled:cursor-not-allowed disabled:opacity-60 dark:border-brand-700 dark:text-brand-200 dark:hover:bg-brand-500/10"
							:disabled="isSubmitting || isAutofilling || !form.selectedEmployee" @click="handleAutofill">
							{{ isAutofilling ? t('otForm.autofilling') : t('otForm.autofillYesterday') }}
						</button>
						<button type="button"
							class="h-11 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5"
							:disabled="isSubmitting" @click="handleReset">
							{{ t('common.reset') }}
						</button>
						<button type="submit"
							class="h-11 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 disabled:cursor-not-allowed disabled:opacity-60"
							:disabled="isSubmitting || !canCreate">
							{{ isSubmitting ? t('otForm.submitting') : t('otForm.submitRequest') }}
						</button>
					</div>

					<div class="space-y-4" v-else>
						<!-- Approved/Rejected request notice -->
						<div v-if="submittedRequestStatus === 'approved'"
							class="flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800 dark:border-emerald-900/50 dark:bg-emerald-900/30 dark:text-emerald-100">
							<svg class="w-5 h-5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
									clip-rule="evenodd" />
							</svg>
							<span class="text-sm font-medium">{{ t('otForm.approvedNotice') }}</span>
						</div>
						<div v-else-if="submittedRequestStatus === 'rejected'"
							class="flex items-center gap-3 rounded-xl border border-error-200 bg-error-50 px-4 py-3 text-error-800 dark:border-error-900/50 dark:bg-error-900/30 dark:text-error-100">
							<svg class="w-5 h-5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
									clip-rule="evenodd" />
							</svg>
							<span class="text-sm font-medium">{{ t('otForm.rejectedNotice') }}</span>
						</div>

						<div class="grid gap-3 md:grid-cols-2">
							<button type="button" v-if="canDeleteRequest"
								class="h-11 rounded-lg border border-error-300 bg-error-50 px-4 text-sm font-semibold text-error-700 shadow-theme-xs transition hover:bg-error-100 focus:outline-hidden focus:ring-3 focus:ring-error-500/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-error-700 dark:bg-error-500/10 dark:text-error-400 dark:hover:bg-error-500/20"
								:disabled="isSubmitting" @click="showDeleteModal = true">
								{{ t('otForm.deleteRequest') }}
							</button>
							<button type="submit" v-if="canEditRequest"
								class="h-11 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 disabled:cursor-not-allowed disabled:opacity-60"
								:disabled="isSubmitting">
								{{ isSubmitting ? t('otForm.updatingRequest') : t('otForm.updateRequest') }}
							</button>
						</div>
					</div>
				</form>
			</ComponentCard>

			<!-- Delete Confirmation Modal -->
			<div v-if="showDeleteModal"
				class="fixed inset-0 z-[99999] flex items-center justify-center bg-gray-900/50 dark:bg-gray-950/70"
				role="dialog" aria-modal="true" aria-labelledby="ot-form-delete-modal-title"
				@click.self="showDeleteModal = false">
				<div class="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
					<div class="mb-4">
						<div
							class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-error-100 dark:bg-error-500/20">
							<svg class="h-6 w-6 text-error-600 dark:text-error-400" fill="none" viewBox="0 0 24 24"
								stroke-width="2" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round"
									d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
							</svg>
						</div>
					</div>
					<div class="text-center">
						<h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white"
							id="ot-form-delete-modal-title">{{
								t('otForm.deleteConfirmTitle') }}
						</h3>
						<p class="mb-6 text-sm text-gray-600 dark:text-gray-400">
							{{ t('otForm.deleteConfirmMsg') }}
						</p>
					</div>
					<div class="flex gap-3">
						<button type="button"
							class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-700 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
							@click="showDeleteModal = false">
							{{ t('common.cancel') }}
						</button>
						<button type="button"
							class="h-11 flex-1 rounded-lg bg-error-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 focus:outline-hidden focus:ring-3 focus:ring-error-500/20"
							@click="handleDelete">
							{{ t('common.delete') }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</AdminLayout>
</template>


<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useI18n } from 'vue-i18n'
import ComponentCard from '@/components/common/ComponentCard.vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import BreakSchedulerSection from '@/components/ot/BreakSchedulerSection.vue'
import OvertimeRegulations from '@/components/ot/OvertimeRegulations.vue'
import SearchableDropdown from '@/components/ui/SearchableDropdown.vue'
import {
	isWeekend,
	type OvertimeFormState,
	useBreakScheduler,
} from '@/composables/overtime/useBreakScheduler'
import { useOvertimeHolidays } from '@/composables/overtime/useOvertimeHolidays'
import { type RawOvertimeResponse, useOvertimeStats } from '@/composables/overtime/useOvertimeStats'
import { type FlatpickrInstance, useFlatpickrScroll } from '@/composables/useFlatpickrScroll'
import { XIcon } from '@/icons'
import { useAuthStore } from '@/stores/auth'
import { useEmployeeStore } from '@/stores/employee'
import { useOvertimeStore } from '@/stores/overtime'
import { useProjectStore } from '@/stores/project'

// ── Stores ────────────────────────────────────────────────────────
const { t } = useI18n()
const employeeStore = useEmployeeStore()
const projectStore = useProjectStore()
const overtimeStore = useOvertimeStore()
const authStore = useAuthStore()

// ── Computed data from stores ─────────────────────────────────────

const employees = computed(() =>
	employeeStore.employees
		.filter((e) => e.is_enabled)
		.map((e) => ({
			id: String(e.id),
			code: e.emp_id,
			name: e.name,
			exclude_from_reports: e.exclude_from_reports,
		}))
		.sort((a, b) => a.name.localeCompare(b.name)),
)

const projects = computed(() =>
	projectStore.projects
		.map((p) => ({ id: String(p.id), name: p.name, is_enabled: p.is_enabled }))
		.sort((a, b) => a.name.localeCompare(b.name)),
)

const enabledProjects = computed(() => projects.value.filter((p) => p.is_enabled))

const selectedEmployeeData = computed(() =>
	employees.value.find((e) => e.id === form.selectedEmployee),
)

const selectedEmployeeName = computed(() => selectedEmployeeData.value?.name || 'Employee')

// ── Admin access & permissions ────────────────────────────────────

const isAdmin = computed(() => authStore.isPtbAdmin)
const canCreate = computed(() => authStore.hasPermission('overtime_form', 'create'))
const canUpdate = computed(() => authStore.hasPermission('overtime_form', 'update'))
const canDelete = computed(() => authStore.hasPermission('overtime_form', 'delete'))

const isApprovedRequest = computed(
	() => submittedRequestStatus.value === 'approved' || submittedRequestStatus.value === 'rejected',
)
const canEditRequest = computed(() => !isApprovedRequest.value && canUpdate.value)
const canDeleteRequest = computed(() => !isApprovedRequest.value && canDelete.value)

const filteredEmployees = computed(() => employees.value)

const canViewStats = computed(() => {
	if (isAdmin.value) return true
	const userWorkerId = authStore.user?.worker_id
	const selectedEmp = employees.value.find((e) => e.id === form.selectedEmployee)
	return selectedEmp?.code === userWorkerId
})

const isExcludedFromOTReports = computed(() => {
	return selectedEmployeeData.value?.exclude_from_reports ?? false
})

// ── Flatpickr ─────────────────────────────────────────────────────

const { flatpickrInstances, attachMonthScroll, attachTimeScroll, destroyFlatpickrs } =
	useFlatpickrScroll()

// ── Form state ────────────────────────────────────────────────────

const todayLocal = () => {
	const now = new Date()
	const year = now.getFullYear()
	const month = String(now.getMonth() + 1).padStart(2, '0')
	const day = String(now.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

const form = reactive<OvertimeFormState>({
	selectedEmployee: '',
	selectedProject: '',
	selectedDate: todayLocal(),
	timeStart: '17:20',
	timeEnd: '18:20',
	isHoliday: false,
	hasBreak: false,
	breakStart: '',
	breakEnd: '',
	breakStart2: '',
	breakEnd2: '',
	breakStart3: '',
	breakEnd3: '',
	reason: '',
	details: '',
})

// ── Composables ───────────────────────────────────────────────────

const { holidays, holidayDateSet, holidayTitleMap, isDateHoliday, fetchHolidays } =
	useOvertimeHolidays(flatpickrInstances)

const {
	rawHours,
	manualBreakHours,
	totalBreakHours,
	totalHours,
	showSecondBreak,
	showThirdBreak,
	scheduleBreaks,
} = useBreakScheduler(form)

const {
	WEEKLY_LIMIT,
	MONTHLY_LIMIT,
	loadLimits,
	overtimePeriod,
	weeklyAppliedHours,
	monthlyAppliedHours,
	weeklyRemainingHours,
	monthlyRemainingHours,
	weeklyStatusColor,
	monthlyStatusColor,
	weeklyRemainingColor,
	monthlyRemainingColor,
	weeklyWarning,
	monthlyWarning,
	remainingWarning,
	weeklyWarningClass,
	monthlyWarningClass,
	remainingWarningClass,
	calculateEmployeeOvertime,
} = useOvertimeStats({ form, canViewStats, isExcludedFromOTReports, overtimeStore })

// ── Flatpickr options ─────────────────────────────────────────────

let lastFetchedHolidayYear = new Date().getFullYear()

const datePickerOptions = {
	dateFormat: 'Y-m-d',
	altInput: false,
	onReady: (_selectedDates: Date[], _dateStr: string, instance: FlatpickrInstance) => {
		flatpickrInstances.value.push(instance)
		attachMonthScroll(instance)
	},
	onDayCreate: (
		_dObj: Date[],
		_dStr: string,
		_fp: FlatpickrInstance,
		dayElem: HTMLElement & { dateObj?: Date },
	) => {
		if (!dayElem.dateObj) return
		const d = dayElem.dateObj
		const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
		if (holidayDateSet.value.has(dateStr)) {
			dayElem.classList.add('ot-holiday-day')
			const title = holidayTitleMap.value.get(dateStr)
			if (title) dayElem.setAttribute('title', title)
		}
	},
	onMonthChange: (_selectedDates: Date[], _dateStr: string, instance: FlatpickrInstance) => {
		const year = instance.currentYear
		if (year && year !== lastFetchedHolidayYear) {
			lastFetchedHolidayYear = year
			fetchHolidays(year)
		}
	},
}

const timePickerOptions = {
	enableTime: true,
	noCalendar: true,
	dateFormat: 'H:i',
	time_24hr: true,
	minuteIncrement: 5,
	scrollInput: true,
	onReady: (_selectedDates: Date[], _dateStr: string, instance: FlatpickrInstance) => {
		flatpickrInstances.value.push(instance)
		attachTimeScroll(instance)
	},
}

// ── Submit / loading state ────────────────────────────────────────

const submitSuccess = ref(false)
const submitError = ref<string | null>(null)
const successMessage = ref(t('otForm.messages.submitted'))
const isSubmitting = ref(false)
const submittedRequestId = ref<number | null>(null)
const submittedRequestStatus = ref<string | null>(null)
const showDeleteModal = ref(false)
const isLoadingExisting = ref(false)
const isAutofilling = ref(false)
const isInitializing = ref(true)

const validationErrors = reactive({
	employee: '',
	project: '',
	date: '',
	timeStart: '',
	timeEnd: '',
	reason: '',
	details: '',
})

// ── Derived computeds ─────────────────────────────────────────────

const selectedEmployeeCode = computed(
	() => employees.value.find((e) => e.id === form.selectedEmployee)?.code || '—',
)

const dayTypeLabel = computed(() => {
	if (form.isHoliday) return t('otForm.holiday')
	const d = new Date(form.selectedDate)
	const day = d.getDay()
	return day === 0 || day === 6 ? t('otForm.weekend') : t('otForm.weekday')
})

const dayTypeChipClass = computed(() => {
	if (form.isHoliday) {
		return 'border-purple-200 bg-purple-50 text-purple-700 dark:border-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
	}
	const d = new Date(form.selectedDate)
	const day = d.getDay()
	if (day === 0 || day === 6) {
		return 'border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-700 dark:bg-orange-900/30 dark:text-orange-300'
	}
	return 'border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
})

// ── Normalize helpers for v-model ─────────────────────────────────

function normalizeTimeValue(value: string | Date) {
	if (value instanceof Date) {
		const hh = String(value.getHours()).padStart(2, '0')
		const mm = String(value.getMinutes()).padStart(2, '0')
		return `${hh}:${mm}`
	}
	return value
}

function normalizeDateValue(value: string | Date) {
	if (value instanceof Date) {
		const year = value.getFullYear()
		const month = String(value.getMonth() + 1).padStart(2, '0')
		const day = String(value.getDate()).padStart(2, '0')
		return `${year}-${month}-${day}`
	}
	return value
}

// ── Form validation ───────────────────────────────────────────────

function validate() {
	validationErrors.employee = ''
	validationErrors.project = ''
	validationErrors.date = ''
	validationErrors.timeStart = ''
	validationErrors.timeEnd = ''
	validationErrors.reason = ''
	validationErrors.details = ''

	let hasError = false

	if (!form.selectedEmployee) {
		validationErrors.employee = t('otForm.validation.selectEmployee')
		hasError = true
	}
	if (!form.selectedProject) {
		validationErrors.project = t('otForm.validation.selectProject')
		hasError = true
	}
	if (!form.selectedDate) {
		validationErrors.date = t('otForm.validation.selectDate')
		hasError = true
	}
	if (!form.timeStart) {
		validationErrors.timeStart = t('otForm.validation.provideStartTime')
		hasError = true
	}
	if (!form.timeEnd) {
		validationErrors.timeEnd = t('otForm.validation.provideEndTime')
		hasError = true
	}
	if (form.timeStart && form.timeEnd && rawHours.value <= 0) {
		validationErrors.timeEnd = t('otForm.validation.endAfterStart')
		hasError = true
	}
	if (!form.reason || form.reason.trim() === '') {
		validationErrors.reason = t('otForm.validation.provideReason')
		hasError = true
	}
	if (!form.details || form.details.trim() === '') {
		validationErrors.details = t('otForm.validation.provideDetails')
		hasError = true
	}
	if (form.hasBreak && manualBreakHours.value < 0) {
		return 'Break times are invalid.'
	}

	return hasError ? 'Please fill in all required fields.' : null
}

function handleReset() {
	form.timeStart = '17:20'
	form.timeEnd = '18:20'
	form.isHoliday = false
	form.hasBreak = false
	form.breakStart = ''
	form.breakEnd = ''
	form.breakStart2 = ''
	form.breakEnd2 = ''
	form.breakStart3 = ''
	form.breakEnd3 = ''
	form.reason = ''
	form.details = ''
	submitSuccess.value = false
	submitError.value = null
	validationErrors.employee = ''
	validationErrors.project = ''
	validationErrors.date = ''
	validationErrors.timeStart = ''
	validationErrors.timeEnd = ''
	validationErrors.reason = ''
	validationErrors.details = ''
	scheduleBreaks()
}

// ── Existing request / autofill ───────────────────────────────────

async function checkExistingRequest(employeeId: string, date: string) {
	if (!employeeId || !date) {
		submittedRequestId.value = null
		submittedRequestStatus.value = null
		return
	}

	try {
		isLoadingExisting.value = true
		const requests = (await overtimeStore.fetchAllRequests({
			employee: Number(employeeId),
			request_date: date,
			start_date: date,
			end_date: date,
		})) as RawOvertimeResponse[]

		if (requests.length > 0) {
			const sorted = [...requests].sort((a, b) => {
				const aCreated = new Date(a.created_at || a.request_date || 0).getTime()
				const bCreated = new Date(b.created_at || b.request_date || 0).getTime()
				if (bCreated !== aCreated) return bCreated - aCreated
				const aStart = a.time_start || ''
				const bStart = b.time_start || ''
				return aStart.localeCompare(bStart)
			})
			const request = sorted[0]
			if (request) {
				submittedRequestId.value = request.id ?? null
				submittedRequestStatus.value = request.status ?? null

				const extractTime = (value: unknown): string => {
					if (!value) return ''
					const str = String(value)
					const match = str.match(/^(\d{1,2}:\d{2})/)
					return match?.[1] ?? ''
				}

				const reqProjectId = request.project ?? request.project_id
				form.selectedProject = reqProjectId ? String(reqProjectId) : ''
				form.timeStart = extractTime(request.time_start) || ''
				form.timeEnd = extractTime(request.time_end) || ''
				form.isHoliday = request.is_holiday ?? false
				form.reason = request.reason || ''
				form.details = request.detail || ''
				form.hasBreak = request.has_break ?? false

				if (request.has_break && request.breaks && request.breaks.length > 0) {
					form.breakStart = extractTime(request.breaks[0]?.start_time)
					form.breakEnd = extractTime(request.breaks[0]?.end_time)
					if (request.breaks.length > 1) {
						form.breakStart2 = extractTime(request.breaks[1]?.start_time)
						form.breakEnd2 = extractTime(request.breaks[1]?.end_time)
					}
					if (request.breaks.length > 2) {
						form.breakStart3 = extractTime(request.breaks[2]?.start_time)
						form.breakEnd3 = extractTime(request.breaks[2]?.end_time)
					}
				} else if (request.has_break && request.break_start && request.break_end) {
					form.breakStart = extractTime(request.break_start)
					form.breakEnd = extractTime(request.break_end)
				}
			}
		} else {
			submittedRequestId.value = null
			submittedRequestStatus.value = null
			form.selectedProject = ''
			form.timeStart = '17:20'
			form.timeEnd = '18:20'
			form.isHoliday = isDateHoliday(date)
			form.hasBreak = false
			form.breakStart = ''
			form.breakEnd = ''
			form.breakStart2 = ''
			form.breakEnd2 = ''
			form.breakStart3 = ''
			form.breakEnd3 = ''
			form.reason = ''
			form.details = ''
		}
	} catch (error) {
		console.error('Error checking existing request:', error)
		submittedRequestId.value = null
		submittedRequestStatus.value = null
	} finally {
		isLoadingExisting.value = false
	}
}

async function handleAutofill() {
	submitError.value = null
	if (!form.selectedEmployee) {
		submitError.value = t('otForm.validation.selectEmployee')
		return
	}

	try {
		isAutofilling.value = true
		const today = new Date()
		const yesterday = new Date(today)
		yesterday.setDate(today.getDate() - 1)
		const yesterdayFormatted = yesterday.toISOString().split('T')[0]

		const requests = (await overtimeStore.fetchAllRequests({
			employee: Number(form.selectedEmployee),
			request_date: yesterdayFormatted,
			start_date: yesterdayFormatted,
			end_date: yesterdayFormatted,
		})) as RawOvertimeResponse[]

		if (requests.length === 0) {
			submitError.value = t('otForm.messages.noDataYesterday')
			return
		}

		const request = requests[0]
		if (!request) {
			submitError.value = t('otForm.messages.noValidDataYesterday')
			return
		}

		const reqProjectId = request.project ?? request.project_id
		form.selectedProject = reqProjectId ? String(reqProjectId) : ''
		form.timeStart = request.time_start?.slice(0, 5) || ''
		form.timeEnd = request.time_end?.slice(0, 5) || ''
		form.isHoliday = request.is_holiday ?? false
		form.reason = request.reason || ''
		form.details = request.detail || ''
		form.hasBreak = request.has_break ?? false

		if (request.has_break && request.breaks && request.breaks.length > 0) {
			form.breakStart = request.breaks[0]?.start_time?.slice(0, 5) || ''
			form.breakEnd = request.breaks[0]?.end_time?.slice(0, 5) || ''
			if (request.breaks.length > 1) {
				form.breakStart2 = request.breaks[1]?.start_time?.slice(0, 5) || ''
				form.breakEnd2 = request.breaks[1]?.end_time?.slice(0, 5) || ''
			}
			if (request.breaks.length > 2) {
				form.breakStart3 = request.breaks[2]?.start_time?.slice(0, 5) || ''
				form.breakEnd3 = request.breaks[2]?.end_time?.slice(0, 5) || ''
			}
		} else if (request.has_break && request.break_start && request.break_end) {
			form.breakStart = request.break_start.slice(0, 5)
			form.breakEnd = request.break_end.slice(0, 5)
			form.breakStart2 = ''
			form.breakEnd2 = ''
			form.breakStart3 = ''
			form.breakEnd3 = ''
		}

		submitSuccess.value = false
		submitError.value = null
		scheduleBreaks()
	} catch (error) {
		console.error(error)
		submitError.value = t('otForm.messages.autofillFailed')
	} finally {
		isAutofilling.value = false
	}
}

// ── Submit / Delete ───────────────────────────────────────────────

async function handleSubmit() {
	submitError.value = null
	submitSuccess.value = false
	const validationError = validate()
	if (validationError) {
		submitError.value = validationError
		return
	}

	const projectId = Number(form.selectedProject)
	if (!Number.isFinite(projectId)) {
		submitError.value = t('otForm.validation.projectInvalid')
		return
	}

	isSubmitting.value = true
	try {
		const computedTotalHours = Number(totalHours.value.toFixed(2))

		const payload = {
			employee: Number.parseInt(form.selectedEmployee, 10),
			project: projectId,
			project_id: projectId,
			request_date: form.selectedDate,
			time_start: form.timeStart,
			time_end: form.timeEnd,
			total_hours: computedTotalHours,
			has_break: form.hasBreak,
			break_start: form.hasBreak && form.breakStart ? form.breakStart : undefined,
			break_end: form.hasBreak && form.breakEnd ? form.breakEnd : undefined,
			is_holiday: form.isHoliday,
			is_weekend: isWeekend(form.selectedDate),
			reason: form.reason,
			detail: form.details,
		}

		let result: RawOvertimeResponse | null = null
		const isUpdate = !!submittedRequestId.value
		if (submittedRequestId.value) {
			result = await overtimeStore.updateRequest(submittedRequestId.value, payload)
		} else {
			result = await overtimeStore.createRequest(payload)
		}

		submitSuccess.value = true
		successMessage.value = isUpdate ? t('otForm.messages.updated') : t('otForm.messages.submitted')
		submittedRequestId.value = result?.id ?? null
		if (result?.project) {
			form.selectedProject = String(result.project)
		} else if (result?.project_id) {
			form.selectedProject = String(result.project_id)
		} else {
			form.selectedProject = String(projectId)
		}

		await calculateEmployeeOvertime(form.selectedEmployee, form.selectedDate)
	} catch (error) {
		console.error(error)
		submitError.value = overtimeStore.error || t('otForm.messages.saveFailed')
	} finally {
		isSubmitting.value = false
	}
}

function adjustDuration(deltaHours: number) {
	const end = new Date(`1970-01-01T${form.timeEnd}:00`)
	const newDate = new Date(end.getTime() + deltaHours * 60 * 60 * 1000)
	const hh = String(newDate.getHours()).padStart(2, '0')
	const mm = String(newDate.getMinutes()).padStart(2, '0')
	form.timeEnd = `${hh}:${mm}`
}

async function handleDelete() {
	showDeleteModal.value = false
	if (!submittedRequestId.value) return

	isSubmitting.value = true
	try {
		await overtimeStore.deleteRequest(submittedRequestId.value)
		submittedRequestId.value = null
		submittedRequestStatus.value = null
		handleReset()

		successMessage.value = 'Overtime request has been successfully deleted.'
		submitSuccess.value = true

		await calculateEmployeeOvertime(form.selectedEmployee, form.selectedDate)
	} catch (error) {
		console.error(error)
		submitError.value = overtimeStore.error || 'Failed to delete request.'
	} finally {
		isSubmitting.value = false
	}
}

// ── Watchers ──────────────────────────────────────────────────────

watch(
	() => [form.timeStart, form.timeEnd],
	() => {
		scheduleBreaks()
	},
	{ immediate: true },
)

watch(
	() => rawHours.value,
	(val) => {
		if (val > 4 && !form.hasBreak) {
			scheduleBreaks()
		}
	},
)

watch(
	() => form.hasBreak,
	(val) => {
		if (!val && rawHours.value > 4) {
			scheduleBreaks()
		}
	},
)

watch(
	() => [
		form.timeStart,
		form.timeEnd,
		form.hasBreak,
		form.breakStart,
		form.breakEnd,
		form.breakStart2,
		form.breakEnd2,
		form.breakStart3,
		form.breakEnd3,
		form.isHoliday,
	],
	() => {
		submitSuccess.value = false
	},
	{ deep: true },
)

watch(
	() => form.selectedEmployee,
	async (newEmployee) => {
		if (isInitializing.value) return
		if (newEmployee && form.selectedDate) {
			await Promise.all([
				calculateEmployeeOvertime(newEmployee, form.selectedDate),
				checkExistingRequest(newEmployee, form.selectedDate),
			])
		}
	},
)

watch(
	() => form.selectedDate,
	async (newDate) => {
		if (isInitializing.value) return

		if (newDate) {
			const newYear = new Date(newDate).getFullYear()
			const firstHoliday = holidays.value[0]
			const currentYear =
				holidays.value.length > 0 && firstHoliday ? new Date(firstHoliday.date).getFullYear() : null
			if (currentYear !== newYear) {
				await fetchHolidays(newYear)
			}

			if (!submittedRequestId.value && isDateHoliday(newDate)) {
				form.isHoliday = true
			} else if (!submittedRequestId.value && !isDateHoliday(newDate)) {
				form.isHoliday = false
			}

			if (form.selectedEmployee) {
				await Promise.all([
					calculateEmployeeOvertime(form.selectedEmployee, newDate),
					checkExistingRequest(form.selectedEmployee, newDate),
				])
			}
		}
	},
)

// ── Computed v-model wrappers (normalize Date ↔ string) ───────────

const selectedEmployee = computed({
	get: () => form.selectedEmployee,
	set: (v: string) => {
		form.selectedEmployee = v
	},
})

const selectedProject = computed({
	get: () => form.selectedProject,
	set: (v: string) => {
		form.selectedProject = v
	},
})

const selectedDate = computed({
	get: () => form.selectedDate,
	set: (v: string | Date) => {
		form.selectedDate = normalizeDateValue(v)
	},
})

const timeStart = computed({
	get: () => form.timeStart,
	set: (v: string | Date) => {
		form.timeStart = normalizeTimeValue(v)
	},
})

const timeEnd = computed({
	get: () => form.timeEnd,
	set: (v: string | Date) => {
		form.timeEnd = normalizeTimeValue(v)
	},
})

const isHoliday = computed({
	get: () => form.isHoliday,
	set: (v: boolean) => {
		form.isHoliday = v
	},
})

const hasBreak = computed({
	get: () => form.hasBreak,
	set: (v: boolean) => {
		form.hasBreak = v
	},
})

const breakStart = computed({
	get: () => form.breakStart,
	set: (v: string | Date) => {
		form.breakStart = normalizeTimeValue(v)
	},
})

const breakEnd = computed({
	get: () => form.breakEnd,
	set: (v: string | Date) => {
		form.breakEnd = normalizeTimeValue(v)
	},
})

const breakStart2 = computed({
	get: () => form.breakStart2,
	set: (v: string | Date) => {
		form.breakStart2 = normalizeTimeValue(v)
	},
})

const breakEnd2 = computed({
	get: () => form.breakEnd2,
	set: (v: string | Date) => {
		form.breakEnd2 = normalizeTimeValue(v)
	},
})

const breakStart3 = computed({
	get: () => form.breakStart3,
	set: (v: string | Date) => {
		form.breakStart3 = normalizeTimeValue(v)
	},
})

const breakEnd3 = computed({
	get: () => form.breakEnd3,
	set: (v: string | Date) => {
		form.breakEnd3 = normalizeTimeValue(v)
	},
})

const reason = computed({
	get: () => form.reason,
	set: (v: string) => {
		form.reason = v
	},
})

const details = computed({
	get: () => form.details,
	set: (v: string) => {
		form.details = v
	},
})

// ── Lifecycle ─────────────────────────────────────────────────────

onMounted(async () => {
	await Promise.all([
		employeeStore.fetchEmployees(),
		projectStore.fetchProjects(),
		fetchHolidays(),
		loadLimits(),
	])

	let targetEmployeeId = form.selectedEmployee

	const currentUser = authStore.user
	if (currentUser?.worker_id) {
		const matchingEmployee = employees.value.find(
			(emp) => emp.code.toLowerCase() === currentUser.worker_id?.toLowerCase(),
		)

		if (matchingEmployee) {
			targetEmployeeId = matchingEmployee.id
			form.selectedEmployee = matchingEmployee.id
		} else {
			console.warn('No matching employee found for current user:', currentUser.worker_id)
		}
	}

	if (!targetEmployeeId && employees.value?.length > 0) {
		const firstEmployee = employees.value[0]
		if (firstEmployee) {
			targetEmployeeId = firstEmployee.id
			form.selectedEmployee = targetEmployeeId
		}
	}

	if (targetEmployeeId) {
		await checkExistingRequest(targetEmployeeId, form.selectedDate)

		if (!submittedRequestId.value && isDateHoliday(form.selectedDate)) {
			form.isHoliday = true
		}

		await calculateEmployeeOvertime(targetEmployeeId, form.selectedDate)
	} else {
		if (isDateHoliday(form.selectedDate)) {
			form.isHoliday = true
		}
	}

	isInitializing.value = false
})

onUnmounted(() => {
	destroyFlatpickrs()
})
</script>


<style scoped>
/* Holiday marker dot on flatpickr calendar days */
:deep(.ot-holiday-day) {
	position: relative;
	background-color: rgba(239, 68, 68, 0.1) !important;
}

:deep(.ot-holiday-day::after) {
	content: '';
	position: absolute;
	bottom: 2px;
	left: 50%;
	transform: translateX(-50%);
	width: 5px;
	height: 5px;
	border-radius: 50%;
	background-color: #ef4444;
}

:deep(.ot-holiday-day:hover) {
	background-color: rgba(239, 68, 68, 0.2) !important;
}

/* When a holiday day is selected, keep the brand color but show the dot */
:deep(.ot-holiday-day.selected) {
	background-color: var(--color-brand-500, #465fff) !important;
}

:deep(.ot-holiday-day.selected::after) {
	background-color: #ffffff;
}
</style>
