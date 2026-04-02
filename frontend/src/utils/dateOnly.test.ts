import { describe, expect, it } from 'vitest'

import { compareDateOnlyStrings, formatDateOnlyLocal, parseDateOnly } from '@/utils/dateOnly'

describe('dateOnly utilities', () => {
	it('parses YYYY-MM-DD as a local calendar date', () => {
		const parsed = parseDateOnly('2026-04-09')

		expect(parsed.getFullYear()).toBe(2026)
		expect(parsed.getMonth()).toBe(3)
		expect(parsed.getDate()).toBe(9)
	})

	it('compares date-only strings lexicographically', () => {
		expect(compareDateOnlyStrings('2026-04-09', '2026-04-10')).toBeLessThan(0)
		expect(compareDateOnlyStrings('2026-04-10', '2026-04-09')).toBeGreaterThan(0)
		expect(compareDateOnlyStrings('2026-04-09', '2026-04-09')).toBe(0)
	})

	it('formats local dates back to YYYY-MM-DD', () => {
		expect(formatDateOnlyLocal(new Date(2026, 3, 9))).toBe('2026-04-09')
	})
})
