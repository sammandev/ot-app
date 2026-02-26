import { createI18n } from 'vue-i18n'
import en from './locales/en'
import id from './locales/id'
import zh from './locales/zh'

export type SupportedLocale = 'en' | 'zh' | 'id'

export const LOCALE_STORAGE_KEY = 'app_locale'

export const supportedLocales: { code: SupportedLocale; name: string; flag: string }[] = [
	{ code: 'en', name: 'English', flag: '🇺🇸' },
	{ code: 'zh', name: '中文', flag: '🇨🇳' },
	{ code: 'id', name: 'Bahasa', flag: '🇮🇩' },
]

function getStoredLocale(): SupportedLocale {
	const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
	if (stored && ['en', 'zh', 'id'].includes(stored)) {
		return stored as SupportedLocale
	}
	return 'en'
}

const i18n = createI18n({
	legacy: false,
	locale: getStoredLocale(),
	fallbackLocale: 'en',
	messages: { en, zh, id },
})

export function setLocale(locale: SupportedLocale) {
	i18n.global.locale.value = locale
	localStorage.setItem(LOCALE_STORAGE_KEY, locale)
	document.documentElement.setAttribute('lang', locale)
}

export default i18n
