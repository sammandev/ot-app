import { reactive, ref } from 'vue'

export interface ConfirmDialogOptions {
	title: string
	message: string
	type?: 'danger' | 'warning' | 'info'
	confirmLabel?: string
	cancelLabel?: string
}

const visible = ref(false)
const options = reactive<ConfirmDialogOptions>({
	title: '',
	message: '',
	type: 'danger',
	confirmLabel: 'Confirm',
	cancelLabel: 'Cancel',
})

let resolvePromise: ((value: boolean) => void) | null = null

export function useConfirmDialog() {
	const confirm = (opts: ConfirmDialogOptions): Promise<boolean> => {
		options.title = opts.title
		options.message = opts.message
		options.type = opts.type || 'danger'
		options.confirmLabel = opts.confirmLabel || 'Confirm'
		options.cancelLabel = opts.cancelLabel || 'Cancel'
		visible.value = true

		return new Promise((resolve) => {
			resolvePromise = resolve
		})
	}

	const onConfirm = () => {
		visible.value = false
		resolvePromise?.(true)
		resolvePromise = null
	}

	const onCancel = () => {
		visible.value = false
		resolvePromise?.(false)
		resolvePromise = null
	}

	return { visible, options, confirm, onConfirm, onCancel }
}
