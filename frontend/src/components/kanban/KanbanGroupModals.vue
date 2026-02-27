<template>
    <!-- Create Group Modal -->
    <div v-if="showGroupModal" class="fixed inset-0 bg-black/50 z-[100000] flex items-center justify-center p-4"
        @click.self="$emit('close-group-modal')">
        <div role="dialog" aria-modal="true" aria-labelledby="kanban-group-modal-title"
            class="bg-white dark:bg-gray-900 rounded-xl w-full max-w-lg border border-gray-200 dark:border-gray-700 flex flex-col max-h-[90vh]">
            <!-- Modal Header -->
            <div class="p-6 pb-4 border-b border-gray-200 dark:border-gray-700">
                <h2 id="kanban-group-modal-title" class="text-xl font-bold text-gray-900 dark:text-white">{{ t('kanban.createNewGroup') }}</h2>
            </div>

            <!-- Modal Body (Scrollable) -->
            <form @submit.prevent="$emit('save-group')" class="flex-1 overflow-y-auto p-6 pt-4 space-y-4">
                <!-- Group Name -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.groupNameRequired') }}</label>
                    <input v-model="groupForm.name" type="text" required
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                        :placeholder="t('kanban.enterGroupName')" />
                </div>

                <!-- Group Description -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.description') }}</label>
                    <textarea v-model="groupForm.description" rows="2"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                        :placeholder="t('kanban.enterGroupDesc')"></textarea>
                </div>

                <!-- Group Color with Templates -->
                <GroupColorPicker v-model="groupForm.color" :color-templates="colorTemplates" />

                <!-- Preview -->
                <div class="p-3 rounded-lg border-l-4" :style="{
                    backgroundColor: groupForm.color + '15',
                    borderLeftColor: groupForm.color
                }">
                    <span class="text-sm font-medium" :style="{ color: groupForm.color }">
                        {{ groupForm.name || t('kanban.groupPreview') }}
                    </span>
                </div>

                <!-- Group Members -->
                <MemberSelector
                    v-model="groupForm.members"
                    :employees="filteredGroupMembers"
                    :all-employees="allEmployees"
                    :group-member-search="groupMemberSearch"
                    @update:search="$emit('update:groupMemberSearch', $event)"
                />
            </form>

            <!-- Modal Footer -->
            <div class="flex justify-end gap-3 p-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button type="button" @click="$emit('close-group-modal')"
                    class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg">{{ t('common.cancel') }}</button>
                <button @click="$emit('save-group')"
                    class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700">{{ t('kanban.createGroup') }}</button>
            </div>
        </div>
    </div>

    <!-- List Groups Modal -->
    <div v-if="showListGroupsModal"
        class="fixed inset-0 bg-black/50 z-[100000] flex items-center justify-center p-4"
        @click.self="$emit('close-list-groups-modal')">
        <div role="dialog" aria-modal="true" aria-labelledby="kanban-groups-list-title"
            class="bg-white dark:bg-gray-900 rounded-xl w-full max-w-3xl border border-gray-200 dark:border-gray-700 flex flex-col max-h-[90vh]">
            <!-- Modal Header -->
            <div class="p-6 pb-4 border-b border-gray-200 dark:border-gray-700">
                <div class="flex items-center justify-between">
                    <h2 id="kanban-groups-list-title" class="text-xl font-bold text-gray-900 dark:text-white">{{ t('kanban.taskGroups') }}</h2>
                    <div class="flex items-center gap-2">
                        <button @click="$emit('sync-department-groups')" :disabled="syncingDepartments"
                            class="px-3 py-1.5 text-sm bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition disabled:opacity-50 flex items-center gap-1.5"
                            title="Create/update groups based on departments">
                            <HourglassIcon v-if="syncingDepartments" class="w-4 h-4" />
                            <RefreshIcon v-else class="w-4 h-4" />
                            {{ t('kanban.syncDepartments') }}
                        </button>
                        <button @click="$emit('close-list-groups-modal')"
                            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
                            <XIcon class="w-5 h-5 text-gray-500" />
                        </button>
                    </div>
                </div>
                <!-- Tabs -->
                <div class="flex gap-2 mt-4">
                    <button @click="$emit('update:listGroupsTab', 'all')" :class="[
                        'px-4 py-2 rounded-lg text-sm font-medium transition',
                        listGroupsTab === 'all'
                            ? 'bg-brand-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                    ]">
                        {{ t('kanban.allGroups') }} ({{ taskGroups.length }})
                    </button>
                    <button v-if="editingGroup" @click="$emit('update:listGroupsTab', 'edit')" :class="[
                        'px-4 py-2 rounded-lg text-sm font-medium transition',
                        listGroupsTab === 'edit'
                            ? 'bg-brand-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                    ]">
                        {{ t('kanban.editGroup') }}
                    </button>
                </div>
            </div>

            <!-- Modal Body -->
            <div class="flex-1 overflow-y-auto p-6">
                <!-- All Groups Tab -->
                <div v-if="listGroupsTab === 'all'" class="space-y-3">
                    <div v-if="taskGroups.length === 0" class="text-center py-12 text-gray-400">
                        <FolderIcon class="w-10 h-10 mx-auto mb-2 text-gray-400" />
                        <p>{{ t('kanban.noGroupsYet') }}</p>
                        <button @click="$emit('close-list-groups-modal'); $emit('open-group-modal')"
                            class="mt-4 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700">
                            {{ t('kanban.createFirstGroup') }}
                        </button>
                    </div>

                    <div v-for="group in taskGroups" :key="group.id"
                        class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border-l-4 group hover:shadow-md transition"
                        :style="{ borderLeftColor: group.color }">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <div class="flex items-center gap-2 mb-1">
                                    <div class="w-4 h-4 rounded-full" :style="{ backgroundColor: group.color }">
                                    </div>
                                    <h3 class="font-semibold text-gray-900 dark:text-white">{{ group.name }}</h3>
                                    <span v-if="group.is_department_group"
                                        class="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                                        {{ t('kanban.departmentBadge') }}
                                    </span>
                                </div>
                                <p v-if="group.description" class="text-sm text-gray-500 dark:text-gray-400 mb-2">
                                    {{ group.description }}
                                </p>
                                <div
                                    class="flex flex-wrap items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                    <span>{{ group.members?.length || 0 }} {{ t('kanban.members') }}</span>
                                    <span>•</span>
                                    <span>{{ group.task_count || 0 }} {{ t('kanban.tasks') }}</span>
                                </div>
                                <!-- Member Avatars Preview -->
                                <div v-if="group.members && group.members.length > 0" class="flex -space-x-2 mt-2">
                                    <div v-for="memberId in group.members.slice(0, 5)" :key="memberId"
                                        class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium ring-2 ring-white dark:ring-gray-800"
                                        :style="{ backgroundColor: group.color + '30', color: group.color }">
                                        {{ getInitials(getEmployeeName(memberId)) }}
                                    </div>
                                    <div v-if="group.members.length > 5"
                                        class="w-7 h-7 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center text-xs font-medium ring-2 ring-white dark:ring-gray-800">
                                        +{{ group.members.length - 5 }}
                                    </div>
                                </div>
                            </div>
                            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                                <button v-if="!group.is_department_group" @click="$emit('start-edit-group', group)"
                                    class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg text-gray-500 hover:text-brand-600"
                                    title="Edit Group">
                                    <PencilIcon class="w-4 h-4" />
                                </button>
                                <button v-if="!group.is_department_group" @click="$emit('delete-group', group.id)"
                                    class="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 rounded-lg text-gray-500 hover:text-red-600"
                                    title="Delete Group">
                                    <TrashIcon class="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Edit Group Tab -->
                <div v-if="listGroupsTab === 'edit' && editingGroup" class="space-y-4">
                    <!-- Group Name -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.groupNameRequired') }}</label>
                        <input v-model="editGroupForm.name" type="text" required
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                            :placeholder="t('kanban.enterGroupName')" />
                    </div>

                    <!-- Group Description -->
                    <div>
                        <label
                            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.description') }}</label>
                        <textarea v-model="editGroupForm.description" rows="2"
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                            :placeholder="t('kanban.enterGroupDesc')"></textarea>
                    </div>

                    <!-- Group Color with Templates -->
                    <GroupColorPicker v-model="editGroupForm.color" :color-templates="colorTemplates" />

                    <!-- Preview -->
                    <div class="p-3 rounded-lg border-l-4" :style="{
                        backgroundColor: editGroupForm.color + '15',
                        borderLeftColor: editGroupForm.color
                    }">
                        <span class="text-sm font-medium" :style="{ color: editGroupForm.color }">
                            {{ editGroupForm.name || t('kanban.groupPreview') }}
                        </span>
                    </div>

                    <!-- Group Members -->
                    <MemberSelector
                        v-model="editGroupForm.members"
                        :employees="filteredGroupMembers"
                        :all-employees="allEmployees"
                        :group-member-search="groupMemberSearch"
                        @update:search="$emit('update:groupMemberSearch', $event)"
                    />

                    <!-- Edit Actions -->
                    <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <button type="button" @click="$emit('cancel-edit-group')"
                            class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg">
                            {{ t('common.cancel') }}
                        </button>
                        <button @click="$emit('save-edit-group')" :disabled="!editGroupForm.name.trim()"
                            class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50">
                            {{ t('kanban.saveChanges') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { colorTemplates, getInitials } from '@/composables/kanban'
import { FolderIcon, HourglassIcon, PencilIcon, RefreshIcon, TrashIcon, XIcon } from '@/icons'
import type { Employee } from '@/services/api/employee'
import type { TaskGroup } from '@/services/api/task'
import GroupColorPicker from './GroupColorPicker.vue'
import MemberSelector from './MemberSelector.vue'

const { t } = useI18n()

defineProps<{
	showGroupModal: boolean
	showListGroupsModal: boolean
	listGroupsTab: string
	editingGroup: TaskGroup | null
	syncingDepartments: boolean
	taskGroups: TaskGroup[]
	groupForm: { name: string; description: string; color: string; members: number[] }
	editGroupForm: { name: string; description: string; color: string; members: number[] }
	groupMemberSearch: string
	filteredGroupMembers: Employee[]
	allEmployees: Employee[]
	getEmployeeName: (id: number) => string
}>()

defineEmits<{
	'close-group-modal': []
	'save-group': []
	'close-list-groups-modal': []
	'open-group-modal': []
	'sync-department-groups': []
	'start-edit-group': [group: TaskGroup]
	'delete-group': [id: number]
	'cancel-edit-group': []
	'save-edit-group': []
	'update:listGroupsTab': [value: string]
	'update:groupMemberSearch': [value: string]
}>()
</script>
