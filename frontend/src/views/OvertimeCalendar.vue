<template>
	<AdminLayout>
		<div class="space-y-6">
			<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<!-- <p class="text-sm font-semibold text-brand-500">Others</p> -->
					<h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.calendar.title') }}
					</h1>
					<p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.calendar.subtitle') }}</p>
				</div>
				<div class="flex flex-wrap items-center gap-2 sm:justify-end">
					<select v-model="selectedTheme"
						class="h-10 rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-700 shadow-theme-xs hover:bg-gray-50 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700">
						<option v-for="theme in themeOptions" :key="theme.value" :value="theme.value">
							{{ theme.label }}
						</option>
					</select>
					<button v-if="canCreate" type="button"
						class="h-10 rounded-lg border border-brand-300 bg-brand-50 px-4 text-sm font-semibold text-brand-700 transition hover:bg-brand-100 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-200"
						@click="openCreateEvent">
						+ Add Event
					</button>
				</div>
			</div>

			<div
				class="rounded-2xl border border-gray-200 bg-white p-3 shadow-theme-sm dark:border-gray-800 dark:bg-gray-900">
				<div class="relative">
					<FullCalendar ref="calendarRef" :options="calendarOptions" class="min-h-[680px]" />
					<div v-if="isPageLoading"
						class="absolute inset-0 z-10 flex items-center justify-center rounded-xl bg-white/70 backdrop-blur-sm dark:bg-gray-900/70">
						<div class="h-10 w-10 animate-spin rounded-full border-2 border-brand-500 border-t-transparent">
						</div>
					</div>
				</div>
				<p v-if="error" class="mt-3 text-sm text-error-600 dark:text-error-400">{{ error }}</p>
			</div>
		</div>

		<CalendarEventForm v-if="showForm" :visible="showForm" :event="selectedEvent" :select-info="selectInfo"
			:employees="employees" :projects="projects" :submitting="isSubmitting" :can-update="canUpdate"
			:can-delete="canDelete" @close="closeForm" @submit="handleSaveEvent" @delete="handleDeleteEvent" />
	</AdminLayout>
</template>

<script setup lang="ts">
import type {
	CalendarApi,
	CalendarOptions,
	DateSelectData,
	EventApi,
	EventClickData,
} from '@fullcalendar/core'
import breezyTheme from '@fullcalendar/theme-breezy'
import formaTheme from '@fullcalendar/theme-forma'
import pulseTheme from '@fullcalendar/theme-pulse'
import FullCalendar from '@fullcalendar/vue3'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import '@fullcalendar/core/skeleton.css'

// Theme CSS is loaded dynamically — only the active theme is imported.
// See loadThemeCSS() below.
const themeCSSLoaders: Record<string, () => Promise<unknown>> = {
	breezy: () =>
		Promise.all([
			import('@fullcalendar/theme-breezy/theme.css'),
			import('@fullcalendar/theme-breezy/palettes/indigo.css'),
		]),
	forma: () =>
		Promise.all([
			import('@fullcalendar/theme-forma/theme.css'),
			import('@fullcalendar/theme-forma/palettes/purple.css'),
		]),
	pulse: () =>
		Promise.all([
			import('@fullcalendar/theme-pulse/theme.css'),
			import('@fullcalendar/theme-pulse/palettes/purple.css'),
		]),
}

const loadThemeCSS = (theme: string) => {
	themeCSSLoaders[theme]?.()
}

import CalendarEventForm from '@/components/calendar/CalendarEventForm.vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { useCalendarHandlers } from '@/composables/calendar/useCalendarHandlers'
import { useCalendarOptions } from '@/composables/calendar/useCalendarOptions'
import { useToast } from '@/composables/useToast'
import { STORAGE_KEY_CALENDAR_THEME, STORAGE_KEY_CALENDAR_VIEW } from '@/constants/storage'
import type { CalendarEvent } from '@/services/api/calendar'
import { useAuthStore } from '@/stores/auth'
import { useCalendarStore } from '@/stores/calendar'
import { useEmployeeStore } from '@/stores/employee'
import { useProjectStore } from '@/stores/project'
import type { CalendarEventPayload } from '@/types/calendar'

