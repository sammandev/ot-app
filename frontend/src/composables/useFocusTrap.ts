import { nextTick, onUnmounted, type Ref, watch } from 'vue'

const FOCUSABLE_SELECTOR = [
	'a[href]',
	'button:not([disabled])',
	'input:not([disabled]):not([type="hidden"])',
	'select:not([disabled])',
	'textarea:not([disabled])',
	'[tabindex]:not([tabindex="-1"])',
].join(', ')

/**
 * Composable that traps keyboard focus inside a modal element while it is visible.
 * Also restores focus to the previously focused element when the modal closes.
 *
 * @param containerRef - Ref to the dialog/modal root element
 * @param isOpen - Ref<boolean> controlling visibility
 */
export function useFocusTrap(containerRef: Ref<HTMLElement | null>, isOpen: Ref<boolean>) {
	let previouslyFocused: HTMLElement | null = null

	function getFocusableElements(): HTMLElement[] {
		if (!containerRef.value) return []
		return Array.from(containerRef.value.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
			(el) => el.offsetParent !== null, // visible only
		)
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key !== 'Tab') return
		const focusable = getFocusableElements()
		if (focusable.length === 0) {
			e.preventDefault()
			return
		}

		const first = focusable[0]!
		const last = focusable[focusable.length - 1]!

		if (e.shiftKey) {
			if (document.activeElement === first) {
				e.preventDefault()
				last.focus()
			}
		} else {
			if (document.activeElement === last) {
				e.preventDefault()
				first.focus()
			}
		}
	}

	function activate() {
		previouslyFocused = document.activeElement as HTMLElement | null
		document.addEventListener('keydown', handleKeyDown)
		nextTick(() => {
			const focusable = getFocusableElements()
			if (focusable.length > 0) {
				focusable[0]!.focus()
			}
		})
	}

	function deactivate() {
		document.removeEventListener('keydown', handleKeyDown)
		if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
			previouslyFocused.focus()
		}
		previouslyFocused = null
	}

	watch(isOpen, (val) => {
		if (val) {
			nextTick(() => activate())
		} else {
			deactivate()
		}
	})

	onUnmounted(() => {
		deactivate()
	})
}
