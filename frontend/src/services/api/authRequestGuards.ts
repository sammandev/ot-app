const AUTH_ENDPOINTS_TO_SKIP_REFRESH = [
	'/auth/login/local/',
	'/auth/login/external/',
	'/auth/exchange-token/',
	'/auth/token/verify/',
	'/auth/token/refresh/',
]

export const shouldSkipRefreshForUrl = (url?: string): boolean =>
	!!url && AUTH_ENDPOINTS_TO_SKIP_REFRESH.some((path) => url.includes(path))
