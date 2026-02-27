/**
 * Production-safe logger that silences debug/info output in production builds.
 * Errors and warnings are always emitted regardless of environment.
 */
const isDev = import.meta.env.DEV

export const logger = {
	error: (...args: unknown[]) => console.error(...args),
	warn: (...args: unknown[]) => console.warn(...args),
	info: (...args: unknown[]) => {
		if (isDev) console.info(...args)
	},
	debug: (...args: unknown[]) => {
		if (isDev) console.debug(...args)
	},
}
