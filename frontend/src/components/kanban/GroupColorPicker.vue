<template>
    <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('kanban.color') }}</label>
        <!-- Color Templates -->
        <div class="grid grid-cols-9 gap-2 mb-3">
            <button v-for="template in colorTemplates" :key="template.color" type="button"
                @click="$emit('update:modelValue', template.color)" :class="[
                    'w-8 h-8 rounded-lg border-2 transition-[border-color,transform,box-shadow]',
                    modelValue === template.color
                        ? 'border-gray-900 dark:border-white scale-110 shadow-md'
                        : 'border-transparent hover:scale-105'
                ]" :style="{ backgroundColor: template.color }" :title="template.name">
            </button>
        </div>
        <!-- Custom Color Picker -->
        <div class="flex items-center gap-2">
            <input :value="modelValue" @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)" type="color"
                class="w-10 h-10 border border-gray-300 dark:border-gray-600 rounded cursor-pointer" />
            <input :value="modelValue" @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)" type="text"
                class="w-24 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm"
                placeholder="#6366F1" />
            <span class="text-xs text-gray-500">{{ t('kanban.custom') }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps<{
	modelValue: string
	colorTemplates: Array<{ color: string; name: string }>
}>()

defineEmits<{
	'update:modelValue': [value: string]
}>()
</script>
