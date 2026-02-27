<template>
    <AdminLayout>
        <div class="h-full flex flex-col">
            <!-- Header -->
            <div class="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ t('pages.kanban.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.kanban.subtitle') }}</p>
                </div>
                <div class="flex items-center gap-3">
                    <!-- Live Presence Indicator -->
                    <PresenceIndicator :viewers="boardWs.viewers.value" :connected="boardWs.connected.value" />

                    <!-- Filter Toggle Button (for all users) -->
                    <button @click="showFilters = !showFilters"
                        class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition flex items-center gap-2">
                        <FunnelIcon class="w-5 h-5" />
                        <span>{{ t('kanban.filters') }}</span>
                        <span v-if="activeFiltersCount > 0"
                            class="ml-1 px-1.5 py-0.5 bg-brand-600 text-white text-xs rounded-full">
                            {{ activeFiltersCount }}
                        </span>
                    </button>

                    <button v-if="canCreate" @click="openCreateModal"
                        class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition flex items-center gap-2">
                        <PlusIcon class="w-5 h-5" />
                        <span>{{ t('kanban.newTask') }}</span>
                    </button>
                    <button v-if="canCreate" @click="openGroupModal"
                        class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition flex items-center gap-2">
                        <UserGroupIcon class="w-5 h-5" />
                        <span>{{ t('kanban.newGroup') }}</span>
                    </button>
                    <button @click="openListGroupsModal"
                        class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                        </svg>
                        <span>{{ t('kanban.listGroups') }}</span>
                    </button>
                </div>
            </div>

            <!-- Filter Panel -->
            <KanbanFilterPanel :show-filters="showFilters" :is-ptb-admin="authStore.isPtbAdmin"
                :selected-department="selectedDepartment" :selected-employee="selectedEmployee"
                :selected-project="selectedProject" :selected-status="selectedStatus"
                :selected-priority="selectedPriority" :selected-label="selectedLabel" :selected-group="selectedGroup"
                :filter-project-search="filterProjectSearch" :show-filter-project-dropdown="showFilterProjectDropdown"
                :active-filters-count="activeFiltersCount" :sorted-departments="sortedDepartments"
                :sorted-employees="sortedEmployees" :filtered-employees="filteredEmployees"
                :sorted-projects="sortedProjects" :filtered-filter-projects="filteredFilterProjects"
                :task-groups="taskGroups" :get-selected-group-color="getSelectedGroupColor"
                @update:selected-department="selectedDepartment = $event"
                @update:selected-employee="selectedEmployee = $event"
                @update:selected-project="selectedProject = $event" @update:selected-status="selectedStatus = $event"
                @update:selected-priority="handleSelectedPriorityUpdate" @update:selected-label="selectedLabel = $event"
                @update:selected-group="selectedGroup = $event"
                @update:filter-project-search="filterProjectSearch = $event"
                @update:show-filter-project-dropdown="showFilterProjectDropdown = $event"
                @filter-project-blur="handleFilterProjectBlur" @clear-filters="clearFilters" />

            <!-- Loading State -->
            <div v-if="loading" class="flex-1 flex items-center justify-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div>
            </div>

            <!-- Kanban Board -->
            <div v-else class="flex-1 overflow-x-auto overflow-y-hidden pb-4">
                <div class="flex h-full gap-6 min-w-[1000px]">
                    <!-- Columns -->
                    <div v-for="column in columns" :key="column.id"
                        class="flex-1 flex flex-col bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700/50">
                        <!-- Column Header -->
                        <div
                            class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                            <div class="flex items-center gap-2">
                                <div :class="`w-3 h-3 rounded-full ${column.color}`"></div>
                                <h3 class="font-semibold text-gray-700 dark:text-gray-300">{{ column.title }}</h3>
                                <span
                                    class="px-2 py-0.5 bg-gray-200 dark:bg-gray-700 rounded-full text-xs font-medium text-gray-600 dark:text-gray-400">
                                    {{ columnTasksMap[column.id].length }}
                                </span>
                            </div>
                        </div>

                        <!-- Tasks List -->
                        <draggable v-model="columnTasksMap[column.id]" :group="{ name: 'tasks', pull: true, put: true }"
                            item-key="id" class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar min-h-[200px]"
                            :animation="200" ghost-class="opacity-50"
                            @change="(evt: unknown) => onDragChange(evt as { added?: { element: CalendarEvent } }, column.id)">
                            <template #item="{ element: task }">
                                <div :data-task-id="task.id" @click.self="openTaskDetail(task)" :class="[
                                    'bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow group relative',
                                    isOverdue(task.end) && task.status !== 'done' ? 'border-red-300 dark:border-red-700' :
                                        isDueSoon(task.end) && task.status !== 'done' ? 'border-orange-300 dark:border-orange-700' :
                                            'border-gray-200 dark:border-gray-700',
                                    getTaskEditingIndicator(task.id),
                                    task.group ? 'border-l-4' : ''
                                ]" :style="task.group_color ? { borderLeftColor: task.group_color } : {}">

                                    <!-- Someone editing indicator -->
                                    <div v-if="isTaskBeingEdited(task.id)"
                                        class="absolute -top-2 -right-2 flex items-center gap-0.5 z-10">
                                        <div v-for="editor in getTaskEditors(task.id).slice(0, 3)" :key="editor.user_id"
                                            class="w-6 h-6 rounded-full bg-yellow-400 text-yellow-900 text-[10px] font-medium flex items-center justify-center ring-2 ring-white dark:ring-gray-800 shadow-sm -ml-1 first:ml-0"
                                            :title="editor.user_name + ' ' + t('kanban.isEditing')">
                                            {{ getInitials(editor.user_name || 'U') }}
                                        </div>
                                        <span v-if="getTaskEditors(task.id).length > 3"
                                            class="w-6 h-6 rounded-full bg-yellow-300 text-yellow-900 text-[10px] font-medium flex items-center justify-center ring-2 ring-white dark:ring-gray-800 shadow-sm -ml-1">
                                            +{{ getTaskEditors(task.id).length - 3 }}
                                        </span>
                                    </div>

                                    <!-- Overdue/Due Soon Indicator -->
                                    <div v-if="task.status !== 'done' && (isOverdue(task.end) || isDueSoon(task.end))"
                                        :class="[
                                            'absolute top-0 left-0 right-0 h-1 rounded-t-lg',
                                            isOverdue(task.end) ? 'bg-red-500' : 'bg-orange-500'
                                        ]">
                                    </div>

                                    <!-- Task Actions -->
                                    <div :class="[
                                        'absolute right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1 z-10',
                                        task.status !== 'done' && (isOverdue(task.end) || isDueSoon(task.end)) ? 'top-3' : 'top-2'
                                    ]">
                                        <button v-if="canUpdate" @click="editTask(task)"
                                            class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-500 bg-white/80 dark:bg-gray-800/80 shadow-sm">
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                                stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                                                <path stroke-linecap="round" stroke-linejoin="round"
                                                    d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125" />
                                            </svg>
                                        </button>
                                        <button v-if="canDelete" @click="deleteTask(task.id!)"
                                            class="p-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded text-red-500 bg-white/80 dark:bg-gray-800/80 shadow-sm">
                                            <TrashIcon class="w-4 h-4" />
                                        </button>
                                    </div>

                                    <!-- Priority & Labels Row with Creator Initials -->
                                    <div class="flex flex-wrap items-center gap-1.5 mb-2">
                                        <!-- Creator Initials -->
                                        <div class="w-5 h-5 rounded-full bg-brand-100 dark:bg-brand-900 text-brand-600 dark:text-brand-300 flex items-center justify-center text-[10px] font-medium flex-shrink-0"
                                            :title="t('kanban.createdBy') + ' ' + (task.employee_name || 'Unknown')">
                                            {{ getInitials(task.employee_name || 'User') }}
                                        </div>

                                        <!-- Priority Badge -->
                                        <span v-if="task.priority && task.priority !== 'medium'"
                                            :class="['px-1.5 py-0.5 text-xs rounded font-medium', getPriorityConfig(task.priority)?.color]"
                                            :title="t('kanban.priorityPrefix') + ' ' + getPriorityConfig(task.priority)?.label">
                                            {{ getPriorityConfig(task.priority)?.icon }} {{
                                                getPriorityConfig(task.priority)?.label }}
                                        </span>

                                        <!-- Project Badge -->
                                        <span v-if="task.project_name"
                                            class="px-1.5 py-0.5 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-xs rounded border border-blue-100 dark:border-blue-800">
                                            {{ task.project_name }}
                                        </span>

                                        <!-- Group Badge -->
                                        <span v-if="task.group_name" class="px-1.5 py-0.5 text-xs rounded border"
                                            :style="{
                                                backgroundColor: (task.group_color || '#6366F1') + '20',
                                                color: task.group_color || '#6366F1',
                                                borderColor: (task.group_color || '#6366F1') + '50'
                                            }" :title="t('kanban.groupPrefix') + ' ' + task.group_name">
                                            {{ task.group_name }}
                                        </span>

                                        <!-- Labels -->
                                        <span v-for="label in (task.labels || []).slice(0, 2)" :key="label"
                                            :class="['px-1.5 py-0.5 text-xs rounded border', getLabelColor(label)]">
                                            {{ label }}
                                        </span>
                                        <span v-if="(task.labels?.length || 0) > 2"
                                            class="px-1.5 py-0.5 text-xs rounded bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                                            +{{ (task.labels?.length || 0) - 2 }}
                                        </span>
                                    </div>

                                    <!-- Task Title -->
                                    <h4 class="font-medium text-gray-900 dark:text-white pr-8 mb-1">{{ task.title }}
                                    </h4>
                                    <p v-if="task.description"
                                        class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
                                        {{ task.description }}
                                    </p>

                                    <!-- Footer info -->
                                    <div
                                        class="flex items-center justify-between mt-2 pt-2 border-t border-gray-100 dark:border-gray-700/50">
                                        <div class="flex items-center gap-2">
                                            <!-- Assignee Avatars (or Creator if no assignees) -->
                                            <div class="flex -space-x-2">
                                                <!-- Show assigned users if any -->
                                                <template v-if="task.assigned_to && task.assigned_to.length > 0">
                                                    <div v-for="empId in (task.assigned_to || []).slice(0, 3)"
                                                        :key="empId"
                                                        class="w-6 h-6 rounded-full bg-emerald-100 dark:bg-emerald-900 text-emerald-600 dark:text-emerald-300 flex items-center justify-center text-xs font-medium ring-2 ring-white dark:ring-gray-800"
                                                        :title="t('kanban.assigned') + ' ' + getEmployeeName(empId)">
                                                        {{ getInitials(getEmployeeName(empId)) }}
                                                    </div>
                                                    <!-- More indicator -->
                                                    <div v-if="(task.assigned_to?.length || 0) > 3"
                                                        class="w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 flex items-center justify-center text-xs font-medium ring-2 ring-white dark:ring-gray-800">
                                                        +{{ (task.assigned_to?.length || 0) - 3 }}
                                                    </div>
                                                </template>
                                                <!-- Show creator avatar if no one is assigned -->
                                                <template v-else>
                                                    <div class="w-6 h-6 rounded-full bg-brand-100 dark:bg-brand-900 text-brand-600 dark:text-brand-300 flex items-center justify-center text-xs font-medium ring-2 ring-white dark:ring-gray-800"
                                                        :title="t('kanban.createdBy') + ' ' + (task.employee_name || 'Unknown')">
                                                        {{ getInitials(task.employee_name || 'User') }}
                                                    </div>
                                                </template>
                                            </div>

                                            <!-- Subtask Progress Indicator -->
                                            <div v-if="task.subtask_count && task.subtask_count > 0"
                                                class="flex items-center gap-1 text-xs"
                                                :class="task.subtask_completed === task.subtask_count ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'"
                                                :title="t('kanban.subtasksLabel') + ' ' + task.subtask_completed + '/' + task.subtask_count + ' ' + t('kanban.completed')">
                                                <CheckIcon class="w-3.5 h-3.5" />
                                                <span>{{ task.subtask_completed }}/{{ task.subtask_count }}</span>
                                            </div>

                                            <!-- Time Tracking Indicator -->
                                            <div v-if="task.estimated_hours || task.actual_hours"
                                                class="flex items-center gap-1 text-xs"
                                                :class="getTimeTrackingClass(task)"
                                                :title="getTimeTrackingTooltip(task)">
                                                <ClockIcon class="w-3.5 h-3.5" />
                                                <span v-if="task.estimated_hours && task.actual_hours">
                                                    {{ formatHours(task.actual_hours) }}/{{
                                                        formatHours(task.estimated_hours) }}h
                                                </span>
                                                <span v-else-if="task.estimated_hours">
                                                    {{ formatHours(task.estimated_hours) }}{{ t('kanban.hEst') }}
                                                </span>
                                                <span v-else-if="task.actual_hours">
                                                    {{ formatHours(task.actual_hours) }}{{ t('kanban.hLogged') }}
                                                </span>
                                            </div>

                                            <!-- Due Date & Time -->
                                            <span :class="['text-xs', getDueDateClass(task.end)]"
                                                :title="task.status !== 'done' && isOverdue(task.end) ? t('kanban.overdue') : task.status !== 'done' && isDueSoon(task.end) ? t('kanban.dueSoon') : ''">
                                                {{ formatDate(task.end) }} - {{ formatTime(task.end) }}
                                                <span v-if="task.status !== 'done' && isOverdue(task.end)"
                                                    class="ml-1 inline-flex items-center">
                                                    <WarningIcon class="w-3.5 h-3.5" />
                                                </span>
                                                <span v-else-if="task.status !== 'done' && isDueSoon(task.end)"
                                                    class="ml-1 inline-flex items-center">
                                                    <AlarmIcon class="w-3.5 h-3.5" />
                                                </span>
                                            </span>
                                        </div>

                                        <!-- Activity Feed Button -->
                                        <div class="flex gap-1">
                                            <button @click.stop="openTaskDetail(task)"
                                                class="text-xs px-2 py-0.5 rounded bg-brand-50 text-brand-600 hover:bg-brand-100 dark:bg-brand-900/30 dark:text-brand-300 flex items-center gap-1"
                                                title="Open Activity Feed">
                                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor"
                                                    viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                                </svg>
                                                {{ t('kanban.activity') }}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </template>

                            <!-- Empty State -->
                            <template #footer>
                                <div v-if="columnTasksMap[column.id].length === 0"
                                    class="h-24 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg flex items-center justify-center text-gray-400 text-sm">
                                    {{ t('kanban.dropTasksHere') }}
                                </div>
                            </template>
                        </draggable>
                    </div>
                </div>
            </div>
        </div>

        <!-- Create/Edit Modal -->
        <div v-if="showModal" class="fixed inset-0 bg-black/50 z-[100000] flex items-center justify-center p-4"
            @click.self="closeModal">
            <div role="dialog" aria-modal="true" aria-labelledby="kanban-task-modal-title"
                class="bg-white dark:bg-gray-800 w-full max-w-lg max-h-[90vh] rounded-xl shadow-xl flex flex-col">
                <h3 id="kanban-task-modal-title"
                    class="text-lg font-bold text-gray-900 dark:text-white p-6 pb-4 border-b border-gray-200 dark:border-gray-700">
                    {{ isEditing ? t('kanban.editTask') : t('kanban.newTask') }}
                </h3>

                <form @submit.prevent="saveTask" class="flex-1 overflow-y-auto p-6 space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                            t('kanban.title')
                            }}</label>
                        <input v-model="form.title" type="text" required
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white" />
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                            t('kanban.description') }}</label>
                        <textarea v-model="form.description" rows="3"
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"></textarea>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                                t('kanban.status')
                                }}</label>
                            <select v-model="form.status"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
                                <option value="todo">{{ t('kanban.todo') }}</option>
                                <option value="in_progress">{{ t('kanban.inProgress') }}</option>
                                <option value="done">{{ t('kanban.done') }}</option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                                t('kanban.priority') }}</label>
                            <select v-model="form.priority"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
                                <option value="low">{{ t('kanban.low') }}</option>
                                <option value="medium">{{ t('kanban.medium') }}</option>
                                <option value="high">{{ t('kanban.high') }}</option>
                                <option value="urgent">{{ t('kanban.urgent') }}</option>
                            </select>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                                t('kanban.dueDate') }}</label>
                            <flat-pickr v-model="form.end" :config="datePickerConfig"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white cursor-pointer"
                                :placeholder="t('kanban.selectDueDate')" required />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                                t('kanban.dueTime') }}</label>
                            <flat-pickr v-model="form.end_time" :config="timePickerConfig"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white cursor-pointer"
                                :placeholder="t('kanban.selectTime')" />
                        </div>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{
                            t('kanban.project')
                            }}</label>
                        <!-- Selected Project Badge -->
                        <div v-if="form.project && !projectDropdownFocused" class="mb-2">
                            <span
                                class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium">
                                <FolderIcon class="w-4 h-4" />
                                {{sortedProjects.find(p => p.id === form.project)?.name}}
                                <button type="button" @click="form.project = null"
                                    class="ml-1 hover:text-blue-900 dark:hover:text-blue-100">
                                    ✕
                                </button>
                            </span>
                        </div>
                        <!-- Searchable Project Dropdown -->
                        <div class="relative" @mouseenter="projectDropdownHovered = true"
                            @mouseleave="projectDropdownHovered = false">
                            <input v-model="projectModalSearch" type="text"
                                :placeholder="form.project ? t('kanban.changeProject') : t('kanban.searchProjectsPlaceholder')"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                                @focus="projectDropdownFocused = true; showProjectDropdown = true"
                                @blur="handleProjectDropdownBlur" />
                            <div v-if="showProjectDropdown && (projectDropdownFocused || projectDropdownHovered)"
                                class="absolute z-50 w-full max-h-48 overflow-y-auto bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg mt-1">
                                <button type="button" @mousedown.prevent="form.project = null; closeProjectDropdown()"
                                    :class="['w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700', form.project === null ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300' : '']">
                                    {{ t('kanban.noProject') }}
                                </button>
                                <button v-for="proj in filteredModalProjects" :key="proj.id" type="button"
                                    @mousedown.prevent="form.project = proj.id; closeProjectDropdown()"
                                    :class="['w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700', form.project === proj.id ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300' : '']">
                                    {{ proj.name }}
                                </button>
                                <p v-if="filteredModalProjects.length === 0 && projectModalSearch"
                                    class="text-center text-gray-400 text-sm py-2">
                                    {{ t('kanban.noProjectsFound') }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Labels Selection -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{
                            t('kanban.labels')
                            }}</label>
                        <div class="flex flex-wrap gap-2">
                            <button v-for="label in availableLabels" :key="label.name" type="button"
                                @click="toggleLabel(label.name)" :class="[
                                    'px-3 py-1.5 text-sm rounded-full border transition-colors',
                                    form.labels.includes(label.name)
                                        ? label.activeClass
                                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:border-gray-400'
                                ]">
                                {{ label.name }}
                            </button>
                        </div>
                    </div>

                    <!-- Group Selection -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{
                            t('kanban.group')
                            }}</label>
                        <select v-model="form.group"
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm">
                            <option :value="null">{{ t('kanban.noGroup') }}</option>
                            <option v-for="group in taskGroups" :key="group.id" :value="group.id">
                                {{ group.name }} ({{ group.members.length }} {{ t('kanban.members') }})
                            </option>
                        </select>
                    </div>

                    <!-- Estimated Hours (Optional) -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            {{ t('kanban.estimatedHours') }} <span class="text-gray-400 font-normal">({{
                                t('common.optional')
                                }})</span>
                        </label>
                        <div class="flex items-center gap-2">
                            <input v-model.number="form.estimated_hours" type="number" min="0" step="0.5"
                                :placeholder="t('kanban.egHours')"
                                class="w-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm" />
                            <span class="text-sm text-gray-500 dark:text-gray-400">{{ t('kanban.hours') }}</span>
                        </div>
                        <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            <LightbulbIcon class="w-3.5 h-3.5 inline" /> {{ t('kanban.timeBudgetHint') }}
                        </p>
                    </div>

                    <!-- Assignees Selection -->
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{
                                t('kanban.assignTo')
                                }}</label>
                            <div class="flex gap-2">
                                <button type="button" @click="selectAllAssignees"
                                    class="text-xs text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300">
                                    {{ t('common.selectAll') }}
                                </button>
                                <span class="text-gray-300 dark:text-gray-600">|</span>
                                <button type="button" @click="deselectAllAssignees"
                                    class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                                    {{ t('common.deselectAll') }}
                                </button>
                            </div>
                        </div>
                        <!-- Assignee Search -->
                        <input v-model="assigneeModalSearch" type="text" :placeholder="t('kanban.searchEmployees')"
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white mb-2 text-sm" />
                        <div
                            class="max-h-36 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-lg p-2 space-y-1">
                            <button v-for="emp in filteredModalEmployees" :key="emp.id" type="button"
                                @click="toggleAssignee(emp.id)" :class="[
                                    'w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left text-sm transition-colors',
                                    form.assigned_to.includes(emp.id)
                                        ? 'bg-brand-50 dark:bg-brand-900/30 border border-brand-300 dark:border-brand-700 text-brand-700 dark:text-brand-300'
                                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                                ]">
                                <div :class="[
                                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                                    form.assigned_to.includes(emp.id)
                                        ? 'bg-brand-200 dark:bg-brand-800 text-brand-700 dark:text-brand-300'
                                        : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                                ]">
                                    {{ getInitials(emp.name) }}
                                </div>
                                <span class="flex-1 truncate">{{ emp.name }}</span>
                                <svg v-if="form.assigned_to.includes(emp.id)" xmlns="http://www.w3.org/2000/svg"
                                    class="w-4 h-4 text-brand-600" fill="none" viewBox="0 0 24 24"
                                    stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M5 13l4 4L19 7" />
                                </svg>
                            </button>
                            <p v-if="filteredModalEmployees.length === 0"
                                class="text-center text-gray-400 text-sm py-2">
                                {{ assigneeModalSearch ? t('kanban.noEmployeesFound') : t('kanban.noEmployeesAvailable')
                                }}
                            </p>
                        </div>
                        <p v-if="form.assigned_to.length > 0" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {{ form.assigned_to.length }} {{ t('kanban.assigneesSelected') }}
                        </p>
                    </div>
                </form>

                <!-- Modal Footer (Outside scrollable area) -->
                <div class="flex justify-end gap-3 p-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button type="button" @click="closeModal"
                        class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg">{{
                            t('common.cancel') }}</button>
                    <button @click="saveTask" class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700">{{
                        t('kanban.saveTask') }}</button>
                </div>
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <div v-if="showDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
            <div class="absolute inset-0 bg-black/50" @click="cancelDelete"></div>
            <div role="dialog" aria-modal="true" aria-labelledby="kanban-delete-modal-title"
                class="rounded-2xl border border-gray-200 bg-white p-6 w-full max-w-md dark:border-gray-800 dark:bg-gray-900 relative z-10">
                <h2 id="kanban-delete-modal-title" class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    {{ t('kanban.confirmDelete') }}
                </h2>
                <p class="text-gray-700 dark:text-gray-300 mb-6">
                    {{ t('kanban.deleteTaskMsg') }}
                </p>
                <div class="flex gap-3">
                    <button @click="cancelDelete" type="button"
                        class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                        {{ t('common.cancel') }}
                    </button>
                    <button @click="confirmDeleteTask"
                        class="h-11 flex-1 rounded-lg bg-error-600 px-4 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 focus:outline-hidden focus:ring-3 focus:ring-error-500/20">
                        {{ t('common.delete') }}
                    </button>
                </div>
            </div>
        </div>

        <!-- Group Modals -->
        <KanbanGroupModals :show-group-modal="showGroupModal" :show-list-groups-modal="showListGroupsModal"
            :list-groups-tab="listGroupsTab" :editing-group="editingGroupTask" :syncing-departments="syncingDepartments"
            :task-groups="taskGroups" :group-form="groupForm" :edit-group-form="editGroupForm"
            :group-member-search="groupMemberSearch" :filtered-group-members="filteredGroupMembers"
            :all-employees="sortedEmployees" :get-employee-name="getEmployeeName" @close-group-modal="closeGroupModal"
            @save-group="saveGroup" @close-list-groups-modal="closeListGroupsModal" @open-group-modal="openGroupModal"
            @sync-department-groups="syncDepartmentGroups" @start-edit-group="startEditGroup"
            @delete-group="deleteGroup" @cancel-edit-group="cancelEditGroup" @save-edit-group="saveEditGroup"
            @update:list-groups-tab="handleListGroupsTabUpdate"
            @update:group-member-search="groupMemberSearch = $event" />

        <!-- Task Detail Drawer (Comments & Activity) -->
        <TaskDetailDrawer :task="selectedTask" :is-open="showTaskDetail" @close="closeTaskDetail" />
    </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useI18n } from 'vue-i18n'
