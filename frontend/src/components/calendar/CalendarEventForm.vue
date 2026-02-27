<template>
  <div class="fixed inset-0 z-[100000] flex items-center justify-center bg-black/50 px-4" @click.self="emit('close')">
    <div
      class="flex w-full max-w-3xl flex-col rounded-2xl border border-gray-200 bg-white shadow-theme-lg dark:border-gray-800 dark:bg-gray-900 max-h-[90vh]">
      <!-- Fixed Header -->
      <div class="flex items-start justify-between gap-3 border-b border-gray-200 py-4 px-6 dark:border-gray-700">
        <div>
          <p class="text-sm font-semibold text-brand-500">Calendar</p>
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white">
            {{ isEdit ? 'Edit Event' : 'Create Event' }}
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">Configure event details and attendees.</p>
        </div>
        <button type="button" @click="emit('close')"
          class="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 text-gray-500 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5">
          <span class="sr-only">Close</span>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="h-5 w-5">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Scrollable Content -->
      <div class="flex-1 overflow-y-auto px-6 py-4">
        <div v-if="formError"
          class="mb-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-700 dark:border-error-500/40 dark:bg-error-500/10 dark:text-error-200">
          {{ formError }}
        </div>

        <form @submit.prevent="handleSubmit" id="event-form">
          <fieldset :disabled="isReadOnly" class="space-y-5 block border-none p-0 min-w-0">
            <div class="grid gap-4" :class="formState.event_type === 'leave' ? 'md:grid-cols-2' : ''">
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Event Type*</label>
                <select v-model="formState.event_type"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                  required @change="handleTypeChange">
                  <option value="">Select event type</option>
                  <option v-for="option in eventTypes" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </div>

              <div v-if="formState.event_type === 'leave'" class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Leave Type*</label>
                <select v-model="formState.leave_type"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                  required>
                  <option value="">Select leave type</option>
                  <option value="personal">Personal</option>
                  <option value="legal">Legal</option>
                  <option value="official">Official</option>
                </select>
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ titleLabel }}*</label>
              <input v-model="formState.title" type="text"
                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                :placeholder="`Enter ${titleLabel.toLowerCase()}`" required />
            </div>

            <div v-if="formState.event_type === 'meeting'" class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Meeting URL*</label>
              <input v-model="formState.meeting_url" type="url"
                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                placeholder="https://..." required />
            </div>

            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">All Day</label>
                <label
                  class="flex h-11 cursor-pointer items-center gap-3 rounded-lg border border-gray-300 px-3 text-sm text-gray-800 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-700 dark:text-white/90 dark:hover:bg-white/5"
                  :class="{ 'cursor-not-allowed opacity-70': formState.event_type === 'holiday' }">
                  <input v-model="formState.all_day" type="checkbox"
                    :disabled="formState.event_type === 'holiday'"
                    class="h-4 w-4 cursor-pointer rounded border-gray-300 text-brand-600 focus:ring-brand-500 disabled:cursor-not-allowed" />
                  <span>Mark as full-day event</span>
                </label>
              </div>
              <div v-if="formState.event_type !== 'holiday'" class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Repeating Event</label>
                <label
                  class="flex h-11 cursor-pointer items-center gap-3 rounded-lg border border-gray-300 px-3 text-sm text-gray-800 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-700 dark:text-white/90 dark:hover:bg-white/5">
                  <input v-model="formState.is_repeating" type="checkbox"
                    class="h-4 w-4 cursor-pointer rounded border-gray-300 text-brand-600 focus:ring-brand-500" />
                  <span>Repeat this event</span>
                </label>
              </div>
            </div>

            <!-- Repeat Frequency (shown when Repeating Event is checked) -->
            <div v-if="formState.is_repeating" class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Repeat Frequency*</label>
              <select v-model="formState.repeat_frequency"
                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                required>
                <option value="">Select frequency</option>
                <option v-for="option in repeatFrequencyOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <!-- Date/Time Fields - Holiday: Single Date, Others: Start-End -->
            <div v-if="formState.event_type === 'holiday'" class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Date*</label>
              <flat-pickr v-model="startDate" :config="datePickerConfig"
                class="h-11 w-full cursor-pointer rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                placeholder="Select holiday date" required @change="syncHolidayDate" />
            </div>

            <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Start*</label>
                <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <flat-pickr v-model="startDate" :config="datePickerConfig"
                    class="h-11 w-full cursor-pointer rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                    placeholder="Select date" required />
                  <flat-pickr v-model="startTime" :config="timePickerConfig" :disabled="formState.all_day"
                    class="h-11 w-full cursor-pointer rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:dark:bg-gray-800"
                    placeholder="Select time" required />
                </div>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">End*</label>
                <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <flat-pickr v-model="endDate" :config="datePickerConfig"
                    class="h-11 w-full cursor-pointer rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                    placeholder="Select date" required />
                  <flat-pickr v-model="endTime" :config="timePickerConfig" :disabled="formState.all_day"
                    class="h-11 w-full cursor-pointer rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:dark:bg-gray-800"
                    placeholder="Select time" required />
                </div>
              </div>
            </div>

            <div v-if="formState.event_type === 'task'" class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Project*</label>
              <select v-model.number="formState.project"
                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                required>
                <option value="" class="text-center">Select project</option>
                <option v-for="project in projectsSorted" :key="project.id" :value="project.id" class="text-center">
                  {{ project.name }}
                </option>
              </select>
            </div>

            <div v-if="formState.event_type === 'leave'" class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Applied By*</label>
                <select v-model.number="formState.applied_by"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                  required>
                  <option value="" class="text-center">Select employee</option>
                  <option v-for="employee in activeEmployeesSorted" :key="employee.id" :value="employee.id" class="text-center">
                    {{ employee.name }}
                  </option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Agent*</label>
                <select v-model.number="formState.agent"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                  required>
                  <option value="" class="text-center">Select agent</option>
                  <option v-for="employee in activeEmployeesSorted" :key="employee.id" :value="employee.id" class="text-center">
                    {{ employee.name }}
                  </option>
                </select>
              </div>
            </div>

            <div v-if="['meeting', 'task'].includes(formState.event_type)" class="space-y-2">
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Send To</label>
                <div class="flex gap-2">
                  <button type="button" @click="selectAllAssignees"
                    class="text-xs text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300">
                    Select All
                  </button>
                  <span class="text-gray-300 dark:text-gray-600">|</span>
                  <button type="button" @click="deselectAllAssignees"
                    class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                    Deselect All
                  </button>
                </div>
              </div>
              <div
                class="max-h-48 overflow-y-auto rounded-xl border border-gray-200 bg-gray-50 p-2 dark:border-gray-700 dark:bg-gray-800/40 space-y-1">
                <button v-for="employee in activeEmployeesSorted" :key="employee.id" type="button"
                  @click="toggleAssignee(employee.id)" :class="[
                    'w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left text-sm transition-colors',
                    formState.assigned_to.includes(employee.id)
                      ? 'bg-brand-50 dark:bg-brand-900/30 border border-brand-300 dark:border-brand-700 text-brand-700 dark:text-brand-300'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                  ]">
                  <div :class="[
                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                    formState.assigned_to.includes(employee.id)
                      ? 'bg-brand-200 dark:bg-brand-800 text-brand-700 dark:text-brand-300'
                      : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                  ]">
                    {{ getInitials(employee.name) }}
                  </div>
                  <span class="flex-1 truncate">{{ employee.name }}</span>
                  <svg v-if="formState.assigned_to.includes(employee.id)" xmlns="http://www.w3.org/2000/svg"
                    class="w-4 h-4 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
                <p v-if="activeEmployeesSorted.length === 0" class="text-center text-gray-400 text-sm py-2">No employees available</p>
              </div>
              <p v-if="formState.assigned_to.length > 0" class="text-xs text-gray-500 dark:text-gray-400">
                {{ formState.assigned_to.length }} recipient(s) selected
              </p>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Description</label>
              <textarea v-model="formState.description" rows="3"
                class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                placeholder="Optional details"></textarea>
            </div>
          </fieldset>
        </form>
      </div>

      <!-- Fixed Footer -->
      <div class="border-t border-gray-200 py-4 px-6 dark:border-gray-700">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
          <button type="button"
            class="h-11 flex-1 rounded-lg border border-gray-300 px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5 sm:flex-none sm:min-w-[100px]"
            @click="emit('close')">
            Cancel
          </button>
          <button v-if="isEdit && canDelete" type="button"
            class="h-11 flex-1 rounded-lg border border-error-300 px-4 text-sm font-semibold text-error-600 transition hover:bg-error-50 focus:outline-hidden focus:ring-3 focus:ring-error-500/10 dark:border-error-500/30 dark:text-error-400 dark:hover:bg-error-500/10 sm:flex-none sm:min-w-[100px]"
            :disabled="submitting" @click="handleDelete">
            Delete
          </button>
          <button v-if="!isReadOnly" type="submit" form="event-form"
            class="h-11 flex-1 rounded-lg bg-brand-600 px-5 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 disabled:cursor-not-allowed disabled:opacity-60 sm:flex-none sm:min-w-[100px]"
            :disabled="submitting || !canSubmit">
            {{ submitting ? 'Saving...' : isEdit ? 'Update' : 'Create' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DateSelectData, EventApi } from '@fullcalendar/core'
import { computed, onUnmounted, reactive, ref, watch } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useFlatpickrScroll } from '@/composables/useFlatpickrScroll'
import type { Employee } from '@/services/api/employee'
import type { Project } from '@/services/api/project'
import type { CalendarEventPayload, CalendarEventType } from '@/types/calendar'

