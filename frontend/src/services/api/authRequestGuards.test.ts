import { describe, expect, it } from 'vitest'

import { shouldSkipRefreshForUrl } from '@/services/api/authRequestGuards'

describe('shouldSkipRefreshForUrl', () => {
	it('skips refresh for login endpoints', () => {
		expect(shouldSkipRefreshForUrl('/auth/login/local/')).toBe(true)
		expect(shouldSkipRefreshForUrl('/auth/login/external/')).toBe(true)
	})

	it('skips refresh for exchange, verify, and refresh endpoints', () => {
		expect(shouldSkipRefreshForUrl('/auth/exchange-token/')).toBe(true)
		expect(shouldSkipRefreshForUrl('/auth/token/verify/')).toBe(true)
		expect(shouldSkipRefreshForUrl('/auth/token/refresh/')).toBe(true)
	})

	it('does not skip refresh for protected business endpoints', () => {
		expect(shouldSkipRefreshForUrl('/v1/overtime-requests/')).toBe(false)
		expect(shouldSkipRefreshForUrl('/v1/notifications/')).toBe(false)
	})
})
