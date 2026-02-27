<template>
    <form @submit.prevent="handleSubmit" class="p-4 space-y-4">
        <!-- Title -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('calendar.holidayForm.holidayTitle') }} *
            </label>
            <input type="text" v-model="form.title" required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                :placeholder="t('calendar.holidayForm.titlePlaceholder')" />
        </div>

        <!-- Date Range -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('calendar.holidayForm.dates') }} *
            </label>
            <div class="relative">
                <input ref="dateInput" type="text" v-model="dateDisplay" required readonly
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 cursor-pointer"
                    :placeholder="t('calendar.holidayForm.selectDates')" />
            </div>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {{ t('calendar.holidayForm.dateRangeHint') }}
            </p>
        </div>

        <!-- Color -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('calendar.holidayForm.color') }}
            </label>
            <div class="flex items-center gap-3">
                <input type="color" v-model="form.color"
                    class="w-10 h-10 rounded cursor-pointer border border-gray-300 dark:border-gray-600" />
                <div class="flex flex-wrap gap-2">
                    <button v-for="preset in colorPresets" :key="preset" type="button"
                        @click="form.color = preset" :style="{ backgroundColor: preset }" :class="[
                            'w-8 h-8 rounded-full border-2 transition',
                            form.color === preset ? 'border-gray-900 dark:border-white scale-110' : 'border-transparent'
                        ]">
                    </button>
                </div>
            </div>
        </div>

        <!-- Description -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('calendar.holidayForm.description') }}
            </label>
            <textarea v-model="form.description" rows="3"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 resize-none"
                :placeholder="t('calendar.holidayForm.descriptionPlaceholder')"></textarea>
        </div>

        <!-- Recurring -->
        <div class="flex items-center gap-2">
            <input type="checkbox" v-model="form.is_recurring" id="combined_is_recurring"
                class="w-4 h-4 text-brand-600 border-gray-300 rounded focus:ring-brand-500" />
            <label for="combined_is_recurring" class="text-sm text-gray-700 dark:text-gray-300">
                {{ t('calendar.holidayForm.recurringAnnually') }}
            </label>
        </div>

        <!-- Preview -->
        <div class="p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">{{ t('calendar.holidayForm.preview') }}</div>
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium" :style="{
                backgroundColor: form.color,
                color: getContrastColor(form.color)
            }">
                {{ form.title || t('calendar.holidayForm.previewPlaceholder') }}
            </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <button type="button" @click="$emit('cancel')"
                class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                {{ t('calendar.holidayForm.cancel') }}
            </button>
            <button type="submit" :disabled="!form.title || selectedDates.length === 0" :class="[
                'px-4 py-2 text-sm font-medium rounded-lg border transition',
                form.title && selectedDates.length > 0
                    ? 'text-brand-700 dark:text-brand-300 border-brand-500 hover:bg-brand-50 dark:hover:bg-brand-900/20'
                    : 'text-gray-400 border-gray-300 dark:border-gray-600 cursor-not-allowed'
            ]">
                {{ t('calendar.holidayForm.create') }}
            </button>
        </div>
    </form>
</template>

<script setup lang="ts">
import flatpickr from 'flatpickr'
import type { Instance } from 'flatpickr/dist/types/instance'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { attachMonthScrollStandalone } from '@/composables/useFlatpickrScroll'
import type { Holiday } from '@/services/api/holiday'

const { t } = useI18n()

interface Props {
	initialDate?: string | null
	initialDates?: string[] | null
}

const props = withDefaults(defineProps<Props>(), {
	initialDate: null,
	initialDates: null,
})

const emit = defineEmits<{
	(e: 'save', data: Partial<Holiday> & { dates?: string[] }): void
	(e: 'cancel'): void
}>()

const colorPresets = [
	'#FFB6C1', // Light Pink (default)
	'#FFD700', // Gold
	'#98FB98', // Pale Green
	'#87CEEB', // Sky Blue
	'#DDA0DD', // Plum
	'#F0E68C', // Khaki
	'#FFA07A', // Light Salmon
	'#B0E0E6', // Powder Blue
]

const dateInput = ref<HTMLInputElement | null>(null)
let flatpickrInstance: Instance | null = null
const selectedDates = ref<string[]>([])

const form = ref({
	title: '',
	description: '',
	color: '#FFB6C1',
	is_recurring: false,
})

// Computed display for date(s)
const dateDisplay = computed(() => {
	if (selectedDates.value.length === 0) return ''
	const firstDate = selectedDates.value[0]
	if (selectedDates.value.length === 1) return firstDate ?? ''
	const lastDate = selectedDates.value[selectedDates.value.length - 1]
	return `${firstDate ?? ''} to ${lastDate ?? ''}`
})

// Initialize with initial date
watch(
	() => [props.initialDate, props.initialDates],
	() => {
		const today = new Date().toISOString().split('T')[0] ?? ''
		if (props.initialDates && props.initialDates.length > 0) {
			selectedDates.value = [...props.initialDates]
		} else {
			selectedDates.value = props.initialDate ? [props.initialDate] : [today]
		}
		if (flatpickrInstance && selectedDates.value.length > 0) {
			flatpickrInstance.setDate(selectedDates.value, false)
		}
	},
	{ immediate: true },
)

const getContrastColor = (hexColor: string): string => {
	const hex = hexColor.replace('#', '')
	const r = parseInt(hex.substr(0, 2), 16)
	const g = parseInt(hex.substr(2, 2), 16)
	const b = parseInt(hex.substr(4, 2), 16)
	const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
	return luminance > 0.5 ? '#1f2937' : '#ffffff'
}

const handleSubmit = () => {
	if (!form.value.title || selectedDates.value.length === 0) return
	const primaryDate = selectedDates.value[0]
	if (!primaryDate) return

	emit('save', {
		title: form.value.title,
		date: primaryDate,
		dates: selectedDates.value,
		description: form.value.description || undefined,
		color: form.value.color,
		is_recurring: form.value.is_recurring,
	})
}

// Helper function to format date to YYYY-MM-DD
const formatDateStr = (date: Date): string => {
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	return `${year}-${month}-${day}`
}

// Helper function to generate all dates between start and end (inclusive)
const getDateRange = (startDate: Date, endDate: Date): string[] => {
	const dates: string[] = []
	const current = new Date(startDate)
	current.setHours(0, 0, 0, 0)
	const end = new Date(endDate)
	end.setHours(0, 0, 0, 0)

	while (current <= end) {
		dates.push(formatDateStr(current))
		current.setDate(current.getDate() + 1)
	}

	return dates
}

// Initialize flatpickr with range mode
onMounted(async () => {
	await nextTick()
	if (dateInput.value) {
		flatpickrInstance = flatpickr(dateInput.value, {
			mode: 'range',
			dateFormat: 'Y-m-d',
			defaultDate: selectedDates.value.length > 0 ? selectedDates.value : undefined,
			onChange: (dates) => {
				if (dates.length === 2) {
					// Range selected - generate all dates in between
					selectedDates.value = getDateRange(dates[0]!, dates[1]!)
				} else if (dates.length === 1) {
					// Single date selected
					selectedDates.value = [formatDateStr(dates[0]!)]
				} else {
					selectedDates.value = []
				}
			},
			onReady: (_selectedDates, _dateStr, instance) => {
				attachMonthScrollStandalone(instance)
			},
			disableMobile: true,
			static: false,
			appendTo: document.body,
		})
	}
})

onUnmounted(() => {
	if (flatpickrInstance) {
		flatpickrInstance.destroy()
		flatpickrInstance = null
	}
})
</script>