// Pinia Stores
const { t } = useI18n()
const { showToast } = useToast()
const calendarStore = useCalendarStore()
const employeeStore = useEmployeeStore()
const projectStore = useProjectStore()
const authStore = useAuthStore()

const calendarRef = ref<{ getApi: () => CalendarApi } | null>(null)
const showForm = ref(false)
const selectedEvent = ref<EventApi | null>(null)
const selectInfo = ref<DateSelectData | null>(null)
const employees = computed(() => employeeStore.employees)
const projects = computed(() => projectStore.projects.filter((p) => p.is_enabled))
const isSubmitting = ref(false)
const isPageLoading = computed(() => calendarStore.loading)

// Permissions
const canCreate = computed(() => authStore.hasPermission('calendar', 'create'))
const canUpdate = computed(() => authStore.hasPermission('calendar', 'update'))
const canDelete = computed(() => authStore.hasPermission('calendar', 'delete'))

// Load theme from localStorage or default to 'breezy'
const loadThemeFromStorage = (): 'breezy' | 'forma' | 'pulse' => {
	const stored = localStorage.getItem(STORAGE_KEY_CALENDAR_THEME)
	if (stored === 'breezy' || stored === 'forma' || stored === 'pulse') {
		return stored
	}
	return 'breezy'
}

const selectedTheme = ref<'breezy' | 'forma' | 'pulse'>(loadThemeFromStorage())

const themeMap = {
	breezy: breezyTheme,
	forma: formaTheme,
	pulse: pulseTheme,
}

const themeOptions = [
	{ value: 'breezy', label: 'Breezy' },
	{ value: 'forma', label: 'Forma' },
	{ value: 'pulse', label: 'Pulse' },
]

// Event type color mapping
const getEventColor = (eventType: string | undefined): string => {
	switch (eventType) {
		case 'holiday':
			return '#10b981' // green
		case 'leave':
			return '#f59e0b' // amber
		case 'meeting':
			return '#6366f1' // indigo
		case 'task':
			return '#3b82f6' // blue
		default:
			return '#6b7280' // gray
	}
}

// Get current user's employee ID based on worker_id matching emp_id
const currentUserEmployeeId = computed(() => {
	const currentUser = authStore.user
	if (!currentUser?.worker_id) return null
	const matchingEmployee = employees.value.find(
		(emp) => emp.emp_id.toLowerCase() === currentUser.worker_id?.toLowerCase(),
	)
	return matchingEmployee?.id ?? null
})

// Computed events from store (mapped to FullCalendar format)
// For non-PTB admin users, Meeting and Task events are filtered to only show:
// - Events assigned to the current user
// - Events created by the current user
// Note: Holiday events are excluded from regular display and shown as background events
const events = computed(() => {
	const isPtbAdmin = authStore.isPtbAdmin
	const userEmpId = currentUserEmployeeId.value

	return calendarStore.events
		.filter((e) => {
			// Exclude holiday events from regular display (they are shown as background)
			if (e.event_type === 'holiday') return false

			// PTB admins see all events
			if (isPtbAdmin) return true

			// Non-restricted event types (leave) are visible to all
			if (e.event_type === 'leave') return true

			// For Meeting/Task events, check if user is assigned or created the event
			const isCreator = userEmpId && e.created_by === userEmpId
			const isAssigned = userEmpId && e.assigned_to?.includes(userEmpId)

			return isCreator || isAssigned
		})
		.map((e) => ({
			id: String(e.id),
			title: e.title,
			start: e.start,
			end: e.end,
			allDay: e.all_day,
			color: getEventColor(e.event_type),
			extendedProps: {
				event_type: e.event_type,
				description: e.description,
				employee_name: e.employee_name,
				project_name: e.project_name,
				created_by: e.created_by ?? null,
				assigned_to: e.assigned_to ?? [],
				meeting_url: e.meeting_url,
				project: e.project ?? null,
				applied_by: e.applied_by ?? null,
				agent: e.agent ?? null,
				// ensure leave_type survives drag/drop for leave events
				leave_type: e.leave_type,
				// Repeating event fields
				is_repeating: e.is_repeating ?? false,
				repeat_frequency: e.repeat_frequency ?? undefined,
				parent_event: e.parent_event ?? null,
			},
		}))
})

