import type { EmployeeLeave, LeaveAgent } from '@/services/api/holiday'
import { compareDateOnlyStrings, parseDateOnly } from '@/utils/dateOnly'

export const LEAVE_AGENT_FALLBACK = '-'

const normalizeText = (value?: string | null): string => value?.trim().replace(/\s+/g, ' ') ?? ''

const getAgentKey = (agent: LeaveAgent): string => {
	if (agent.type === 'employee') {
		return `employee:${agent.employee_id}`
	}
	if (agent.type === 'external') {
		return `external:${normalizeText(agent.worker_id).toLowerCase()}|${normalizeText(agent.email).toLowerCase()}`
	}
	return `manual:${normalizeText(agent.name).toLowerCase()}`
}

const getAgentLabel = (agent: LeaveAgent): string => {
	if (agent.type === 'employee') return normalizeText(agent.name)
	if (agent.type === 'external') {
		return normalizeText(agent.username) || normalizeText(agent.email) || normalizeText(agent.worker_id)
	}
	return normalizeText(agent.name)
}

const getSortedAgentKeys = (leave: EmployeeLeave): string[] => (leave.agents ?? []).map(getAgentKey).sort()

const getLeaveCreatedAtMs = (leave: EmployeeLeave): number | null => {
	if (!leave.created_at) return null
	const timestamp = new Date(leave.created_at).getTime()
	return Number.isFinite(timestamp) ? timestamp : null
}

export const areLeavesInSameBatch = (reference: EmployeeLeave, candidate: EmployeeLeave): boolean => {
	const referenceBatchKey = normalizeText(reference.batch_key)
	const candidateBatchKey = normalizeText(candidate.batch_key)
	if (referenceBatchKey || candidateBatchKey) {
		return referenceBatchKey !== '' && referenceBatchKey === candidateBatchKey
	}

	if (reference.employee !== candidate.employee) return false
	if (normalizeText(reference.notes) !== normalizeText(candidate.notes)) return false
	if (reference.created_by !== candidate.created_by) return false

	const referenceAgentKeys = getSortedAgentKeys(reference)
	const candidateAgentKeys = getSortedAgentKeys(candidate)
	if (referenceAgentKeys.join(',') !== candidateAgentKeys.join(',')) return false

	const referenceCreatedAt = getLeaveCreatedAtMs(reference)
	const candidateCreatedAt = getLeaveCreatedAtMs(candidate)
	if (referenceCreatedAt !== null && candidateCreatedAt !== null) {
		return Math.abs(referenceCreatedAt - candidateCreatedAt) <= 30_000
	}

	return reference.id === candidate.id
}

export const getLeaveBatch = (leaves: EmployeeLeave[], reference: EmployeeLeave | null | undefined): EmployeeLeave[] => {
	if (!reference) return []

	const relatedLeaves = leaves
		.filter((leave) => areLeavesInSameBatch(reference, leave))
		.sort((left, right) => compareDateOnlyStrings(left.date, right.date))

	return relatedLeaves.length > 0 ? relatedLeaves : [reference]
}

export interface LeaveEmployeeSummary {
	employeeId: number
	employeeName: string
	employeeEmpId: string
	leaveDays: number
	dates: string[]
	representativeLeave: EmployeeLeave
	agentDisplay: string
}

const getAgentParts = (leave: EmployeeLeave): string[] => {
	return (leave.agents ?? []).map(getAgentLabel).filter((value) => value !== '')
}

export const getLeaveAgentDisplay = (leave: EmployeeLeave, noneLabel: string): string => {
	const uniqueParts = Array.from(new Set(getAgentParts(leave)))
	return uniqueParts.length > 0 ? uniqueParts.join(', ') : noneLabel
}

export const formatLeaveSummaryDates = (
	dates: string[],
	weekdayLabels: string[],
	maxVisible = 4,
): string => {
	const preview = dates
		.slice(0, maxVisible)
		.map((dateStr) => {
			const date = parseDateOnly(dateStr)
			return `${weekdayLabels[date.getDay()] ?? ''}-${date.getDate()}`
		})

	if (dates.length > maxVisible) {
		preview.push(`+${dates.length - maxVisible}`)
	}

	return preview.join(', ')
}

export const getUniqueLeaveEmployeeCountByDate = (leaves: EmployeeLeave[], date: string): number =>
	new Set(leaves.filter((leave) => leave.date === date).map((leave) => leave.employee)).size

export const summarizeLeavesByEmployee = (
	leaves: EmployeeLeave[],
	noneLabel: string,
): LeaveEmployeeSummary[] => {
	const summaries = new Map<number, LeaveEmployeeSummary & { agentParts: Set<string> }>()

	for (const leave of [...leaves].sort((a, b) => compareDateOnlyStrings(a.date, b.date))) {
		const existing = summaries.get(leave.employee)
		if (!existing) {
			summaries.set(leave.employee, {
				employeeId: leave.employee,
				employeeName: leave.employee_name,
				employeeEmpId: leave.employee_emp_id,
				leaveDays: 1,
				dates: [leave.date],
				representativeLeave: leave,
				agentDisplay: '',
				agentParts: new Set(getAgentParts(leave)),
			})
			continue
		}

		existing.leaveDays += 1
		if (!existing.dates.includes(leave.date)) {
			existing.dates.push(leave.date)
		}
		for (const part of getAgentParts(leave)) {
			existing.agentParts.add(part)
		}
	}

	return [...summaries.values()]
		.map(({ agentParts, ...summary }) => ({
			...summary,
			dates: [...summary.dates].sort(compareDateOnlyStrings),
			agentDisplay: agentParts.size > 0 ? [...agentParts].join(', ') : noneLabel,
		}))
		.sort((a, b) => {
			const firstDateDiff = compareDateOnlyStrings(
				a.dates[0] ?? a.representativeLeave.date,
				b.dates[0] ?? b.representativeLeave.date,
			)
			if (firstDateDiff !== 0) {
				return firstDateDiff
			}
			return a.employeeName.localeCompare(b.employeeName)
		})
}