import draggable from 'vuedraggable'
import KanbanFilterPanel from '@/components/kanban/KanbanFilterPanel.vue'
import KanbanGroupModals from '@/components/kanban/KanbanGroupModals.vue'
import PresenceIndicator from '@/components/kanban/PresenceIndicator.vue'
import TaskDetailDrawer from '@/components/kanban/TaskDetailDrawer.vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import {
	availableLabels,
	columns,
	formatDate,
	formatHours,
	formatTime,
	getDueDateClass,
	getInitials,
	getLabelColor,
	getPriorityConfig,
	getTimeTrackingClass,
	getTimeTrackingTooltip,
	isDueSoon,
	isOverdue,
	useKanbanFilters,
	useKanbanGroups,
	useKanbanTasks,
	useKanbanWebSocket,
} from '@/composables/kanban'
import { useFlatpickrScroll } from '@/composables/useFlatpickrScroll'
import { usePagePermission } from '@/composables/usePagePermission'
import {
	AlarmIcon,
	CheckIcon,
	ClockIcon,
	FolderIcon,
	FunnelIcon,
	LightbulbIcon,
	PlusIcon,
	TrashIcon,
	UserGroupIcon,
	WarningIcon,
} from '@/icons'
import type { CalendarEvent } from '@/services/api/calendar'
import type { Project } from '@/services/api/project'
import type { TaskGroup } from '@/services/api/task'
import { useBoardWebSocket } from '@/services/websocket'
import { useAuthStore } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import { useEmployeeStore } from '@/stores/employee'

