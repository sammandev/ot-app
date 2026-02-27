<template>
    <Teleport to="body">
        <div class="fixed inset-0 z-[99999] flex items-center justify-center p-4">
            <!-- Backdrop -->
            <div class="absolute inset-0 bg-black/50" @click="$emit('close')"></div>

            <!-- Modal -->
            <div
                role="dialog" aria-modal="true" aria-labelledby="holiday-form-modal-title"
                class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md max-h-[90vh] flex flex-col overflow-hidden">
                <!-- Header -->
                <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 id="holiday-form-modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">
                        {{ holiday ? t('calendar.holidayForm.editTitle') : t('calendar.holidayForm.addTitle') }}
                    </h3>
                    <button @click="$emit('close')"
                        class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
                        <XMarkIcon class="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                <!-- Form -->
                <form @submit.prevent="handleSubmit" class="p-4 space-y-4 overflow-y-auto flex-1">
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
                        <input type="checkbox" v-model="form.is_recurring" id="recurring"
                            class="w-4 h-4 text-brand-600 border-gray-300 rounded focus:ring-brand-500" />
                        <label for="recurring" class="text-sm text-gray-700 dark:text-gray-300">
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
                </form>

                <!-- Footer -->
                <div
                    class="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                    <button v-if="holiday && canDelete" type="button" @click="$emit('delete', holiday.id)"
                        class="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 rounded-lg border border-red-300 dark:border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition">
                        {{ t('calendar.holidayForm.delete') }}
                    </button>
                    <div v-else></div>

                    <div class="flex items-center gap-2">
                        <button type="button" @click="$emit('close')"
                            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                            {{ t('calendar.holidayForm.cancel') }}
                        </button>
                        <button type="submit" @click="handleSubmit" :disabled="!form.title || selectedDates.length === 0" :class="[
                            'px-4 py-2 text-sm font-medium rounded-lg border transition',
                            form.title && selectedDates.length > 0
                                ? 'text-brand-700 dark:text-brand-300 border-brand-500 hover:bg-brand-50 dark:hover:bg-brand-900/20'
                                : 'text-gray-400 border-gray-300 dark:border-gray-600 cursor-not-allowed'
                        ]">
                            {{ holiday ? t('calendar.holidayForm.update') : t('calendar.holidayForm.create') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<script setup lang="ts">
import flatpickr from 'flatpickr'
import type { Instance } from 'flatpickr/dist/types/instance'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { attachMonthScrollStandalone } from '@/composables/useFlatpickrScroll'
import { XMarkIcon } from '@/icons'
import type { Holiday } from '@/services/api/holiday'

const { t } = useI18n()

interface Props {
	holiday?: Holiday | null
	initialDate?: string | null
	initialDates?: string[] | null
	canDelete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	holiday: null,
	initialDate: null,
	initialDates: null,
	canDelete: false,
})

const emit = defineEmits<{
	(e: 'close'): void
	(e: 'save', data: Partial<Holiday> & { dates?: string[] }): void
	(e: 'delete', id: number): void
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
	color: '#FFB6C1',
	description: '',
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

// Initialize form with holiday data or initial date
watch(
	() => [props.holiday, props.initialDate, props.initialDates],
	() => {
		if (props.holiday) {
			form.value = {
				title: props.holiday.title,
				color: props.holiday.color || '#FFB6C1',
				description: props.holiday.description || '',
				is_recurring: props.holiday.is_recurring,
			}
			selectedDates.value = [props.holiday.date]
		} else {
			const today = new Date().toISOString().split('T')[0] ?? ''
			form.value = {
				title: '',
				color: '#FFB6C1',
				description: '',
				is_recurring: false,
			}
			// Support initial dates array for range selection
			if (props.initialDates && props.initialDates.length > 0) {
				selectedDates.value = [...props.initialDates]
			} else {
				selectedDates.value = props.initialDate ? [props.initialDate] : [today]
			}
		}
		// Update flatpickr if it exists
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
		...form.value,
		date: primaryDate,
		dates: selectedDates.value,
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
onMounted(() => {
	nextTick(() => {
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
})

onUnmounted(() => {
	if (flatpickrInstance) {
		flatpickrInstance.destroy()
		flatpickrInstance = null
	}
})
</script>
