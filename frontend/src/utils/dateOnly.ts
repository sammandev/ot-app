export const DATE_ONLY_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/

export const parseDateOnly = (value: string): Date => {
	const match = DATE_ONLY_PATTERN.exec(value)
	if (!match) {
		return new Date(value)
	}

	const [, year, month, day] = match
	return new Date(Number(year), Number(month) - 1, Number(day))
}

export const compareDateOnlyStrings = (left: string, right: string): number => {
	if (left === right) return 0
	return left < right ? -1 : 1
}

export const formatDateOnlyLocal = (value: Date): string => {
	const year = value.getFullYear()
	const month = String(value.getMonth() + 1).padStart(2, '0')
	const day = String(value.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}
