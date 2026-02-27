<template>
  <div ref="modalRef" class="fixed inset-0 flex items-center justify-center overflow-y-auto z-99999"
    role="dialog" aria-modal="true">
    <div
      v-if="fullScreenBackdrop"
      class="fixed inset-0 h-full w-full bg-gray-400/50 backdrop-blur-[32px]"
      aria-hidden="true"
      @click="$emit('close')"
    ></div>
    <slot name="body"></slot>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFocusTrap } from '@/composables/useFocusTrap'

interface ModalProps {
	fullScreenBackdrop?: boolean
}

defineProps<ModalProps>()
defineEmits(['close'])

const modalRef = ref<HTMLElement | null>(null)
const isOpen = computed(() => true) // Modal is always open when rendered
useFocusTrap(modalRef, isOpen)
</script>
