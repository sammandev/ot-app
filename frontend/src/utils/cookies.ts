/**
 * Read a cookie value by name from `document.cookie`.
 *
 * @param name — Cookie name to look up
 * @returns The cookie value, or `null` if not found
 */
export function getCookie(name: string): string | null {
	const value = `; ${document.cookie}`
	const parts = value.split(`; ${name}=`)
	if (parts.length === 2) {
		return parts.pop()?.split(';').shift() || null
	}
	return null
}