const authStore = useAuthStore()
const { t } = useI18n()
const employeeStore = useEmployeeStore()
const departmentStore = useDepartmentStore()
const { canCreate, canUpdate, canDelete } = usePagePermission('kanban')

// WebSocket connection
const boardWs = useBoardWebSocket()

// ── Core Data ────────────────────────────────────────────────────────
const loading = ref(false)
const events = ref<CalendarEvent[]>([])
const projects = ref<Project[]>([])
const taskGroups = ref<TaskGroup[]>([])

// ── Composables ──────────────────────────────────────────────────────
const {
	selectedProject,
	selectedEmployee,
	selectedDepartment,
	selectedStatus,
	showFilters,
	selectedLabel,
	selectedPriority,
	selectedGroup,
	filterProjectSearch,
	showFilterProjectDropdown,
	currentUserEmployeeId,
	userGroupIds,
	sortedProjects,
	sortedEmployees,
	sortedDepartments,
	filteredEmployees,
	filteredFilterProjects,
	activeFiltersCount,
	columnTasksMap,
	clearFilters,
	handleFilterProjectBlur,
} = useKanbanFilters(events, projects, taskGroups)

const {
	showModal,
	isEditing,
	editingId,
	showDeleteModal,
	taskToDelete,
	showTaskDetail,
	selectedTask,
	form,
	projectModalSearch,
	assigneeModalSearch,
	showProjectDropdown,
	projectDropdownFocused,
	projectDropdownHovered,
	filteredModalProjects,
	filteredModalEmployees,
	fetchTasks,
	fetchProjects,
	fetchTaskGroups,
	openTaskDetail,
	closeTaskDetail,
	openCreateModal,
	editTask,
	closeModal,
	saveTask,
	deleteTask,
	confirmDeleteTask,
	cancelDelete,
	onDragChange,
	toggleLabel,
	toggleAssignee,
	selectAllAssignees,
	deselectAllAssignees,
	handleProjectDropdownBlur,
	closeProjectDropdown,
	getEmployeeName,
	getSelectedGroupColor,
} = useKanbanTasks(
	events,
	projects,
	taskGroups,
	boardWs,
	sortedEmployees,
	sortedProjects,
	selectedGroup,
)

