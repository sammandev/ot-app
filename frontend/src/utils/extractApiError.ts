interface ApiErrorObject {
	[key: string]: ApiErrorValue | undefined
}

type ApiErrorValue = string | string[] | ApiErrorObject

function flattenApiError(value: ApiErrorValue | undefined): string[] {
	if (!value) {
		return []
	}

	if (typeof value === 'string') {
		const trimmed = value.trim()
		return trimmed ? [trimmed] : []
	}

	if (Array.isArray(value)) {
		return value.flatMap((item) => flattenApiError(item))
	}

	return Object.entries(value).flatMap(([key, nestedValue]) => {
		const messages = flattenApiError(nestedValue)
		if (key === 'non_field_errors' || key === 'detail' || key === 'message') {
			return messages
		}
		return messages.map((message) => `${key}: ${message}`)
	})
}

/**
 * Extract a human-readable error message from an Axios error (or any unknown error).
 *
 * Supports common DRF error shapes like `detail`, `message`, field arrays,
 * and nested validation objects.
 */
export function extractApiError(err: unknown, fallback: string): string {
	const axiosError = err as {
		response?: {
			data?: {
				detail?: string
				message?: string
				non_field_errors?: string[]
				[key: string]: ApiErrorValue | undefined
			}
		}
	}

	const data = axiosError.response?.data
	const messages = flattenApiError(data)
	return messages[0] || fallback
}
