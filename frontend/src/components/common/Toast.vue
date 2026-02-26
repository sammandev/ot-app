<template>
  <Transition name="toast-slide" @enter="onEnter" @leave="onLeave">
    <div v-if="isVisible"
      class="fixed bottom-4 right-4 rounded-lg bg-gray-900 px-4 py-3 text-sm font-medium text-white shadow-lg dark:bg-gray-800 z-50">
      {{ message }}
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

// Multi-word component name for linting
defineOptions({
	name: 'ToastNotification',
})

const isVisible = ref(false)
const message = ref('')
let timeout: ReturnType<typeof setTimeout> | null = null

const showToast = (msg: string, duration = 3000) => {
	message.value = msg
	isVisible.value = true
	if (timeout) clearTimeout(timeout)
	timeout = setTimeout(() => {
		isVisible.value = false
	}, duration)
}

const onEnter = (el: Element) => {
	const node = el as HTMLElement
	node.style.opacity = '0'
	node.style.transform = 'translateX(400px)'
	void node.offsetHeight // force reflow
	node.style.transition = 'all 0.3s ease'
	node.style.opacity = '1'
	node.style.transform = 'translateX(0)'
}

const onLeave = (el: Element) => {
	const node = el as HTMLElement
	node.style.transition = 'all 0.3s ease'
	node.style.opacity = '0'
	node.style.transform = 'translateX(400px)'
}

onMounted(() => {
	window.addEventListener('sidebar-hidden', (e: Event) => {
		const evt = e as CustomEvent
		showToast(evt.detail?.message || 'Sidebar hidden.')
	})
	window.addEventListener('sidebar-restored', (e: Event) => {
		const evt = e as CustomEvent
		showToast(evt.detail?.message || 'Sidebar restored.')
	})
})
</script>

<style scoped>
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(400px);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(400px);
}
</style>