interface CalendarEventFormState {
	event_type: CalendarEventType | ''
	title: string
	description: string
	start_date: string | null
	end_date: string | null
	start_time: string | null
	end_time: string | null
	meeting_url: string
	project: number | null
	applied_by: number | null
	agent: number | null
	leave_type: string
	assigned_to: number[]
	all_day: boolean
	is_repeating: boolean
	repeat_frequency: 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | ''
}

const props = withDefaults(
	defineProps<{
		visible: boolean
		event: EventApi | null
		selectInfo: DateSelectData | null
		employees: Employee[]
		projects: Project[]
		submitting?: boolean
		canUpdate?: boolean
		canDelete?: boolean
	}>(),
	{
		canUpdate: true,
		canDelete: true,
	},
)

const emit = defineEmits<{
	(e: 'close'): void
	(e: 'submit', payload: CalendarEventPayload): void
	(e: 'delete', id: string | number): void
}>()

const eventTypes: { value: CalendarEventType; label: string }[] = [
	{ value: 'holiday', label: 'Holiday' },
	{ value: 'leave', label: 'Leave' },
	{ value: 'meeting', label: 'Meeting' },
	{ value: 'task', label: 'Task' },
]

const repeatFrequencyOptions: { value: string; label: string }[] = [
	{ value: 'hourly', label: 'Every Hour' },
	{ value: 'daily', label: 'Every Day' },
	{ value: 'weekly', label: 'Every Week' },
	{ value: 'monthly', label: 'Every Month' },
	{ value: 'yearly', label: 'Every Year' },
]