const {
	showGroupModal,
	groupForm,
	groupMemberSearch,
	openGroupModal,
	closeGroupModal,
	filteredGroupMembers,
	toggleGroupMember,
	selectAllGroupMembers,
	deselectAllGroupMembers,
	saveGroup,
	showListGroupsModal,
	listGroupsTab,
	editingGroup,
	editGroupForm,
	syncingDepartments,
	openListGroupsModal,
	closeListGroupsModal,
	startEditGroup,
	cancelEditGroup,
	toggleEditGroupMember,
	saveEditGroup,
	deleteGroup,
	syncDepartmentGroups,
} = useKanbanGroups(taskGroups, sortedEmployees)

const editingGroupTask = computed<TaskGroup | null>(() => {
	return taskGroups.value.find((group) => group.id === editingGroup.value) ?? null
})

const {
	setupWebSocket,
	isTaskBeingEdited,
	getTaskEditorName,
	getTaskEditors,
	getTaskEditingIndicator,
} = useKanbanWebSocket(events, boardWs)

const handleSelectedPriorityUpdate = (value: string | null) => {
	if (
		value === 'low' ||
		value === 'medium' ||
		value === 'high' ||
		value === 'urgent' ||
		value === null
	) {
		selectedPriority.value = value
	}
}

const handleListGroupsTabUpdate = (value: string) => {
	if (value === 'all' || value === 'edit') {
		listGroupsTab.value = value
	}
}

