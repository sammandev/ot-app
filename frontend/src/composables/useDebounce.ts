/**
 * Debounce Composable
 * Provides debounced reactive values and functions
 */

import { type Ref, ref, watch } from 'vue'

/**
 * Debounce a ref value
 * @param value - The reactive value to debounce
 * @param delay - Delay in milliseconds (default: 300ms)
 * @returns Debounced ref
 */
export function useDebounce<T>(value: Ref<T>, delay: number = 300): Ref<T> {
	const debouncedValue = ref<T>(value.value) as Ref<T>
	let timeout: ReturnType<typeof setTimeout> | null = null

	watch(
		value,
		(newValue) => {
			if (timeout) {
				clearTimeout(timeout)
			}

			timeout = setTimeout(() => {
				debouncedValue.value = newValue
			}, delay)
		},
		{ immediate: false },
	)

	return debouncedValue
}

/**
 * Debounce a function
 * @param fn - The function to debounce
 * @param delay - Delay in milliseconds (default: 300ms)
 * @returns Debounced function
 */
export function useDebounceFn<T extends (...args: unknown[]) => unknown>(
	fn: T,
	delay: number = 300,
): (...args: Parameters<T>) => void {
	let timeout: ReturnType<typeof setTimeout> | null = null

	return (...args: Parameters<T>) => {
		if (timeout) {
			clearTimeout(timeout)
		}

		timeout = setTimeout(() => {
			fn(...args)
		}, delay)
	}
}

/**
 * Create a debounced search handler with loading state
 * @param searchFn - Async search function
 * @param delay - Debounce delay in milliseconds (default: 300ms)
 * @returns Object with search function and loading state
 */
export function useDebouncedSearch<T>(
	searchFn: (query: string) => Promise<T>,
	delay: number = 300,
) {
	const isSearching = ref(false)
	const searchQuery = ref('')
	const debouncedQuery = useDebounce(searchQuery, delay)
	const results = ref<T | null>(null)
	const error = ref<string | null>(null)

	watch(debouncedQuery, async (query) => {
		if (!query || query.length < 2) {
			results.value = null
			return
		}

		isSearching.value = true
		error.value = null

		try {
			results.value = await searchFn(query)
		} catch (err) {
			error.value = err instanceof Error ? err.message : 'Search failed'
			results.value = null
		} finally {
			isSearching.value = false
		}
	})

	const reset = () => {
		searchQuery.value = ''
		results.value = null
		error.value = null
		isSearching.value = false
	}

	return {
		searchQuery,
		debouncedQuery,
		isSearching,
		results,
		error,
		reset,
	}
}