// Active employees sorted alphabetically
const activeEmployeesSorted = computed(() => {
	return [...props.employees]
		.filter((e) => e.is_enabled)
		.sort((a, b) => a.name.localeCompare(b.name))
})

// Projects sorted alphabetically
const projectsSorted = computed(() => {
	return [...props.projects].sort((a, b) => a.name.localeCompare(b.name))
})

// Helper function to get initials from name
const getInitials = (name: string) => {
	return name
		.split(' ')
		.map((n) => n[0])
		.join('')
		.substring(0, 2)
		.toUpperCase()
}

// Track flatpickr instances for cleanup
const { flatpickrInstances, attachMonthScroll, attachTimeScroll, destroyFlatpickrs } =
	useFlatpickrScroll()

const datePickerConfig = {
	dateFormat: 'Y-m-d',
	altInput: false,
	allowInput: true,
	static: false,
	appendTo: typeof document !== 'undefined' ? document.body : undefined,
	onReady: (
		_selectedDates: unknown,
		_dateStr: string,
		instance: Parameters<typeof attachMonthScroll>[0],
	) => {
		flatpickrInstances.value.push(instance)
		attachMonthScroll(instance)
	},
}

const timePickerConfig = {
	enableTime: true,
	noCalendar: true,
	dateFormat: 'H:i',
	time_24hr: true,
	minuteIncrement: 5,
	allowInput: true,
	static: false,
	appendTo: typeof document !== 'undefined' ? document.body : undefined,
	onReady: (
		_selectedDates: unknown,
		_dateStr: string,
		instance: Parameters<typeof attachMonthScroll>[0],
	) => {
		flatpickrInstances.value.push(instance)
		attachTimeScroll(instance)
	},
}

// Helper functions to normalize flatpickr values
function normalizeTimeValue(value: string | Date | null): string | null {
	if (!value) return null
	if (value instanceof Date) {
		const hh = String(value.getHours()).padStart(2, '0')
		const mm = String(value.getMinutes()).padStart(2, '0')
		return `${hh}:${mm}`
	}
	return value
}