// Holiday events as background events (soft pink color on calendar dates)
const holidayBackgroundEvents = computed(() => {
	return calendarStore.events
		.filter((e) => e.event_type === 'holiday')
		.map((e) => ({
			id: `holiday-bg-${e.id}`,
			start: e.start,
			end: e.end,
			display: 'background' as const,
			backgroundColor: '#fce7f3', // soft pink (pink-100)
			extendedProps: {
				event_type: 'holiday',
				title: e.title,
				description: e.description,
			},
		}))
})

// Holiday events as regular events for List view (using inverse-background for grid but visible in list)
const holidayListEvents = computed(() => {
	return calendarStore.events
		.filter((e) => e.event_type === 'holiday')
		.map((e) => ({
			id: String(e.id),
			title: e.title,
			start: e.start,
			end: e.end,
			allDay: true,
			display: 'list-item' as const, // Only show in list views
			color: '#f472b6', // pink-400 for text/border in list view
			extendedProps: {
				event_type: e.event_type,
				description: e.description,
				employee_name: e.employee_name,
				created_by: e.created_by ?? null,
				is_repeating: e.is_repeating ?? false,
				repeat_frequency: e.repeat_frequency ?? undefined,
				parent_event: e.parent_event ?? null,
			},
		}))
})

// Combine regular events with holiday background events and holiday list events
const allCalendarEvents = computed(() => {
	return [...events.value, ...holidayBackgroundEvents.value, ...holidayListEvents.value]
})

const error = computed(() => calendarStore.error)

const buildUpdatePayload = (payload: CalendarEventPayload): Partial<CalendarEvent> => {
	const data: Partial<CalendarEvent> = {
		title: payload.title,
		event_type: payload.event_type,
		description: payload.description,
		start: payload.start,
		end: payload.end,
		all_day: payload.all_day,
	}

	if (payload.created_by) data.created_by = payload.created_by
	if (payload.assigned_to && payload.assigned_to.length > 0) data.assigned_to = payload.assigned_to
	if (payload.meeting_url) data.meeting_url = payload.meeting_url
	if (payload.project) data.project = payload.project
	if (payload.applied_by) data.applied_by = payload.applied_by
	if (payload.agent) data.agent = payload.agent
	if (payload.leave_type) data.leave_type = payload.leave_type

	return data
}

const updateEvent = async (id: string | number, payload: CalendarEventPayload) => {
	const convertedPayload = buildUpdatePayload(payload)
	await calendarStore.updateEvent(Number(id), convertedPayload)
}

const { handleEventDrop, handleEventResize } = useCalendarHandlers(updateEvent)

const handleViewChange = (info: unknown) => {
	const viewInfo = info as { view?: { type?: string } }
	if (viewInfo?.view?.type) {
		localStorage.setItem(STORAGE_KEY_CALENDAR_VIEW, viewInfo.view.type)
	}
}

const baseOptions = useCalendarOptions(allCalendarEvents, handleViewChange)

// Add theme plugin to options
const optionsWithTheme = computed(() => ({
	...baseOptions.value,
	plugins: [...(baseOptions.value.plugins || []), themeMap[selectedTheme.value]],
}))

const calendarOptions = computed(
	() =>
		({
			...optionsWithTheme.value,
			select: handleDateSelect,
			eventClick: handleEventClick,
			eventDrop: handleEventDrop,
			eventResize: handleEventResize,
		}) as CalendarOptions,
)

const syncEventsWithCalendar = () => {
	const api = calendarRef.value?.getApi()
	if (!api) return

	// Get current event sources and remove them
	const sources = api.getEventSources()
	sources.forEach((source) => {
		source.remove()
	})

	// Add new event source (includes both regular events and holiday backgrounds)
	api.addEventSource(allCalendarEvents.value)
}

const openCreateEvent = () => {
	selectedEvent.value = null
	selectInfo.value = {
		start: new Date(),
		end: new Date(),
		allDay: false,
	} as DateSelectData
	showForm.value = true
}

