/**
 * Extract a human-readable error message from an Axios error (or any unknown error).
 *
 * Checks `response.data.detail` → `response.data.message` → fallback string.
 *
 * @param err — The caught error (typically from an Axios call)
 * @param fallback — Default message when no server message is available
 * @returns The extracted error string
 *
 * @example
 * ```ts
 * try {
 *   await departmentAPI.create(data)
 * } catch (err: unknown) {
 *   error.value = extractApiError(err, 'Failed to create department')
 *   throw err
 * }
 * ```
 */
export function extractApiError(err: unknown, fallback: string): string {
	const axiosError = err as {
		response?: { data?: { detail?: string; message?: string } }
	}
	return axiosError.response?.data?.detail || axiosError.response?.data?.message || fallback
}