function normalizeDateValue(value: string | Date | null): string | null {
	if (!value) return null
	if (value instanceof Date) {
		const year = value.getFullYear()
		const month = String(value.getMonth() + 1).padStart(2, '0')
		const day = String(value.getDate()).padStart(2, '0')
		return `${year}-${month}-${day}`
	}
	return value
}

const formError = ref<string | null>(null)
const currentEventId = ref<string | number | null>(null)

const defaultState = (): CalendarEventFormState => {
	const now = new Date()
	const today = now.toISOString().split('T')[0] ?? null
	const time = now.toTimeString().slice(0, 5)
	return {
		event_type: '',
		title: '',
		description: '',
		start_date: today,
		end_date: today,
		start_time: time,
		end_time: time,
		meeting_url: '',
		project: null,
		applied_by: null,
		agent: null,
		leave_type: '',
		assigned_to: [],
		all_day: false,
		is_repeating: false,
		repeat_frequency: '',
	}
}

const formState = reactive<CalendarEventFormState>(defaultState())

const titleLabel = computed(() => {
	switch (formState.event_type) {
		case 'holiday':
			return 'Holiday Title'
		case 'leave':
			return 'Leave Reason'
		case 'meeting':
			return 'Meeting Title'
		case 'task':
			return 'Task Title'
		default:
			return 'Title'
	}
})

const isEdit = computed(() => !!currentEventId.value)

const isReadOnly = computed(() => isEdit.value && !props.canUpdate)

const canSubmit = computed(() => {
	if (isReadOnly.value) return false
	if (!formState.event_type || !formState.title) return false
	if (!formState.start_date || !formState.end_date) return false
	if (!formState.all_day && (!formState.start_time || !formState.end_time)) return false
	if (formState.event_type === 'meeting' && !formState.meeting_url) return false
	if (formState.event_type === 'task' && !formState.project) return false
	if (formState.event_type === 'leave' && (!formState.applied_by || !formState.agent)) return false
	if (formState.is_repeating && !formState.repeat_frequency) return false

	const start = buildDate(formState.start_date, formState.start_time || '00:00')
	const end = buildDate(formState.end_date, formState.end_time || '00:00')
	return start.getTime() <= end.getTime()
})

const buildDate = (date: string, time: string) => new Date(`${date}T${time || '00:00'}`)

const resetForm = () => {
	Object.assign(formState, defaultState())
	formError.value = null
	currentEventId.value = null
}

const hydrateFromSelection = (selection: DateSelectData | null) => {
	resetForm()
	if (!selection) return
	const start = selection.start || new Date()
	const end = selection.end || selection.start || new Date()
	formState.start_date = start.toISOString().split('T')[0] ?? null
	formState.end_date = end.toISOString().split('T')[0] ?? null
	formState.start_time = start.toTimeString().slice(0, 5)
	formState.end_time = end.toTimeString().slice(0, 5)
	// formState.all_day = !!selection.allDay
}

const hydrateFromEvent = (event: EventApi) => {
	resetForm()
	currentEventId.value = event.id
	const start = event.start || new Date()
	const end = event.end || event.start || new Date()
	formState.event_type = (event.extendedProps?.event_type as CalendarEventType) || 'task'
	formState.title = event.title || ''
	formState.description = event.extendedProps?.description || ''
	formState.start_date = start.toISOString().split('T')[0] ?? null
	formState.end_date = end.toISOString().split('T')[0] ?? null
	formState.start_time = start.toTimeString().slice(0, 5)
	formState.end_time = end.toTimeString().slice(0, 5)
	formState.meeting_url = event.extendedProps?.meeting_url || ''
	formState.project = event.extendedProps?.project || null
	formState.applied_by = event.extendedProps?.applied_by || null
	formState.agent = event.extendedProps?.agent || null
	formState.leave_type = event.extendedProps?.leave_type || ''
	formState.assigned_to = event.extendedProps?.assigned_to || []
	formState.all_day = !!event.allDay || !!event.extendedProps?.all_day
	formState.is_repeating = event.extendedProps?.is_repeating || false
	formState.repeat_frequency = event.extendedProps?.repeat_frequency || ''
}

