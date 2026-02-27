<template>
  <div class="relative" ref="dropdownRef">
    <button type="button" @click="!disabled && (open = !open)"
      class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border bg-transparent bg-none px-4 py-2.5 pr-11 text-sm text-center shadow-theme-xs focus:outline-hidden focus:ring-3 dark:bg-gray-900 truncate"
      :class="[
        error ? 'border-error-300 text-gray-800 focus:border-error-300 focus:ring-error-500/10 dark:border-error-700 dark:text-white/90 dark:focus:border-error-800' : 'border-gray-300 text-gray-800 focus:border-brand-300 focus:ring-brand-500/10 dark:border-gray-700 dark:text-white/90 dark:focus:border-brand-800',
        disabled ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''
      ]" :disabled="disabled">
      {{ displayText }}
    </button>
    <span class="absolute z-30 text-gray-500 -translate-y-1/2 pointer-events-none right-4 top-1/2 dark:text-gray-400">
      <svg class="stroke-current" width="20" height="20" viewBox="0 0 20 20" fill="none"
        xmlns="http://www.w3.org/2000/svg">
        <path d="M4.79175 7.396L10.0001 12.6043L15.2084 7.396" stroke="" stroke-width="1.5"
          stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </span>
    <div v-if="open"
      class="absolute z-50 mt-1 w-full rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900">
      <div class="p-2">
        <input v-model="search" type="text" :placeholder="searchPlaceholder"
          class="w-full rounded-md border border-gray-300 bg-transparent px-3 py-2 text-sm focus:border-brand-300 focus:outline-hidden focus:ring-1 focus:ring-brand-500/20 dark:border-gray-600 dark:text-white dark:placeholder:text-gray-400"
          @click.stop ref="searchInputRef" />
      </div>
      <ul class="max-h-60 overflow-y-auto py-1">
        <li v-for="item in filtered" :key="item.id" @click="select(item.id)"
          class="cursor-pointer px-4 py-2 text-sm text-center hover:bg-gray-100 dark:hover:bg-gray-800"
          :class="[
            modelValue === item.id ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/20 dark:text-brand-300 font-medium' : 'text-gray-700 dark:text-gray-300'
          ]">
          {{ item.name }}
        </li>
        <slot name="extra-items"></slot>
        <li v-if="filtered.length === 0"
          class="px-4 py-2 text-sm text-center text-gray-400 dark:text-gray-500">{{ noResultsText }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

export interface DropdownItem {
	id: string
	name: string
}

const props = withDefaults(
	defineProps<{
		modelValue: string
		items: DropdownItem[]
		placeholder?: string
		searchPlaceholder?: string
		noResultsText?: string
		disabled?: boolean
		error?: string
	}>(),
	{
		placeholder: 'Select...',
		searchPlaceholder: 'Search...',
		noResultsText: 'No results found',
		disabled: false,
		error: '',
	},
)

const emit = defineEmits<{
	'update:modelValue': [value: string]
}>()

const open = ref(false)
const search = ref('')
const dropdownRef = ref<HTMLElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)

const displayText = computed(() => {
	if (!props.modelValue) return props.placeholder
	const item = props.items.find((i) => i.id === props.modelValue)
	return item?.name || props.placeholder
})

const filtered = computed(() => {
	if (!search.value) return props.items
	const q = search.value.toLowerCase()
	return props.items.filter((i) => i.name.toLowerCase().includes(q))
})

function select(id: string) {
	emit('update:modelValue', id)
	open.value = false
	search.value = ''
}

function handleClickOutside(e: MouseEvent) {
	if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
		open.value = false
		search.value = ''
	}
}

watch(open, (val) => {
	if (val) nextTick(() => searchInputRef.value?.focus())
})

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside))
</script>
