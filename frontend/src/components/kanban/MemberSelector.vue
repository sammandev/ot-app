<template>
    <div>
        <div class="flex items-center justify-between mb-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('kanban.members') }}</label>
            <div class="flex gap-2">
                <button type="button" @click="$emit('update:modelValue', allEmployees.map(e => e.id))"
                    class="text-xs text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300">
                    {{ t('common.selectAll') }}
                </button>
                <span class="text-gray-300 dark:text-gray-600">|</span>
                <button type="button" @click="$emit('update:modelValue', [])"
                    class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                    {{ t('common.deselectAll') }}
                </button>
            </div>
        </div>
        <!-- Member Search -->
        <input :value="groupMemberSearch" @input="$emit('update:search', ($event.target as HTMLInputElement).value)" type="text" :placeholder="t('kanban.searchEmployees')"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white mb-2 text-sm" />
        <div class="max-h-48 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-lg p-2 space-y-1">
            <button v-for="emp in employees" :key="emp.id" type="button"
                @click="toggleMember(emp.id)" :class="[
                    'w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left text-sm transition-colors',
                    modelValue.includes(emp.id)
                        ? 'bg-brand-50 dark:bg-brand-900/30 border border-brand-300 dark:border-brand-700 text-brand-700 dark:text-brand-300'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                ]">
                <div :class="[
                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                    modelValue.includes(emp.id)
                        ? 'bg-brand-200 dark:bg-brand-800 text-brand-700 dark:text-brand-300'
                        : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                ]">
                    {{ getInitials(emp.name) }}
                </div>
                <span class="flex-1 truncate">{{ emp.name }}</span>
                <span
                    class="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded">
                    {{ getDepartmentCode(emp.department) }}
                </span>
                <svg v-if="modelValue.includes(emp.id)" xmlns="http://www.w3.org/2000/svg"
                    class="w-4 h-4 text-brand-600" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M5 13l4 4L19 7" />
                </svg>
            </button>
            <p v-if="employees.length === 0" class="text-center text-gray-400 text-sm py-2">
                {{ groupMemberSearch ? t('kanban.noEmployeesFound') : t('kanban.noEmployeesAvailable') }}
            </p>
        </div>
        <p v-if="modelValue.length > 0" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ modelValue.length }} {{ t('kanban.membersSelected') }}
        </p>
    </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { getInitials } from '@/composables/kanban'
import type { Employee } from '@/services/api/employee'
import { useDepartmentStore } from '@/stores/department'

const { t } = useI18n()
const departmentStore = useDepartmentStore()

const props = defineProps<{
	modelValue: number[]
	employees: Employee[]
	allEmployees: Employee[]
	groupMemberSearch: string
}>()

const emit = defineEmits<{
	'update:modelValue': [value: number[]]
	'update:search': [value: string]
}>()

function getDepartmentCode(deptId: number | null): string {
	if (!deptId) return ''
	const dept = departmentStore.departments.find((d) => d.id === deptId)
	return dept?.code || ''
}

function toggleMember(id: number) {
	const idx = props.modelValue.indexOf(id)
	const newMembers = [...props.modelValue]
	if (idx >= 0) {
		newMembers.splice(idx, 1)
	} else {
		newMembers.push(id)
	}
	emit('update:modelValue', newMembers)
}
</script>