const handleSubmit = () => {
	formError.value = null
	if (!canSubmit.value) {
		formError.value = 'Please complete required fields before saving.'
		return
	}

	if (!formState.start_date || !formState.end_date) {
		formError.value = 'Please select start and end dates.'
		return
	}

	const startDate = buildDate(
		formState.start_date,
		formState.all_day ? '00:00' : formState.start_time || '00:00',
	)
	const endDate = buildDate(
		formState.end_date,
		formState.all_day ? '23:59' : formState.end_time || '23:59',
	)

	if (endDate.getTime() < startDate.getTime()) {
		formError.value = 'End date/time must be after start date/time.'
		return
	}

	const payload: CalendarEventPayload = {
		event_type: formState.event_type || 'task',
		title: formState.title,
		start: startDate.toISOString(),
		end: endDate.toISOString(),
		description: formState.description || undefined,
		meeting_url: formState.meeting_url || undefined,
		project: formState.project || undefined,
		applied_by: formState.applied_by || undefined,
		agent: formState.agent || undefined,
		leave_type: formState.leave_type || undefined,
		assigned_to: formState.assigned_to?.length ? formState.assigned_to : undefined,
		all_day: formState.all_day,
		is_repeating: formState.is_repeating || undefined,
		repeat_frequency:
			formState.is_repeating && formState.repeat_frequency
				? (formState.repeat_frequency as CalendarEventPayload['repeat_frequency'])
				: undefined,
	}

	emit('submit', payload)
}

const handleDelete = () => {
	if (!currentEventId.value) return
	emit('delete', currentEventId.value)
}

const handleTypeChange = () => {
	// Reset type-specific fields when type changes
	formState.meeting_url = ''
	formState.project = null
	formState.applied_by = null
	formState.agent = null
	formState.leave_type = ''
	formState.assigned_to = []
	if (formState.event_type === 'holiday') {
		// Holiday: All day, single date, no repeating
		formState.all_day = true
		formState.is_repeating = false
		formState.repeat_frequency = ''
		formState.start_time = '00:00'
		formState.end_time = '23:59'
		// Sync end date to start date for single date field
		formState.end_date = formState.start_date
	} else if (formState.event_type === 'leave') {
		formState.all_day = true
		formState.start_time = '00:00'
		formState.end_time = '23:59'
	} else {
		formState.all_day = false
	}
}

// Sync end date when start date changes for holiday (single date field)
const syncHolidayDate = () => {
	if (formState.event_type === 'holiday') {
		formState.end_date = formState.start_date
	}
}

// Toggle assignee in form
const toggleAssignee = (empId: number) => {
	const idx = formState.assigned_to.indexOf(empId)
	if (idx > -1) {
		formState.assigned_to.splice(idx, 1)
	} else {
		formState.assigned_to.push(empId)
	}
}

// Select all assignees
const selectAllAssignees = () => {
	formState.assigned_to = activeEmployeesSorted.value.map((emp) => emp.id)
}

// Deselect all assignees
const deselectAllAssignees = () => {
	formState.assigned_to = []
}

watch(
	() => props.visible,
	(open) => {
		if (open) {
			if (props.event) {
				hydrateFromEvent(props.event)
			} else {
				hydrateFromSelection(props.selectInfo)
			}
		} else {
			resetForm()
		}
	},
	{ immediate: true },
)

watch(
	() => props.selectInfo,
	(selection) => {
		if (props.visible && !props.event) {
			hydrateFromSelection(selection)
		}
	},
)

// Lock/unlock body scroll when modal opens/closes
watch(
	() => props.visible,
	(isVisible) => {
		if (typeof document !== 'undefined') {
			if (isVisible) {
				document.body.style.overflow = 'hidden'
			} else {
				document.body.style.overflow = ''
			}
		}
	},
)

// Computed properties for flatpickr v-model binding
const startDate = computed({
	get: () => formState.start_date,
	set: (v: string | Date | null) => {
		formState.start_date = normalizeDateValue(v)
	},
})

const endDate = computed({
	get: () => formState.end_date,
	set: (v: string | Date | null) => {
		formState.end_date = normalizeDateValue(v)
	},
})

const startTime = computed({
	get: () => formState.start_time,
	set: (v: string | Date | null) => {
		formState.start_time = normalizeTimeValue(v)
	},
})

const endTime = computed({
	get: () => formState.end_time,
	set: (v: string | Date | null) => {
		formState.end_time = normalizeTimeValue(v)
	},
})

// Cleanup flatpickr instances on unmount
onUnmounted(() => {
	destroyFlatpickrs()

	// Ensure body scroll is restored
	if (typeof document !== 'undefined') {
		document.body.style.overflow = ''
	}
})
</script>

<style>
/* Ensure flatpickr calendar appears above the modal */
.flatpickr-calendar {
  z-index: 100001 !important;
}
</style>
