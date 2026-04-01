const ALLOWED_PROTOCOLS = new Set(['http:', 'https:'])

export function toSafeExternalUrl(value?: string | null): string | null {
	if (!value) return null

	const trimmed = value.trim()
	if (!trimmed) return null

	try {
		const url = new URL(trimmed, window.location.origin)
		if (!ALLOWED_PROTOCOLS.has(url.protocol)) {
			return null
		}
		return url.toString()
	} catch {
		return null
	}
}
