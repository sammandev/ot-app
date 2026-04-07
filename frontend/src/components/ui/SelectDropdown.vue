<template>
    <div class="relative" ref="containerRef">
        <button type="button" @click="toggle" :disabled="disabled"
            class="flex h-11 w-full items-center justify-between rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5"
            :class="[
                disabled && 'opacity-60 cursor-not-allowed hover:bg-white dark:hover:bg-gray-900',
                isOpen && 'ring-3 ring-brand-500/10 border-brand-300 dark:border-brand-800',
            ]">
            <span class="truncate">{{ displayLabel }}</span>
            <svg class="h-4 w-4 shrink-0 text-gray-400 transition-transform duration-200"
                :class="{ 'rotate-180': isOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
        </button>

        <div v-if="isOpen"
            class="absolute left-0 top-full z-30 mt-2 w-full min-w-[18rem] rounded-2xl border border-gray-200 bg-white p-3 shadow-2xl dark:border-gray-700 dark:bg-gray-900">
            <!-- Header -->
            <div class="mb-2 flex items-center gap-3">
                <div
                    class="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                    <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                    <span>{{ headerLabel }}</span>
                </div>
            </div>

            <!-- Search input -->
            <div v-if="searchable" class="mb-2">
                <input ref="searchInputRef" v-model="searchQuery" type="text" placeholder="Search..."
                    class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-2 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-gray-500"
                    @click.stop />
            </div>

            <!-- Options list -->
            <div v-if="filteredOptions.length === 0"
                class="rounded-xl bg-gray-50 px-3 py-4 text-center text-sm text-gray-500 dark:bg-gray-950 dark:text-gray-400">
                No matching options
            </div>
            <div v-else class="custom-scrollbar max-h-64 space-y-1 overflow-auto pr-1">
                <button v-for="option in filteredOptions" :key="option.value" type="button"
                    class="flex w-full cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-white/5"
                    @click="selectOption(option.value)">
                    <span class="min-w-0 flex-1 break-words text-left">{{ option.label }}</span>
                    <svg v-if="modelValue === option.value"
                        class="h-4 w-4 shrink-0 text-brand-600 dark:text-brand-400" fill="none" stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { FilterOption } from './FilterDropdown.vue'

export type { FilterOption }

const props = withDefaults(
    defineProps<{
        modelValue: string
        options: FilterOption[]
        placeholder?: string
        searchable?: boolean
        disabled?: boolean
    }>(),
    {
        placeholder: 'Select...',
        searchable: true,
        disabled: false,
    },
)

const emit = defineEmits<{
    'update:modelValue': [value: string]
}>()

const isOpen = ref(false)
const searchQuery = ref('')
const containerRef = ref<HTMLElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)

const headerLabel = computed(() => {
    return props.placeholder.replace(/^All\s+/i, '').trim() || 'Select'
})

const displayLabel = computed(() => {
    if (!props.modelValue) return props.placeholder
    const match = props.options.find((o: FilterOption) => o.value === props.modelValue)
    return match?.label ?? props.modelValue
})

const filteredOptions = computed(() => {
    if (!searchQuery.value.trim()) return props.options
    const q = searchQuery.value.trim().toLowerCase()
    return props.options.filter((o: FilterOption) => o.label.toLowerCase().includes(q))
})

const toggle = () => {
    if (props.disabled) return
    isOpen.value = !isOpen.value
    if (!isOpen.value) {
        searchQuery.value = ''
    }
}

const selectOption = (value: string) => {
    emit('update:modelValue', value)
    isOpen.value = false
    searchQuery.value = ''
}

const handleClickOutside = (event: MouseEvent) => {
    if (containerRef.value && event.target instanceof Node && !containerRef.value.contains(event.target)) {
        isOpen.value = false
        searchQuery.value = ''
    }
}

watch(isOpen, (open: boolean) => {
    if (open && props.searchable) {
        void nextTick(() => {
            searchInputRef.value?.focus()
        })
    }
})

onMounted(() => {
    document.addEventListener('mousedown', handleClickOutside)
})

onBeforeUnmount(() => {
    document.removeEventListener('mousedown', handleClickOutside)
})
</script>