// ── Flatpickr Setup (UI-specific, stays in component) ───────────────
const { flatpickrInstances, attachMonthScroll, attachTimeScroll, destroyFlatpickrs } =
	useFlatpickrScroll()

const datePickerConfig = {
	dateFormat: 'Y-m-d',
	altInput: false,
	appendTo: document.body,
	static: false,
	onReady: (
		_selectedDates: unknown,
		_dateStr: string,
		instance: Parameters<typeof attachMonthScroll>[0],
	) => {
		flatpickrInstances.value.push(instance)
		attachMonthScroll(instance)
	},
}

const timePickerConfig = {
	enableTime: true,
	noCalendar: true,
	dateFormat: 'H:i',
	time_24hr: true,
	minuteIncrement: 5,
	appendTo: document.body,
	static: false,
	scrollInput: true,
	onReady: (
		_selectedDates: unknown,
		_dateStr: string,
		instance: Parameters<typeof attachMonthScroll>[0],
	) => {
		flatpickrInstances.value.push(instance)
		attachTimeScroll(instance)
	},
}

// Lifecycle Hooks
onMounted(async () => {
	loading.value = true
	// Start WebSocket connection immediately (don't wait for data loading)
	setupWebSocket()

	try {
		await Promise.all([
			fetchTasks(),
			fetchProjects(),
			fetchTaskGroups(),
			employeeStore.fetchEmployees(),
			departmentStore.fetchDepartments(),
		])
	} finally {
		loading.value = false
	}
})

onUnmounted(() => {
	boardWs.disconnect()
	destroyFlatpickrs()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.5);
    border-radius: 20px;
}
</style>
