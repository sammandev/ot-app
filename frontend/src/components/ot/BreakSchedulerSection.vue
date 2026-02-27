<template>
  <div class="space-y-4 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-900/40">
    <div class="flex flex-col items-center justify-center gap-1">
      <label :class="disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'"
        class="flex items-center gap-2 text-sm font-semibold text-gray-900 dark:text-white">
        <div class="relative">
          <input v-model="hasBreakModel" type="checkbox" class="sr-only" :disabled="disabled" />
          <div
            :class="hasBreakModel ? 'border-brand-500 bg-brand-500' : 'bg-transparent border-gray-300 dark:border-gray-700'"
            class="mr-2 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] hover:border-brand-500 dark:hover:border-brand-500">
            <span :class="hasBreakModel ? '' : 'opacity-0'">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11.6666 3.5L5.24992 9.91667L2.33325 7" stroke="white" stroke-width="1.94437"
                  stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </span>
          </div>
        </div>
        {{ t('otForm.takeBreak') }}
      </label>
      <p class="text-xs text-center text-gray-500 dark:text-gray-400">{{ t('otForm.breakRule') }}</p>
    </div>
    <div class="space-y-4" v-if="hasBreakModel">
      <div class="grid gap-4 md:grid-cols-2">
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('otForm.breakStart') }}</label>
          <flat-pickr v-model="breakStartModel" :config="timePickerConfig" :disabled="disabled"
            :class="disabled ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''"
            class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800" />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('otForm.breakEnd') }}</label>
          <flat-pickr v-model="breakEndModel" :config="timePickerConfig" :disabled="disabled"
            :class="disabled ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''"
            class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800" />
        </div>
      </div>
      <div class="grid gap-4 md:grid-cols-2" v-if="showSecondBreak">
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('otForm.break2Start') }}</label>
          <flat-pickr v-model="breakStart2Model" :config="timePickerConfig" :disabled="disabled"
            :class="disabled ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''"
            class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800" />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('otForm.break2End') }}</label>
          <flat-pickr v-model="breakEnd2Model" :config="timePickerConfig" :disabled="disabled"
            :class="disabled ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''"
            class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800" />
        </div>
      </div>
      <div class="grid gap-4 md:grid-cols-2" v-if="showThirdBreak">
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('otForm.break3Start') }}</label>
          <flat-pickr v-model="breakStart3Model" :config="timePickerConfig" :disabled="disabled"
            :class="disabled ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''"
            class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800" />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('otForm.break3End') }}</label>
          <flat-pickr v-model="breakEnd3Model" :config="timePickerConfig" :disabled="disabled"
            :class="disabled ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''"
            class="dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800" />
        </div>
      </div>
    </div>
    <div class="text-sm text-gray-600 dark:text-gray-300">
      <div class="flex flex-wrap justify-center gap-3">
        <span
          class="badge px-4 py-1.5 text-sm font-semibold rounded-full border border-amber-200 bg-amber-100 text-amber-700 dark:border-amber-700 dark:bg-amber-900/30 dark:text-amber-300">{{
            t('otForm.breakHours') }}: {{ totalBreakHours.toFixed(2) }}</span>
        <span
          class="badge px-4 py-1.5 text-sm font-semibold rounded-full border border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">{{
            t('otForm.overtimeHours') }}: {{ totalHours.toFixed(2) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
	hasBreak: boolean
	breakStart: string
	breakEnd: string
	breakStart2: string
	breakEnd2: string
	breakStart3: string
	breakEnd3: string
	showSecondBreak: boolean
	showThirdBreak: boolean
	totalBreakHours: number
	totalHours: number
	timePickerConfig: Record<string, unknown>
	disabled?: boolean
}>()

const emit = defineEmits<{
	'update:hasBreak': [value: boolean]
	'update:breakStart': [value: string]
	'update:breakEnd': [value: string]
	'update:breakStart2': [value: string]
	'update:breakEnd2': [value: string]
	'update:breakStart3': [value: string]
	'update:breakEnd3': [value: string]
}>()

const hasBreakModel = computed({
	get: () => props.hasBreak,
	set: (v: boolean) => emit('update:hasBreak', v),
})
const breakStartModel = computed({
	get: () => props.breakStart,
	set: (v: string) => emit('update:breakStart', v),
})
const breakEndModel = computed({
	get: () => props.breakEnd,
	set: (v: string) => emit('update:breakEnd', v),
})
const breakStart2Model = computed({
	get: () => props.breakStart2,
	set: (v: string) => emit('update:breakStart2', v),
})
const breakEnd2Model = computed({
	get: () => props.breakEnd2,
	set: (v: string) => emit('update:breakEnd2', v),
})
const breakStart3Model = computed({
	get: () => props.breakStart3,
	set: (v: string) => emit('update:breakStart3', v),
})
const breakEnd3Model = computed({
	get: () => props.breakEnd3,
	set: (v: string) => emit('update:breakEnd3', v),
})
</script>
