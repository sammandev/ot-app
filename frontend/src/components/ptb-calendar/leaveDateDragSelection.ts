interface FlatpickrInstance {
	calendarContainer?: HTMLElement
	setDate: (dates: string[], triggerChange: boolean) => void
	redraw: () => void
}

interface FlatpickrDayElement extends HTMLElement {
	dateObj?: Date
	dataset: DOMStringMap & {
		leaveDragPreview?: string
	}
}

interface LeaveDateDragSelectionOptions {
	getSelectedDates: () => string[]
	setSelectedDates: (dates: string[]) => void
}

const DAY_SELECTOR = '.flatpickr-day'
const PREVIEW_BACKGROUND = 'rgba(16, 185, 129, 0.18)'
const PREVIEW_SHADOW = 'inset 0 0 0 2px rgba(16, 185, 129, 0.55)'

const padTwoDigits = (value: number): string => (value < 10 ? `0${value}` : String(value))

const formatDateStr = (date: Date): string => {
	const year = date.getFullYear()
	const month = padTwoDigits(date.getMonth() + 1)
	const day = padTwoDigits(date.getDate())
	return `${year}-${month}-${day}`
}

const sortUniqueDateStrings = (dates: string[]) => {
	const uniqueDates: string[] = []
	for (let index = 0; index < dates.length; index += 1) {
		const dateValue = dates[index]
		if (!dateValue || uniqueDates.indexOf(dateValue) !== -1) continue
		uniqueDates.push(dateValue)
	}

	return uniqueDates.sort((left, right) => new Date(left).getTime() - new Date(right).getTime())
}

const getRangeDates = (startDate: string, endDate: string): string[] => {
	const start = new Date(startDate)
	const end = new Date(endDate)
	const minDate = start <= end ? start : end
	const maxDate = start <= end ? end : start
	const dates: string[] = []
	const current = new Date(minDate.getTime())

	while (current <= maxDate) {
		dates.push(formatDateStr(current))
		current.setDate(current.getDate() + 1)
	}

	return dates
}

const findDayElement = (target: EventTarget | null): FlatpickrDayElement | null => {
	if (!(target instanceof HTMLElement)) return null
	const dayElement = target.closest(DAY_SELECTOR)
	if (!(dayElement instanceof HTMLElement)) return null
	return dayElement as FlatpickrDayElement
}

const isSelectableDay = (dayElement: FlatpickrDayElement | null): dayElement is FlatpickrDayElement => {
	if (!dayElement?.dateObj) return false
	return !dayElement.classList.contains('flatpickr-disabled') && !dayElement.classList.contains('disabled')
}

const clearPreview = (container: HTMLElement) => {
	const dayElements = container.querySelectorAll<FlatpickrDayElement>(DAY_SELECTOR)
	for (let index = 0; index < dayElements.length; index += 1) {
		const dayElement = dayElements[index]
		if (!dayElement) continue
		if (dayElement.dataset.leaveDragPreview !== 'true') continue
		dayElement.dataset.leaveDragPreview = 'false'
		dayElement.style.removeProperty('background-color')
		dayElement.style.removeProperty('box-shadow')
	}
}

const paintPreview = (container: HTMLElement, startDate: string, endDate: string) => {
	clearPreview(container)
	const rangeDates = getRangeDates(startDate, endDate)
	const rangeDateLookup: Record<string, boolean> = {}
	for (let index = 0; index < rangeDates.length; index += 1) {
		const rangeDate = rangeDates[index]
		if (!rangeDate) continue
		rangeDateLookup[rangeDate] = true
	}

	const dayElements = container.querySelectorAll<FlatpickrDayElement>(DAY_SELECTOR)
	for (let index = 0; index < dayElements.length; index += 1) {
		const dayElement = dayElements[index]
		if (!dayElement) continue
		if (!isSelectableDay(dayElement)) continue
		const dateObj = dayElement.dateObj
		if (!dateObj) continue
		if (!rangeDateLookup[formatDateStr(dateObj)]) continue
		dayElement.dataset.leaveDragPreview = 'true'
		dayElement.style.backgroundColor = PREVIEW_BACKGROUND
		dayElement.style.boxShadow = PREVIEW_SHADOW
	}
}

export const attachLeaveDateDragSelection = (
	instance: FlatpickrInstance,
	options: LeaveDateDragSelectionOptions,
) => {
	const container = instance.calendarContainer
	if (!container) return () => undefined

	let dragStart: string | null = null
	let dragEnd: string | null = null
	let isDragging = false
	let suppressNextClick = false

	const resetDragState = () => {
		isDragging = false
		dragStart = null
		dragEnd = null
		clearPreview(container)
	}

	const finalizeDrag = () => {
		if (!isDragging || !dragStart || !dragEnd) {
			resetDragState()
			return
		}

		const rangeDates = getRangeDates(dragStart, dragEnd)
		const shouldMergeRange = rangeDates.length > 1
		resetDragState()

		if (!shouldMergeRange) return

		const mergedDates = sortUniqueDateStrings([...options.getSelectedDates(), ...rangeDates])
		options.setSelectedDates(mergedDates)
		instance.setDate(mergedDates, false)
		instance.redraw()

		suppressNextClick = true
		window.setTimeout(() => {
			suppressNextClick = false
		}, 0)
	}

	const handleMouseDown = (event: MouseEvent) => {
		if (event.button !== 0) return
		const dayElement = findDayElement(event.target)
		if (!isSelectableDay(dayElement)) return
		const dateObj = dayElement.dateObj
		if (!dateObj) return

		dragStart = formatDateStr(dateObj)
		dragEnd = dragStart
		isDragging = true
		paintPreview(container, dragStart, dragEnd)
		event.preventDefault()
	}

	const handleMouseOver = (event: MouseEvent) => {
		if (!isDragging || !dragStart) return
		const dayElement = findDayElement(event.target)
		if (!isSelectableDay(dayElement)) return
		const dateObj = dayElement.dateObj
		if (!dateObj) return

		dragEnd = formatDateStr(dateObj)
		paintPreview(container, dragStart, dragEnd)
	}

	const handleClickCapture = (event: MouseEvent) => {
		if (!suppressNextClick) return
		const dayElement = findDayElement(event.target)
		if (!dayElement) return
		event.preventDefault()
		event.stopPropagation()
		suppressNextClick = false
	}

	const handleDragStart = (event: DragEvent) => {
		if (!findDayElement(event.target)) return
		event.preventDefault()
	}

	container.addEventListener('mousedown', handleMouseDown)
	container.addEventListener('mouseover', handleMouseOver)
	container.addEventListener('click', handleClickCapture, true)
	container.addEventListener('dragstart', handleDragStart)
	document.addEventListener('mouseup', finalizeDrag)

	return () => {
		container.removeEventListener('mousedown', handleMouseDown)
		container.removeEventListener('mouseover', handleMouseOver)
		container.removeEventListener('click', handleClickCapture, true)
		container.removeEventListener('dragstart', handleDragStart)
		document.removeEventListener('mouseup', finalizeDrag)
		clearPreview(container)
	}
}