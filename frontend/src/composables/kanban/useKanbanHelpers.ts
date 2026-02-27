import type { CalendarEvent } from '@/services/api/calendar'

// ── Types ───────────────────────────────────────────────────────────────
export type PriorityLevel = 'low' | 'medium' | 'high' | 'urgent'
export type TaskStatus = 'todo' | 'in_progress' | 'done'

// ── Constants ───────────────────────────────────────────────────────────
export const columns: { id: TaskStatus; title: string; color: string }[] = [
	{ id: 'todo', title: 'To Do', color: 'bg-gray-400' },
	{ id: 'in_progress', title: 'In Progress', color: 'bg-blue-500' },
	{ id: 'done', title: 'Done', color: 'bg-green-500' },
]

export const colorTemplates = [
	{
		name: 'Indigo',
		color: '#6366F1',
		bg: 'bg-indigo-100 dark:bg-indigo-900/40',
		text: 'text-indigo-700 dark:text-indigo-300',
	},
	{
		name: 'Blue',
		color: '#3B82F6',
		bg: 'bg-blue-100 dark:bg-blue-900/40',
		text: 'text-blue-700 dark:text-blue-300',
	},
	{
		name: 'Cyan',
		color: '#06B6D4',
		bg: 'bg-cyan-100 dark:bg-cyan-900/40',
		text: 'text-cyan-700 dark:text-cyan-300',
	},
	{
		name: 'Teal',
		color: '#14B8A6',
		bg: 'bg-teal-100 dark:bg-teal-900/40',
		text: 'text-teal-700 dark:text-teal-300',
	},
	{
		name: 'Emerald',
		color: '#10B981',
		bg: 'bg-emerald-100 dark:bg-emerald-900/40',
		text: 'text-emerald-700 dark:text-emerald-300',
	},
	{
		name: 'Green',
		color: '#22C55E',
		bg: 'bg-green-100 dark:bg-green-900/40',
		text: 'text-green-700 dark:text-green-300',
	},
	{
		name: 'Lime',
		color: '#84CC16',
		bg: 'bg-lime-100 dark:bg-lime-900/40',
		text: 'text-lime-700 dark:text-lime-300',
	},
	{
		name: 'Yellow',
		color: '#EAB308',
		bg: 'bg-yellow-100 dark:bg-yellow-900/40',
		text: 'text-yellow-700 dark:text-yellow-300',
	},
	{
		name: 'Amber',
		color: '#F59E0B',
		bg: 'bg-amber-100 dark:bg-amber-900/40',
		text: 'text-amber-700 dark:text-amber-300',
	},
	{
		name: 'Orange',
		color: '#F97316',
		bg: 'bg-orange-100 dark:bg-orange-900/40',
		text: 'text-orange-700 dark:text-orange-300',
	},
	{
		name: 'Red',
		color: '#EF4444',
		bg: 'bg-red-100 dark:bg-red-900/40',
		text: 'text-red-700 dark:text-red-300',
	},
	{
		name: 'Rose',
		color: '#F43F5E',
		bg: 'bg-rose-100 dark:bg-rose-900/40',
		text: 'text-rose-700 dark:text-rose-300',
	},
	{
		name: 'Pink',
		color: '#EC4899',
		bg: 'bg-pink-100 dark:bg-pink-900/40',
		text: 'text-pink-700 dark:text-pink-300',
	},
	{
		name: 'Fuchsia',
		color: '#D946EF',
		bg: 'bg-fuchsia-100 dark:bg-fuchsia-900/40',
		text: 'text-fuchsia-700 dark:text-fuchsia-300',
	},
	{
		name: 'Purple',
		color: '#A855F7',
		bg: 'bg-purple-100 dark:bg-purple-900/40',
		text: 'text-purple-700 dark:text-purple-300',
	},
	{
		name: 'Violet',
		color: '#8B5CF6',
		bg: 'bg-violet-100 dark:bg-violet-900/40',
		text: 'text-violet-700 dark:text-violet-300',
	},
	{
		name: 'Slate',
		color: '#64748B',
		bg: 'bg-slate-100 dark:bg-slate-900/40',
		text: 'text-slate-700 dark:text-slate-300',
	},
	{
		name: 'Gray',
		color: '#6B7280',
		bg: 'bg-gray-100 dark:bg-gray-700/40',
		text: 'text-gray-700 dark:text-gray-300',
	},
]

