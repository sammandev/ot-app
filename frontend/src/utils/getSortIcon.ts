import type { Ref } from 'vue'

/**
 * Returns a sort direction indicator string for a column header.
 *
 * - `' ↕'` — column is not the current sort field (neutral)
 * - `' ↑'` — ascending
 * - `' ↓'` — descending
 *
 * @example
 * ```ts
 * // Option A — pass refs directly (most common)
 * const sortBy = ref<'name' | 'date'>('name')
 * const sortOrder = ref<'asc' | 'desc'>('asc')
 * const icon = getSortIcon('name', sortBy, sortOrder) // ' ↑'
 *
 * // Option B — pass plain values (useful when caller already unwrapped)
 * const icon = getSortIcon('name', 'name', 'asc') // ' ↑'
 * ```
 */
export function getSortIcon(
	field: string,
	currentSortBy: Ref<string | null> | string | null,
	currentSortOrder: Ref<string> | string,
): string {
	const sortByVal =
		currentSortBy === null || typeof currentSortBy === 'string' ? currentSortBy : currentSortBy.value
	const sortOrderVal =
		typeof currentSortOrder === 'string' ? currentSortOrder : currentSortOrder.value

	if (sortByVal !== field) return ' ↕'
	return sortOrderVal === 'asc' ? ' ↑' : ' ↓'
}