const handleDateSelect = (selection: DateSelectData) => {
	selectedEvent.value = null
	selectInfo.value = selection
	showForm.value = true
}

const handleEventClick = (info: EventClickData) => {
	selectedEvent.value = info.event
	selectInfo.value = null
	showForm.value = true
}

const closeForm = () => {
	showForm.value = false
	selectedEvent.value = null
	selectInfo.value = null
}

const handleSaveEvent = async (payload: CalendarEventPayload) => {
	isSubmitting.value = true
	try {
		// Auto-set created_by from logged-in user
		const currentUser = authStore.user
		let createdByEmployeeId: number | undefined

		if (currentUser?.worker_id) {
			// Find matching employee based on worker_id matching emp_id
			const matchingEmployee = employees.value.find(
				(emp) => emp.emp_id.toLowerCase() === currentUser.worker_id?.toLowerCase(),
			)
			if (matchingEmployee) {
				createdByEmployeeId = matchingEmployee.id
			}
		}

		if (selectedEvent.value) {
			// Update existing event - only send fields that have values
			const id = Number(selectedEvent.value.id)
			const normalizedAssignedTo =
				payload.assigned_to && payload.assigned_to.length > 0 ? payload.assigned_to : []
			const updatePayload: Partial<CalendarEvent> = {
				title: payload.title,
				event_type: payload.event_type,
				description: payload.description,
				start: payload.start,
				end: payload.end,
				all_day: payload.all_day ?? false,
				assigned_to: normalizedAssignedTo,
				meeting_url: payload.meeting_url || undefined,
				project: payload.project ?? null,
				applied_by: payload.applied_by ?? null,
				agent: payload.agent ?? null,
				leave_type: payload.leave_type ?? undefined,
			}

			if (createdByEmployeeId) updatePayload.created_by = createdByEmployeeId

			await calendarStore.updateEvent(id, updatePayload)
		} else {
			// Create new event
			const createPayload: Omit<CalendarEvent, 'id'> = {
				title: payload.title,
				event_type: payload.event_type,
				description: payload.description,
				start: payload.start,
				end: payload.end,
				all_day: payload.all_day ?? false,
				created_by: createdByEmployeeId,
				assigned_to: payload.assigned_to,
				meeting_url: payload.meeting_url,
				project: payload.project ?? undefined,
				applied_by: payload.applied_by ?? undefined,
				agent: payload.agent ?? undefined,
				leave_type: payload.leave_type ?? undefined,
			}
			await calendarStore.createEvent(createPayload)
		}
		closeForm()
		// The store watcher below will auto-sync the calendar
	} catch (err) {
		console.error('Failed to save event', err)
		showToast(t('calendar.saveFailed', 'Failed to save event'), 'error')
	} finally {
		isSubmitting.value = false
	}
}

const handleDeleteEvent = async (id: string | number) => {
	isSubmitting.value = true
	try {
		await calendarStore.deleteEvent(Number(id))
		closeForm()
		// The store watcher below will auto-sync the calendar
	} catch (err) {
		console.error('Failed to delete event', err)
		showToast(t('calendar.deleteFailed', 'Failed to delete event'), 'error')
	} finally {
		isSubmitting.value = false
	}
}
// Save theme to localStorage when it changes
watch(
	() => selectedTheme.value,
	(newTheme) => {
		localStorage.setItem(STORAGE_KEY_CALENDAR_THEME, newTheme)
		loadThemeCSS(newTheme)
		// Re-sync events after theme change to apply new plugin
		nextTick(() => {
			syncEventsWithCalendar()
		})
	},
)

// Watch for store events changes and sync with calendar UI
// No deep:true — the store replaces the array reference on each CRUD operation
watch(
	() => calendarStore.events,
	() => {
		nextTick(() => {
			syncEventsWithCalendar()
		})
	},
)
// Load initial data from API and sync calendar
onMounted(async () => {
	loadThemeCSS(selectedTheme.value)
	await Promise.all([
		calendarStore.fetchEvents(),
		employeeStore.fetchEmployees(),
		projectStore.fetchProjects(),
	])
	syncEventsWithCalendar()
})

