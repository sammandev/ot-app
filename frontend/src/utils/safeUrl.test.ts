import { describe, expect, it } from 'vitest'

import { toSafeExternalUrl } from '@/utils/safeUrl'

describe('toSafeExternalUrl', () => {
	it('allows https urls', () => {
		expect(toSafeExternalUrl('https://example.com/docs')).toBe('https://example.com/docs')
	})

	it('blocks javascript urls', () => {
		expect(toSafeExternalUrl('javascript:alert(1)')).toBeNull()
	})

	it('blocks data urls', () => {
		expect(toSafeExternalUrl('data:text/html;base64,SGk=')).toBeNull()
	})
})
