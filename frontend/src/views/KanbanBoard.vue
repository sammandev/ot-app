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

            <!-- Filter Panel (for all users) -->
            <div v-if="showFilters"
                class="mb-4 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm">
                <div class="flex flex-wrap items-end gap-4">
                    <!-- Department Filter (PTB admins only) -->
                    <div v-if="authStore.isPtbAdmin" class="flex-1 min-w-[200px]">
                        <label
                            class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.department') }}</label>
                        <div class="relative">
                            <select v-model="selectedDepartment"
                                class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                                <option :value="null">{{ t('kanban.allDepartments') }}</option>
                                <option v-for="dept in sortedDepartments" :key="dept.id" :value="dept.id">{{ dept.name
                                    }}</option>
                            </select>
                            <ChevronDownIcon
                                class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <!-- Employee Filter (PTB admins only) -->
                    <div v-if="authStore.isPtbAdmin" class="flex-1 min-w-[200px]">
                        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.employee') }}</label>
                        <div class="relative">
                            <select v-model="selectedEmployee"
                                class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                                <option :value="null">{{ t('kanban.allEmployees') }}</option>
                                <option v-for="emp in filteredEmployees" :key="emp.id" :value="emp.id">{{ emp.name }}
                                </option>
                            </select>
                            <ChevronDownIcon
                                class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <!-- Project Filter (Searchable Dropdown) -->
                    <div class="flex-1 min-w-[200px]">
                        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.project') }}</label>
                        <div class="relative" ref="filterProjectDropdownRef">
                            <input type="text" v-model="filterProjectSearch" @focus="showFilterProjectDropdown = true"
                                @blur="handleFilterProjectBlur"
                                :placeholder="selectedProject ? '' : t('kanban.searchProjects')"
                                class="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:border-brand-500" />

                            <!-- Selected Project Display -->
                            <div v-if="selectedProject && !showFilterProjectDropdown && !filterProjectSearch"
                                class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                                <span class="text-gray-700 dark:text-gray-300 text-sm">
                                    {{sortedProjects.find(p => p.id === selectedProject)?.name}}
                                </span>
                            </div>

                            <ChevronDownIcon class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />

                            <!-- Dropdown -->
                            <div v-if="showFilterProjectDropdown"
                                class="absolute z-50 mt-1 w-full max-h-48 overflow-y-auto bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
                                <button type="button"
                                    @mousedown.prevent="selectedProject = null; showFilterProjectDropdown = false; filterProjectSearch = ''"
                                    :class="['w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700', selectedProject === null ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300' : 'text-gray-700 dark:text-gray-300']">
                                    {{ t('kanban.allProjects') }}
                                </button>
                                <button v-for="proj in filteredFilterProjects" :key="proj.id" type="button"
                                    @mousedown.prevent="selectedProject = proj.id; showFilterProjectDropdown = false; filterProjectSearch = ''"
                                    :class="['w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700', selectedProject === proj.id ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300' : 'text-gray-700 dark:text-gray-300']">
                                    {{ proj.name }}
                                </button>
                                <p v-if="filteredFilterProjects.length === 0 && filterProjectSearch"
                                    class="text-center text-gray-400 text-sm py-2">
                                    {{ t('kanban.noProjectsFound') }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Status Filter -->
                    <div class="flex-1 min-w-[150px]">
                        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.status') }}</label>
                        <div class="relative">
                            <select v-model="selectedStatus"
                                class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                                <option :value="null">{{ t('kanban.allStatuses') }}</option>
                                <option value="todo">{{ t('kanban.todo') }}</option>
                                <option value="in_progress">{{ t('kanban.inProgress') }}</option>
                                <option value="done">{{ t('kanban.done') }}</option>
                            </select>
                            <ChevronDownIcon
                                class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <!-- Priority Filter -->
                    <div class="flex-1 min-w-[140px]">
                        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.priority') }}</label>
                        <div class="relative">
                            <select v-model="selectedPriority"
                                class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                                <option :value="null">{{ t('kanban.allPriorities') }}</option>
                                <option value="low">{{ t('kanban.low') }}</option>
                                <option value="medium">{{ t('kanban.medium') }}</option>
                                <option value="high">{{ t('kanban.high') }}</option>
                                <option value="urgent">{{ t('kanban.urgent') }}</option>
                            </select>
                            <ChevronDownIcon
                                class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <!-- Label Filter -->
                    <div class="flex-1 min-w-[150px]">
                        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.label') }}</label>
                        <div class="relative">
                            <select v-model="selectedLabel"
                                class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                                <option :value="null">{{ t('kanban.allLabels') }}</option>
                                <option v-for="label in availableLabels" :key="label.name" :value="label.name">{{
                                    label.name }}</option>
                            </select>
                            <ChevronDownIcon
                                class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <!-- Group Filter -->
                    <div class="flex-1 min-w-[150px]">
                        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('kanban.group') }}</label>
                        <div class="relative">
                            <select v-model="selectedGroup"
                                class="w-full appearance-none bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-3 pr-8 rounded-lg text-sm focus:outline-none focus:border-brand-500">
                                <option :value="null">{{ t('kanban.allGroups') }}</option>
                                <option v-for="group in taskGroups" :key="group.id" :value="group.id">
                                    {{ group.name }}
                                </option>
                            </select>
                            <ChevronDownIcon
                                class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <!-- Clear Filters Button -->
                    <button v-if="activeFiltersCount > 0" @click="clearFilters"
                        class="px-3 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 transition flex items-center gap-1">
                        <XIcon class="w-4 h-4" />
                        <span>{{ t('common.clear') }}</span>
                    </button>
                </div>

                <!-- Active Filters Summary -->
                <div v-if="activeFiltersCount > 0" class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                    <div class="flex flex-wrap items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                        <span>{{ t('kanban.showingTasksFor') }}</span>
                        <span v-if="authStore.isPtbAdmin && selectedDepartment"
                            class="inline-flex items-center px-2 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded-full text-xs">
                            {{sortedDepartments.find(d => d.id === selectedDepartment)?.name}}
                            <button @click="selectedDepartment = null" class="ml-1 hover:text-purple-900">×</button>
                        </span>
                        <span v-if="authStore.isPtbAdmin && selectedEmployee"
                            class="inline-flex items-center px-2 py-0.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-full text-xs">
                            {{filteredEmployees.find(e => e.id === selectedEmployee)?.name || sortedEmployees.find(e =>
                                e.id === selectedEmployee)?.name}}
                            <button @click="selectedEmployee = null" class="ml-1 hover:text-blue-900">×</button>
                        </span>
                        <span v-if="selectedProject"
                            class="inline-flex items-center px-2 py-0.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-full text-xs">
                            {{sortedProjects.find(p => p.id === selectedProject)?.name}}
                            <button @click="selectedProject = null" class="ml-1 hover:text-green-900">×</button>
                        </span>
                        <span v-if="selectedStatus"
                            class="inline-flex items-center px-2 py-0.5 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 rounded-full text-xs">
                            {{ selectedStatus === 'todo' ? t('kanban.todo') : selectedStatus === 'in_progress' ? t('kanban.inProgress') :
                                t('kanban.done') }}
                            <button @click="selectedStatus = null" class="ml-1 hover:text-orange-900">×</button>
                        </span>
                        <span v-if="selectedPriority"
                            class="inline-flex items-center px-2 py-0.5 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-full text-xs">
                            {{ getPriorityConfig(selectedPriority)?.icon }} {{
                                getPriorityConfig(selectedPriority)?.label }}
                            <button @click="selectedPriority = null" class="ml-1 hover:text-red-900">×</button>
                        </span>
                        <span v-if="selectedLabel"
                            :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs', getLabelColor(selectedLabel)]">
                            {{ selectedLabel }}
                            <button @click="selectedLabel = null" class="ml-1 hover:opacity-75">×</button>
                        </span>
                        <span v-if="selectedGroup" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs"
                            :style="{ backgroundColor: getSelectedGroupColor() + '20', color: getSelectedGroupColor(), borderColor: getSelectedGroupColor() }"
                            style="border-width: 1px;">
                            {{taskGroups.find(g => g.id === selectedGroup)?.name}}
                            <button @click="selectedGroup = null" class="ml-1 hover:opacity-75">×</button>
                        </span>
                    </div>
                </div>
            </div>

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
                                        <div v-for="editor in getTaskEditors(task.id).slice(0, 3)"
                                            :key="editor.user_id"
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
                                                    class="ml-1 inline-flex items-center"><WarningIcon class="w-3.5 h-3.5" /></span>
                                                <span v-else-if="task.status !== 'done' && isDueSoon(task.end)"
                                                    class="ml-1 inline-flex items-center"><AlarmIcon class="w-3.5 h-3.5" /></span>
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
            <div role="dialog" aria-modal="true" aria-labelledby="kanban-task-modal-title" class="bg-white dark:bg-gray-800 w-full max-w-lg max-h-[90vh] rounded-xl shadow-xl flex flex-col">
                <h3 id="kanban-task-modal-title"
                    class="text-lg font-bold text-gray-900 dark:text-white p-6 pb-4 border-b border-gray-200 dark:border-gray-700">
                    {{ isEditing ? t('kanban.editTask') : t('kanban.newTask') }}
                </h3>

                <form @submit.prevent="saveTask" class="flex-1 overflow-y-auto p-6 space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.title') }}</label>
                        <input v-model="form.title" type="text" required
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white" />
                    </div>

                    <div>
                        <label
                            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.description') }}</label>
                        <textarea v-model="form.description" rows="3"
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"></textarea>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.status') }}</label>
                            <select v-model="form.status"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
                                <option value="todo">{{ t('kanban.todo') }}</option>
                                <option value="in_progress">{{ t('kanban.inProgress') }}</option>
                                <option value="done">{{ t('kanban.done') }}</option>
                            </select>
                        </div>

                        <div>
                            <label
                                class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.priority') }}</label>
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
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.dueDate') }}</label>
                            <flat-pickr v-model="form.end" :config="datePickerConfig"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white cursor-pointer"
                                :placeholder="t('kanban.selectDueDate')" required />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.dueTime') }}</label>
                            <flat-pickr v-model="form.end_time" :config="timePickerConfig"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white cursor-pointer"
                                :placeholder="t('kanban.selectTime')" />
                        </div>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.project') }}</label>
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
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('kanban.labels') }}</label>
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
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('kanban.group') }}</label>
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
                            {{ t('kanban.estimatedHours') }} <span class="text-gray-400 font-normal">({{ t('common.optional') }})</span>
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
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('kanban.assignTo') }}</label>
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
                                {{ assigneeModalSearch ? t('kanban.noEmployeesFound') : t('kanban.noEmployeesAvailable') }}
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
                        class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg">{{ t('common.cancel') }}</button>
                    <button @click="saveTask"
                        class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700">{{ t('kanban.saveTask') }}</button>
                </div>
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <div v-if="showDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center">
            <div class="absolute inset-0 bg-black/50" @click="cancelDelete"></div>
            <div
                role="dialog" aria-modal="true" aria-labelledby="kanban-delete-modal-title"
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

        <!-- Create Group Modal -->
        <div v-if="showGroupModal" class="fixed inset-0 bg-black/50 z-[100000] flex items-center justify-center p-4"
            @click.self="closeGroupModal">
            <div
                role="dialog" aria-modal="true" aria-labelledby="kanban-group-modal-title"
                class="bg-white dark:bg-gray-900 rounded-xl w-full max-w-lg border border-gray-200 dark:border-gray-700 flex flex-col max-h-[90vh]">
                <!-- Modal Header -->
                <div class="p-6 pb-4 border-b border-gray-200 dark:border-gray-700">
                    <h2 id="kanban-group-modal-title" class="text-xl font-bold text-gray-900 dark:text-white">{{ t('kanban.createNewGroup') }}</h2>
                </div>

                <!-- Modal Body (Scrollable) -->
                <form @submit.prevent="saveGroup" class="flex-1 overflow-y-auto p-6 pt-4 space-y-4">
                    <!-- Group Name -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.groupNameRequired') }}</label>
                        <input v-model="groupForm.name" type="text" required
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                            :placeholder="t('kanban.enterGroupName')" />
                    </div>

                    <!-- Group Description -->
                    <div>
                        <label
                            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('kanban.description') }}</label>
                        <textarea v-model="groupForm.description" rows="2"
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                            :placeholder="t('kanban.enterGroupDesc')"></textarea>
                    </div>

                    <!-- Group Color with Templates -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('kanban.color') }}</label>
                        <!-- Color Templates -->
                        <div class="grid grid-cols-9 gap-2 mb-3">
                            <button v-for="template in colorTemplates" :key="template.color" type="button"
                                @click="groupForm.color = template.color" :class="[
                                    'w-8 h-8 rounded-lg border-2 transition-[border-color,transform,box-shadow]',
                                    groupForm.color === template.color
                                        ? 'border-gray-900 dark:border-white scale-110 shadow-md'
                                        : 'border-transparent hover:scale-105'
                                ]" :style="{ backgroundColor: template.color }" :title="template.name">
                            </button>
                        </div>
                        <!-- Custom Color Picker -->
                        <div class="flex items-center gap-2">
                            <input v-model="groupForm.color" type="color"
                                class="w-10 h-10 border border-gray-300 dark:border-gray-600 rounded cursor-pointer" />
                            <input v-model="groupForm.color" type="text"
                                class="w-24 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm"
                                placeholder="#6366F1" />
                            <span class="text-xs text-gray-500">{{ t('kanban.custom') }}</span>
                        </div>
                        <!-- Preview -->
                        <div class="mt-3 p-3 rounded-lg border-l-4" :style="{
                            backgroundColor: groupForm.color + '15',
                            borderLeftColor: groupForm.color
                        }">
                            <span class="text-sm font-medium" :style="{ color: groupForm.color }">
                                {{ groupForm.name || t('kanban.groupPreview') }}
                            </span>
                        </div>
                    </div>

                    <!-- Group Members -->
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('kanban.members') }}</label>
                            <div class="flex gap-2">
                                <button type="button" @click="selectAllGroupMembers"
                                    class="text-xs text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300">
                                    {{ t('common.selectAll') }}
                                </button>
                                <span class="text-gray-300 dark:text-gray-600">|</span>
                                <button type="button" @click="deselectAllGroupMembers"
                                    class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                                    {{ t('common.deselectAll') }}
                                </button>
                            </div>
                        </div>
                        <!-- Member Search -->
                        <input v-model="groupMemberSearch" type="text" :placeholder="t('kanban.searchEmployees')"
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white mb-2 text-sm" />
                        <div
                            class="max-h-48 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-lg p-2 space-y-1">
                            <button v-for="emp in filteredGroupMembers" :key="emp.id" type="button"
                                @click="toggleGroupMember(emp.id)" :class="[
                                    'w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left text-sm transition-colors',
                                    groupForm.members.includes(emp.id)
                                        ? 'bg-brand-50 dark:bg-brand-900/30 border border-brand-300 dark:border-brand-700 text-brand-700 dark:text-brand-300'
                                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                                ]">
                                <div :class="[
                                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                                    groupForm.members.includes(emp.id)
                                        ? 'bg-brand-200 dark:bg-brand-800 text-brand-700 dark:text-brand-300'
                                        : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                                ]">
                                    {{ getInitials(emp.name) }}
                                </div>
                                <span class="flex-1 truncate">{{ emp.name }}</span>
                                <span
                                    class="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded">{{
                                    getDepartmentCode(emp.department) }}</span>
                                <svg v-if="groupForm.members.includes(emp.id)" xmlns="http://www.w3.org/2000/svg"
                                    class="w-4 h-4 text-brand-600" fill="none" viewBox="0 0 24 24"
                                    stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M5 13l4 4L19 7" />
                                </svg>
                            </button>
                            <p v-if="filteredGroupMembers.length === 0" class="text-center text-gray-400 text-sm py-2">
                                {{ groupMemberSearch ? t('kanban.noEmployeesFound') : t('kanban.noEmployeesAvailable') }}
                            </p>
                        </div>
                        <p v-if="groupForm.members.length > 0" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {{ groupForm.members.length }} {{ t('kanban.membersSelected') }}
                        </p>
                    </div>
                </form>

                <!-- Modal Footer -->
                <div class="flex justify-end gap-3 p-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button type="button" @click="closeGroupModal"
                        class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg">{{ t('common.cancel') }}</button>
                    <button @click="saveGroup"
                        class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700">{{ t('kanban.createGroup') }}</button>
                </div>
            </div>
        </div>

        <!-- List Groups Modal -->
        <div v-if="showListGroupsModal"
            class="fixed inset-0 bg-black/50 z-[100000] flex items-center justify-center p-4"
            @click.self="closeListGroupsModal">
            <div
                role="dialog" aria-modal="true" aria-labelledby="kanban-groups-list-title"
                class="bg-white dark:bg-gray-900 rounded-xl w-full max-w-3xl border border-gray-200 dark:border-gray-700 flex flex-col max-h-[90vh]">
                <!-- Modal Header -->
                <div class="p-6 pb-4 border-b border-gray-200 dark:border-gray-700">
                    <div class="flex items-center justify-between">
                        <h2 id="kanban-groups-list-title" class="text-xl font-bold text-gray-900 dark:text-white">{{ t('kanban.taskGroups') }}</h2>
                        <div class="flex items-center gap-2">
                            <button @click="syncDepartmentGroups" :disabled="syncingDepartments"
                                class="px-3 py-1.5 text-sm bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition disabled:opacity-50 flex items-center gap-1.5"
                                title="Create/update groups based on departments">
                                <HourglassIcon v-if="syncingDepartments" class="w-4 h-4" />
                                <RefreshIcon v-else class="w-4 h-4" />
                                {{ t('kanban.syncDepartments') }}
                            </button>
                            <button @click="closeListGroupsModal"
                                class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
                                <XIcon class="w-5 h-5 text-gray-500" />
                            </button>
                        </div>
                    </div>
                    <!-- Tabs -->
                    <div class="flex gap-2 mt-4">
                        <button @click="listGroupsTab = 'all'" :class="[
                            'px-4 py-2 rounded-lg text-sm font-medium transition',
                            listGroupsTab === 'all'
                                ? 'bg-brand-600 text-white'
                                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                        ]">
                            {{ t('kanban.allGroups') }} ({{ taskGroups.length }})
                        </button>
                        <button v-if="editingGroup" @click="listGroupsTab = 'edit'" :class="[
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
                            <button @click="closeListGroupsModal(); openGroupModal()"
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
                                    <button v-if="!group.is_department_group" @click="startEditGroup(group)"
                                        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg text-gray-500 hover:text-brand-600"
                                        title="Edit Group">
                                        <PencilIcon class="w-4 h-4" />
                                    </button>
                                    <button v-if="!group.is_department_group" @click="deleteGroup(group.id)"
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
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('kanban.color') }}</label>
                            <!-- Color Templates -->
                            <div class="grid grid-cols-9 gap-2 mb-3">
                                <button v-for="template in colorTemplates" :key="template.color" type="button"
                                    @click="editGroupForm.color = template.color" :class="[
                                        'w-8 h-8 rounded-lg border-2 transition-[border-color,transform,box-shadow]',
                                        editGroupForm.color === template.color
                                            ? 'border-gray-900 dark:border-white scale-110 shadow-md'
                                            : 'border-transparent hover:scale-105'
                                    ]" :style="{ backgroundColor: template.color }" :title="template.name">
                                </button>
                            </div>
                            <!-- Custom Color Picker -->
                            <div class="flex items-center gap-2">
                                <input v-model="editGroupForm.color" type="color"
                                    class="w-10 h-10 border border-gray-300 dark:border-gray-600 rounded cursor-pointer" />
                                <input v-model="editGroupForm.color" type="text"
                                    class="w-24 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm"
                                    placeholder="#6366F1" />
                                <span class="text-xs text-gray-500">{{ t('kanban.custom') }}</span>
                            </div>
                            <!-- Preview -->
                            <div class="mt-3 p-3 rounded-lg border-l-4" :style="{
                                backgroundColor: editGroupForm.color + '15',
                                borderLeftColor: editGroupForm.color
                            }">
                                <span class="text-sm font-medium" :style="{ color: editGroupForm.color }">
                                    {{ editGroupForm.name || t('kanban.groupPreview') }}
                                </span>
                            </div>
                        </div>

                        <!-- Group Members -->
                        <div>
                            <div class="flex items-center justify-between mb-2">
                                <label
                                    class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('kanban.members') }}</label>
                                <div class="flex gap-2">
                                    <button type="button"
                                        @click="editGroupForm.members = sortedEmployees.map(e => e.id)"
                                        class="text-xs text-brand-600 hover:text-brand-700 dark:text-brand-400">
                                        {{ t('common.selectAll') }}
                                    </button>
                                    <span class="text-gray-300 dark:text-gray-600">|</span>
                                    <button type="button" @click="editGroupForm.members = []"
                                        class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400">
                                        {{ t('common.deselectAll') }}
                                    </button>
                                </div>
                            </div>
                            <input v-model="groupMemberSearch" type="text" :placeholder="t('kanban.searchEmployees')"
                                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white mb-2 text-sm" />
                            <div
                                class="max-h-48 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-lg p-2 space-y-1">
                                <button v-for="emp in filteredGroupMembers" :key="emp.id" type="button"
                                    @click="toggleEditGroupMember(emp.id)" :class="[
                                        'w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left text-sm transition-colors',
                                        editGroupForm.members.includes(emp.id)
                                            ? 'bg-brand-50 dark:bg-brand-900/30 border border-brand-300 dark:border-brand-700 text-brand-700 dark:text-brand-300'
                                            : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                                    ]">
                                    <div :class="[
                                        'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                                        editGroupForm.members.includes(emp.id)
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
                                    <svg v-if="editGroupForm.members.includes(emp.id)" class="w-4 h-4 text-brand-600"
                                        fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M5 13l4 4L19 7" />
                                    </svg>
                                </button>
                            </div>
                            <p v-if="editGroupForm.members.length > 0"
                                class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                {{ editGroupForm.members.length }} {{ t('kanban.membersSelected') }}
                            </p>
                        </div>

                        <!-- Edit Actions -->
                        <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                            <button type="button" @click="cancelEditGroup"
                                class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg">
                                {{ t('common.cancel') }}
                            </button>
                            <button @click="saveEditGroup" :disabled="!editGroupForm.name.trim()"
                                class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50">
                                {{ t('kanban.saveChanges') }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Task Detail Drawer (Comments & Activity) -->
        <TaskDetailDrawer :task="selectedTask" :is-open="showTaskDetail" @close="closeTaskDetail" />
    </AdminLayout>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import flatPickr from 'vue-flatpickr-component'
import { useI18n } from 'vue-i18n'
import draggable from 'vuedraggable'
import PresenceIndicator from '@/components/kanban/PresenceIndicator.vue'
import TaskDetailDrawer from '@/components/kanban/TaskDetailDrawer.vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import {
	availableLabels,
	colorTemplates,
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
	priorityConfig,
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
	ChevronDownIcon,
	ClockIcon,
	FolderIcon,
	FunnelIcon,
	HourglassIcon,
	LightbulbIcon,
	LightningIcon,
	PencilIcon,
	PlusIcon,
	RefreshIcon,
	TrashIcon,
	UserGroupIcon,
	WarningIcon,
	XIcon,
} from '@/icons'
import type { CalendarEvent, Project, TaskGroup } from '@/services/api'
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
	filterProjectDropdownRef,
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
	getDepartmentCode,
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

const {
	setupWebSocket,
	isTaskBeingEdited,
	getTaskEditorName,
	getTaskEditors,
	getTaskEditingIndicator,
} = useKanbanWebSocket(events, boardWs)

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

// ── Lifecycle ────────────────────────────────────────────────────────
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