onUnmounted(() => {
	// Clear calendar event sources to prevent stale references
	const api = calendarRef.value?.getApi()
	if (api) {
		api.getEventSources().forEach((s) => {
			s.remove()
		})
	}
})
</script>

<style scoped>
:deep(.fc) {
	--fc-border-color: var(--color-gray-200);
	--fc-page-bg-color: transparent;
	--fc-neutral-bg-color: var(--color-gray-50);
	--fc-list-event-hover-bg-color: var(--color-gray-100);
	--fc-today-bg-color: var(--color-brand-50);
	--fc-button-text-color: var(--color-gray-700);
}

:deep(.fc .fc-toolbar-title) {
	font-size: 1.125rem;
	font-weight: 700;
	color: var(--color-gray-900);
}

:deep(.fc .fc-button-primary) {
	background: var(--color-gray-100);
	border: 1px solid var(--color-gray-200);
	color: var(--color-gray-700);
	border-radius: 0.5rem;
	padding: 0.35rem 0.75rem;
}

:deep(.fc .fc-button-primary:hover) {
	background: var(--color-gray-200);
}

:deep(.fc .fc-daygrid-day-number),
:deep(.fc .fc-col-header-cell-cushion) {
	color: var(--color-gray-700);
}

:deep(.dark .fc .fc-toolbar-title) {
	color: var(--color-white);
}

:deep(.dark .fc .fc-button-primary) {
	background: var(--color-gray-800);
	border-color: var(--color-gray-700);
	color: var(--color-gray-100);
}

:deep(.dark .fc .fc-daygrid-day-number),
:deep(.dark .fc .fc-col-header-cell-cushion) {
	color: var(--color-gray-100);
}

:deep(.fc .fc-multimonth-title) {
	font-weight: 700;
	color: var(--color-gray-900);
}

:deep(.dark .fc .fc-multimonth-title) {
	color: var(--color-white);
}

:deep(.fc .week-number) {
	color: var(--color-gray-500);
	font-weight: 600;
}

:deep(.dark .fc .week-number) {
	color: var(--color-gray-300);
}

/* Calendar date hover effects - Month/Year views */
:deep(.fc .fc-daygrid-day) {
	cursor: pointer;
	transition: background-color 0.15s ease;
}

:deep(.fc .fc-daygrid-day:hover) {
	background-color: var(--color-gray-100);
}

:deep(.dark .fc .fc-daygrid-day:hover) {
	background-color: var(--color-gray-800);
}

/* Calendar date hover effects - Week view time grid */
:deep(.fc .fc-timegrid-slot) {
	cursor: pointer;
	transition: background-color 0.15s ease;
}

:deep(.fc .fc-timegrid-slot:hover) {
	background-color: var(--color-gray-100);
}

:deep(.dark .fc .fc-timegrid-slot:hover) {
	background-color: var(--color-gray-800);
}

/* Calendar date hover effects - Day view slots */
:deep(.fc .fc-timegrid-col) {
	cursor: pointer;
}

/* Calendar header date cells */
:deep(.fc .fc-col-header-cell) {
	cursor: pointer;
	transition: background-color 0.15s ease;
}

:deep(.fc .fc-col-header-cell:hover) {
	background-color: var(--color-gray-100);
}

:deep(.dark .fc .fc-col-header-cell:hover) {
	background-color: var(--color-gray-800);
}

/* Multi-month (Year view) date cells */
:deep(.fc .fc-multimonth-daygrid-table td) {
	cursor: pointer;
	transition: background-color 0.15s ease;
}

:deep(.fc .fc-multimonth-daygrid-table td:hover) {
	background-color: var(--color-gray-100);
}

:deep(.dark .fc .fc-multimonth-daygrid-table td:hover) {
	background-color: var(--color-gray-800);
}

/* Date number links */
:deep(.fc .fc-daygrid-day-number) {
	cursor: pointer;
	padding: 4px 8px;
	border-radius: 4px;
	transition: background-color 0.15s ease;
}

:deep(.fc .fc-daygrid-day-number:hover) {
	background-color: var(--color-brand-100);
}

:deep(.dark .fc .fc-daygrid-day-number:hover) {
	background-color: var(--color-brand-900);
}
</style>
