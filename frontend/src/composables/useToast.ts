import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
	id: number
	message: string
	type: ToastType
}

const toasts = ref<Toast[]>([])
let toastId = 0

export function useToast() {
	const showToast = (message: string, type: ToastType = 'info', duration = 3000) => {
		const id = ++toastId
		toasts.value.push({ id, message, type })

		// Auto-remove after duration
		setTimeout(() => {
			removeToast(id)
		}, duration)
	}

	const removeToast = (id: number) => {
		const index = toasts.value.findIndex((t) => t.id === id)
		if (index !== -1) {
			toasts.value.splice(index, 1)
		}
	}

	return {
		toasts,
		showToast,
		removeToast,
	}
}