export const availableLabels = [
	{
		name: 'Red',
		color:
			'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800',
		activeClass: 'bg-red-500 text-white border-red-500',
	},
	{
		name: 'Green',
		color:
			'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800',
		activeClass: 'bg-green-500 text-white border-green-500',
	},
	{
		name: 'Blue',
		color:
			'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800',
		activeClass: 'bg-blue-500 text-white border-blue-500',
	},
	{
		name: 'Purple',
		color:
			'bg-purple-100 text-purple-700 border-purple-200 dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-800',
		activeClass: 'bg-purple-500 text-white border-purple-500',
	},
	{
		name: 'Orange',
		color:
			'bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/30 dark:text-orange-300 dark:border-orange-800',
		activeClass: 'bg-orange-500 text-white border-orange-500',
	},
	{
		name: 'Cyan',
		color:
			'bg-cyan-100 text-cyan-700 border-cyan-200 dark:bg-cyan-900/30 dark:text-cyan-300 dark:border-cyan-800',
		activeClass: 'bg-cyan-500 text-white border-cyan-500',
	},
	{
		name: 'Yellow',
		color:
			'bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300 dark:border-yellow-800',
		activeClass: 'bg-yellow-500 text-white border-yellow-500',
	},
	{
		name: 'Pink',
		color:
			'bg-pink-100 text-pink-700 border-pink-200 dark:bg-pink-900/30 dark:text-pink-300 dark:border-pink-800',
		activeClass: 'bg-pink-500 text-white border-pink-500',
	},
]

export const priorityConfig: Record<PriorityLevel, { label: string; color: string; icon: string }> =
	{
		low: {
			label: 'Low',
			color: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
			icon: '',
		},
		medium: {
			label: 'Medium',
			color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-300',
			icon: '',
		},
		high: {
			label: 'High',
			color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-300',
			icon: '↑',
		},
		urgent: {
			label: 'Urgent',
			color: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-300',
			icon: '⚡',
		},
	}

// ── Utility Functions ───────────────────────────────────────────────────

export function getInitials(name: string | undefined | null): string {
	if (!name) return '??'
	return name
		.split(' ')
		.map((n) => n[0])
		.join('')
		.substring(0, 2)
		.toUpperCase()
}

export function formatDate(dateStr: string | undefined | null): string {
	if (!dateStr) return ''
	return new Date(dateStr).toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
	})
}

export function formatTime(dateStr: string | undefined | null): string {
	if (!dateStr) return ''
	return new Date(dateStr).toLocaleTimeString('en-US', {
		hour: '2-digit',
		minute: '2-digit',
		hour12: false,
	})
}

export function getDueDateClass(dateStr: string): string {
	const dueDate = new Date(dateStr)
	const now = new Date()
	const hoursUntilDue = (dueDate.getTime() - now.getTime()) / (1000 * 60 * 60)

	if (hoursUntilDue < 0) {
		return 'text-red-600 dark:text-red-400 font-semibold'
	} else if (hoursUntilDue <= 8) {
		return 'text-orange-600 dark:text-orange-400 font-semibold'
	} else if (hoursUntilDue <= 24) {
		return 'text-yellow-600 dark:text-yellow-400'
	}
	return 'text-gray-400'
}

export function isOverdue(dateStr: string): boolean {
	return new Date(dateStr) < new Date()
}

export function isDueSoon(dateStr: string): boolean {
	const dueDate = new Date(dateStr)
	const now = new Date()
	const hoursUntilDue = (dueDate.getTime() - now.getTime()) / (1000 * 60 * 60)
	return hoursUntilDue > 0 && hoursUntilDue <= 8
}

export function getLabelColor(labelName: string): string {
	const label = availableLabels.find((l) => l.name === labelName)
	return (
		label?.color ||
		'bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600'
	)
}

export function getPriorityConfig(
	priority: string | undefined | null,
): { label: string; color: string; icon: string } | null {
	if (!priority || !(priority in priorityConfig)) return null
	return priorityConfig[priority as PriorityLevel]
}

export function formatHours(hours: number | null | undefined): string {
	if (hours === null || hours === undefined) return '0'
	const num = Number(hours)
	return num % 1 === 0 ? num.toString() : num.toFixed(1)
}

export function getTimeTrackingClass(task: CalendarEvent): string {
	if (!task.estimated_hours || !task.actual_hours) {
		return 'text-gray-500 dark:text-gray-400'
	}
	const actual = Number(task.actual_hours)
	const estimated = Number(task.estimated_hours)
	if (actual > estimated) {
		return 'text-red-600 dark:text-red-400'
	} else if (actual >= estimated * 0.8) {
		return 'text-amber-600 dark:text-amber-400'
	}
	return 'text-green-600 dark:text-green-400'
}

export function getTimeTrackingTooltip(task: CalendarEvent): string {
	const parts: string[] = []
	if (task.estimated_hours) {
		parts.push(`Estimated: ${formatHours(task.estimated_hours)}h`)
	}
	if (task.actual_hours) {
		parts.push(`Logged: ${formatHours(task.actual_hours)}h`)
	}
	if (task.estimated_hours && task.actual_hours) {
		const remaining = Number(task.estimated_hours) - Number(task.actual_hours)
		if (remaining > 0) {
			parts.push(`Remaining: ${formatHours(remaining)}h`)
		} else if (remaining < 0) {
			parts.push(`Over by: ${formatHours(Math.abs(remaining))}h`)
		}
	}
	return parts.join(' | ')
}
