import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import multiMonthPlugin from '@fullcalendar/multimonth'
import timeGridPlugin from '@fullcalendar/timegrid'
import type { Ref } from 'vue'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { CalendarEventInput } from '@/types/calendar'

export const useCalendarOptions = (
	events: Ref<CalendarEventInput[]>,
	handleViewChange: (info: unknown) => void,
) => {
	const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)

	const updateWidth = () => {
		viewportWidth.value = window.innerWidth
	}

	onMounted(() => {
		window.addEventListener('resize', updateWidth)
	})

	onBeforeUnmount(() => {
		window.removeEventListener('resize', updateWidth)
	})

	const isMobile = computed(() => viewportWidth.value < 768)

	const baseOptions = computed(() => ({
		plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, multiMonthPlugin, listPlugin],
		initialView: localStorage.getItem('calendarView') || 'multiMonthYear',
		editable: true,
		selectable: true,
		eventStartEditable: true,
		eventResizableFromStart: true,
		eventDurationEditable: true,
		droppable: true,
		selectMirror: true,
		unselectAuto: true,
		events: events.value,
		eventDisplay: 'block',
		contentHeight: 'auto',
		handleWindowResize: true,
		views: {
			multiMonthYear: {
				fixedWeekCount: true,
				showNonCurrentDates: true,
			},
			dayGridMonth: {
				fixedWeekCount: false,
			},
		},
		firstDay: 1,
		weekNumbers: true,
		weekText: 'Week',
		weekNumberContent: (arg: { num: number }) => 'W' + arg.num,
		weekNumberClassNames: 'week-number',
		displayEventEnd: true,
		showNonCurrentDates: true,
		datesSet: handleViewChange,
	}))

	const options = computed(() => ({
		...baseOptions.value,
		headerToolbar: {
			left: isMobile.value
				? 'timeGridDay,timeGridWeek,dayGridMonth,listMonth'
				: 'timeGridDay,timeGridWeek,dayGridMonth,multiMonthYear,listMonth',
			center: 'title',
			right: 'today prev,next',
		},
		buttonText: {
			timeGridDay: 'Day',
			timeGridWeek: 'Week',
			dayGridMonth: 'Month',
			multiMonthYear: 'Year',
			listMonth: 'List',
		},
	}))

	return options
}
