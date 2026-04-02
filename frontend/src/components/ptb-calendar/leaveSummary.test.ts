import { describe, expect, it } from 'vitest'

import type { EmployeeLeave } from '@/services/api/holiday'
import { formatLeaveSummaryDates, summarizeLeavesByEmployee } from '@/components/ptb-calendar/leaveSummary'

const weekdayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const makeLeave = (overrides: Partial<EmployeeLeave>): EmployeeLeave => ({
	id: overrides.id ?? 1,
	employee: overrides.employee ?? 1,
	employee_name: overrides.employee_name ?? 'Employee',
	employee_emp_id: overrides.employee_emp_id ?? 'EMP001',
	employee_dept_code: overrides.employee_dept_code ?? 'OPS',
	date: overrides.date ?? '2026-04-09',
	agents: overrides.agents ?? [],
	batch_key: overrides.batch_key ?? 'batch-1',
	notes: overrides.notes ?? '',
	created_by: overrides.created_by ?? 1,
	created_by_username: overrides.created_by_username ?? 'owner',
	created_at: overrides.created_at ?? '2026-04-01T00:00:00Z',
	updated_at: overrides.updated_at ?? '2026-04-01T00:00:00Z',
	agent_ids: overrides.agent_ids ?? [],
	agent_details: overrides.agent_details ?? [],
})

describe('leaveSummary', () => {
	it('formats date-only summaries without timezone drift', () => {
		expect(formatLeaveSummaryDates(['2026-04-09'], weekdayLabels, 1)).toBe('Thu-9')
	})

	it('sorts grouped employee summaries by local date-only strings', () => {
		const summaries = summarizeLeavesByEmployee(
			[
				makeLeave({ id: 2, date: '2026-04-10' }),
				makeLeave({ id: 1, date: '2026-04-09' }),
			],
			'-',
		)

		expect(summaries).toHaveLength(1)
		expect(summaries[0]?.dates).toEqual(['2026-04-09', '2026-04-10'])
	})
})
