import { onUnmounted, ref } from 'vue'

/**
 * Flatpickr instance interface — superset of fields used across all components.
 * Compatible with flatpickr's native `Instance` type.
 */
export interface FlatpickrInstance {
	destroy?: () => void
	calendarContainer?: HTMLElement
	timeContainer?: HTMLElement
	selectedDates?: Date[]
	_input?: HTMLInputElement
	config?: { minuteIncrement?: number }
	changeMonth?: (delta: number) => void
	setDate?: (date: Date, triggerChange: boolean) => void
	redraw?: () => void
	currentMonth?: number
	currentYear?: number
}

interface RegisteredHandler {
	element: HTMLElement
	event: string
	handler: EventListener
}

/**
 * Composable providing mouse-wheel scroll helpers for flatpickr:
 *
 * - `attachMonthScroll(instance)` — scroll wheel on calendar to change month
 * - `attachTimeScroll(instance)` — scroll wheel on hour/minute inputs to adjust time
 * - `destroyFlatpickrs()` — tear down all tracked instances and remove listeners
 *
 * Automatically cleans up on `onUnmounted`.
 *
 * @example
 * ```ts
 * const { flatpickrInstances, attachMonthScroll, destroyFlatpickrs } = useFlatpickrScroll()
 *
 * const datePickerOptions = {
 *   onReady: (_dates, _str, instance) => {
 *     flatpickrInstances.value.push(instance)
 *     attachMonthScroll(instance)
 *   },
 * }
 * ```
 */
export function useFlatpickrScroll() {
	const flatpickrInstances = ref<FlatpickrInstance[]>([])
	const registeredHandlers = ref<RegisteredHandler[]>([])

	/**
	 * Attach a wheel listener on the calendar container to change month on scroll.
	 * Ignores the event when Ctrl is held (allows browser zoom).
	 */
	const attachMonthScroll = (instance: FlatpickrInstance) => {
		const container = instance?.calendarContainer
		if (!container) return

		const onWheel = (e: WheelEvent) => {
			if (e.ctrlKey) return
			e.preventDefault()
			if (e.deltaY < 0) instance.changeMonth?.(-1)
			else if (e.deltaY > 0) instance.changeMonth?.(1)
		}

		container.addEventListener('wheel', onWheel as EventListener, { passive: false })
		registeredHandlers.value.push({
			element: container,
			event: 'wheel',
			handler: onWheel as EventListener,
		})
	}

	/**
	 * Adjust a time-picker flatpickr's value by ±1 unit (hour or minute).
	 */
	const adjustFlatpickrTime = (
		instance: FlatpickrInstance,
		direction: 1 | -1,
		unit: 'hour' | 'minute',
	) => {
		const inputVal = instance?._input?.value || '00:00'
		const [hStr, mStr] = inputVal.split(':')
		const hours = Number.parseInt(hStr || '0', 10) || 0
		const minutes = Number.parseInt(mStr || '0', 10) || 0
		const minuteStep = instance?.config?.minuteIncrement || 1
		const step = unit === 'hour' ? 60 : minuteStep
		const total = hours * 60 + minutes + direction * step
		const clamped = ((total % 1440) + 1440) % 1440
		const nextHours = Math.floor(clamped / 60)
		const nextMinutes = clamped % 60
		const base = instance.selectedDates?.[0] ? new Date(instance.selectedDates[0]) : new Date()
		base.setHours(nextHours, nextMinutes, 0, 0)
		instance.setDate?.(base, true)
	}

	/**
	 * Attach wheel listeners on the hour and minute inputs inside a time-picker flatpickr.
	 */
	const attachTimeScroll = (instance: FlatpickrInstance) => {
		const hourInput = instance?.timeContainer?.querySelector(
			'.flatpickr-hour',
		) as HTMLInputElement | null
		const minuteInput = instance?.timeContainer?.querySelector(
			'.flatpickr-minute',
		) as HTMLInputElement | null

		const registerWheel = (el: HTMLElement | null, unit: 'hour' | 'minute') => {
			if (!el) return
			const onWheel = (e: WheelEvent) => {
				e.preventDefault()
				adjustFlatpickrTime(instance, e.deltaY < 0 ? -1 : 1, unit)
			}
			el.addEventListener('wheel', onWheel as EventListener, { passive: false })
			registeredHandlers.value.push({
				element: el,
				event: 'wheel',
				handler: onWheel as EventListener,
			})
		}

		registerWheel(hourInput, 'hour')
		registerWheel(minuteInput, 'minute')
	}

	/**
	 * Remove all registered wheel listeners and destroy all tracked flatpickr instances.
	 */
	const destroyFlatpickrs = () => {
		for (const { element, event, handler } of registeredHandlers.value) {
			element.removeEventListener(event, handler)
		}
		registeredHandlers.value = []

		for (const instance of flatpickrInstances.value) {
			if (typeof instance?.destroy === 'function') {
				instance.destroy()
			}
		}
		flatpickrInstances.value = []
	}

	onUnmounted(destroyFlatpickrs)

	return {
		flatpickrInstances,
		registeredHandlers,
		attachMonthScroll,
		attachTimeScroll,
		adjustFlatpickrTime,
		destroyFlatpickrs,
	}
}

/**
 * Standalone `attachMonthScroll` — for components that manage their own flatpickr
 * lifecycle (e.g. native `flatpickr()` calls) and only need the wheel-to-change-month
 * behavior without the full composable's instance tracking.
 *
 * **Does not register cleanup.** The caller is responsible for destroying the
 * flatpickr instance (which removes the container and its listeners).
 */
export function attachMonthScrollStandalone(instance: {
	calendarContainer?: HTMLElement
	changeMonth?: (delta: number) => void
}) {
	const container = instance?.calendarContainer
	if (!container) return
	const onWheel = (e: WheelEvent) => {
		if (e.ctrlKey) return
		e.preventDefault()
		if (e.deltaY < 0) instance.changeMonth?.(-1)
		else if (e.deltaY > 0) instance.changeMonth?.(1)
	}
	container.addEventListener('wheel', onWheel as EventListener, { passive: false })
}
