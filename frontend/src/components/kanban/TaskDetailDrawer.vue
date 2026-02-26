<template>
  <!-- Task Detail Drawer/Sidebar -->
  <Transition name="slide-right">
    <div v-if="isOpen" class="fixed inset-0 z-[100001] flex justify-end">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/40" @click="close"></div>

      <!-- Drawer -->
      <div class="relative w-full max-w-xl bg-white dark:bg-gray-900 shadow-2xl flex flex-col h-full">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ t('kanban.taskDetails') }}</h2>
          <button @click="close" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition">
            <XIcon class="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <!-- Task Info -->
        <div v-if="task" class="p-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-start justify-between mb-2">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white">{{ task.title }}</h3>
            <span :class="['px-2 py-1 text-xs rounded-full font-medium', statusClass]">
              {{ statusLabel }}
            </span>
          </div>
          <p v-if="task.description" class="text-gray-600 dark:text-gray-400 text-sm mb-3">
            {{ task.description }}
          </p>

          <!-- Task metadata badges -->
          <div class="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-400 mb-3">
            <span v-if="task.project_name"
              class="bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 px-2 py-1 rounded">
              <FolderIcon class="w-3.5 h-3.5 inline" /> {{ task.project_name }}
            </span>
            <span class="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
              <CalenderIcon class="w-3.5 h-3.5" /> {{ t('kanban.dueBadge') }} {{ formatDateTime(task.end) }}
            </span>
            <span v-if="task.priority" :class="['px-2 py-1 rounded', priorityClass]">
              {{ priorityLabel }}
            </span>
            <!-- Time Budget Badge (calculated from dates) -->
            <span v-if="calculatedTimeBudget"
              class="bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 px-2 py-1 rounded flex items-center gap-1"
              :title="timeBudgetTooltip">
              <ClockIcon class="w-3.5 h-3.5" /> {{ calculatedTimeBudget }}
            </span>
            <!-- Manual Estimated Hours (if set) -->
            <span v-if="task.estimated_hours"
              class="bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 px-2 py-1 rounded flex items-center gap-1">
              <BarChartIcon class="w-3.5 h-3.5" /> {{ t('kanban.estBadge') }} {{ task.estimated_hours }}{{ t('kanban.h')
              }}
            </span>
          </div>

          <!-- Creator and Assignees -->
          <div class="space-y-2 text-xs">
            <!-- Created by -->
            <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <span class="font-medium">{{ t('kanban.createdBy') }}</span>
              <div class="flex items-center gap-1">
                <div
                  class="w-5 h-5 rounded-full bg-brand-100 dark:bg-brand-900 text-brand-600 dark:text-brand-300 flex items-center justify-center text-[10px] font-medium">
                  {{ getInitials(task.employee_name) }}
                </div>
                <span>{{ task.employee_name || t('kanban.unknown') }}</span>
              </div>
            </div>

            <!-- Assigned to -->
            <div v-if="task.assigned_to && task.assigned_to.length > 0"
              class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <span class="font-medium">{{ t('kanban.assignedTo') }}</span>
              <div class="flex items-center gap-1 flex-wrap">
                <div v-for="empId in task.assigned_to" :key="empId"
                  class="flex items-center gap-1 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 px-1.5 py-0.5 rounded">
                  <div
                    class="w-4 h-4 rounded-full bg-emerald-200 dark:bg-emerald-800 flex items-center justify-center text-[9px] font-medium">
                    {{ getInitials(getEmployeeName(empId)) }}
                  </div>
                  <span class="text-[11px]">{{ getEmployeeName(empId) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="text-gray-400 dark:text-gray-500 italic">
              {{ t('kanban.noAssignees') }}
            </div>

            <!-- Last updated -->
            <div v-if="task.updated_at" class="text-gray-400 dark:text-gray-500">
              {{ t('kanban.lastUpdated') }} {{ formatDateTime(task.updated_at) }}
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
          <button @click="activeTab = 'comments'" :class="['flex-1 py-3 px-2 text-xs sm:text-sm font-medium transition whitespace-nowrap',
            activeTab === 'comments'
              ? 'text-brand-600 border-b-2 border-brand-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400']">
            <ChatIcon class="w-4 h-4 inline" /> {{ t('kanban.tabComments') }} ({{ comments.length }})
          </button>
          <button @click="activeTab = 'attachments'" :class="['flex-1 py-3 px-2 text-xs sm:text-sm font-medium transition whitespace-nowrap',
            activeTab === 'attachments'
              ? 'text-brand-600 border-b-2 border-brand-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400']">
            <PaperclipIcon class="w-4 h-4 inline" /> {{ t('kanban.tabFiles') }} ({{ attachments.length }})
          </button>
          <button @click="activeTab = 'checklist'" :class="['flex-1 py-3 px-2 text-xs sm:text-sm font-medium transition whitespace-nowrap',
            activeTab === 'checklist'
              ? 'text-brand-600 border-b-2 border-brand-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400']">
            <CheckIcon class="w-4 h-4 inline" /> {{ t('kanban.tabChecklist') }} ({{ subtaskProgress }})
          </button>
          <button @click="activeTab = 'reminders'" :class="['flex-1 py-3 px-2 text-xs sm:text-sm font-medium transition whitespace-nowrap',
            activeTab === 'reminders'
              ? 'text-brand-600 border-b-2 border-brand-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400']">
            <BellIcon class="w-4 h-4 inline" /> {{ t('kanban.tabAlerts') }} ({{ pendingRemindersCount }})
          </button>
          <button @click="activeTab = 'activity'" :class="['flex-1 py-3 px-2 text-xs sm:text-sm font-medium transition whitespace-nowrap',
            activeTab === 'activity'
              ? 'text-brand-600 border-b-2 border-brand-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400']">
            <ClipboardIcon class="w-4 h-4 inline" /> {{ t('kanban.tabActivity') }}
          </button>
          <button @click="activeTab = 'time'" :class="['flex-1 py-3 px-2 text-xs sm:text-sm font-medium transition whitespace-nowrap',
            activeTab === 'time'
              ? 'text-brand-600 border-b-2 border-brand-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400']">
            <ClockIcon class="w-4 h-4 inline" /> {{ t('kanban.tabTime') }}
          </button>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-y-auto">
          <!-- Comments Tab -->
          <div v-if="activeTab === 'comments'" class="p-4 space-y-4">
            <!-- Typing Indicator -->
            <div v-if="typingUsers.length > 0" class="text-xs text-gray-500 dark:text-gray-400 italic">
              {{ typingUsersText }} {{ t('kanban.typing') }}
            </div>

            <!-- Comment List -->
            <div v-if="comments.length === 0" class="text-center py-8 text-gray-400">
              <p>{{ t('kanban.noCommentsYet') }}</p>
            </div>

            <div v-for="comment in comments" :key="comment.id" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 group">
              <div class="flex items-start gap-3">
                <!-- Avatar -->
                <div
                  class="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900 text-brand-600 dark:text-brand-300 flex items-center justify-center text-xs font-medium">
                  {{ getInitials(comment.author_name) }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between mb-1">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-sm text-gray-900 dark:text-white">
                        {{ comment.author_name }}
                      </span>
                      <span class="text-xs text-gray-400" :title="formatFullLocalDateTime(comment.created_at)">{{ timeAgo(comment.created_at) }}</span>
                      <span v-if="comment.is_edited" class="text-xs text-gray-400 italic">{{ t('kanban.edited')
                        }}</span>
                    </div>
                    <!-- Edit/Delete buttons for own comments -->
                    <div v-if="isOwnComment(comment)"
                      class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                      <button @click.stop="startEditComment(comment)"
                        class="p-1 text-gray-400 hover:text-brand-600 text-xs" title="Edit">
                        <PencilIcon class="w-3.5 h-3.5" />
                      </button>
                      <button @click.stop="deleteComment(comment.id)"
                        class="p-1 text-gray-400 hover:text-red-500 text-xs" title="Delete">
                        <TrashIcon class="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <!-- Edit mode for main comment -->
                  <div v-if="editingCommentId === comment.id" class="space-y-2">
                    <textarea v-model="editCommentContent" rows="2"
                      class="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm resize-none focus:outline-none focus:border-brand-500"></textarea>
                    <div class="flex gap-2">
                      <button @click="saveEditComment" :disabled="!editCommentContent.trim()"
                        class="px-2 py-1 bg-brand-600 text-white text-xs rounded hover:bg-brand-700 disabled:opacity-50">
                        {{ t('common.save') }}
                      </button>
                      <button @click="cancelEditComment"
                        class="px-2 py-1 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-xs rounded hover:bg-gray-100 dark:hover:bg-gray-700">
                        {{ t('common.cancel') }}
                      </button>
                    </div>
                  </div>

                  <!-- Normal view -->
                  <p v-if="editingCommentId !== comment.id"
                    class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                    {{ comment.content }}
                  </p>

                  <!-- Replies -->
                  <div v-if="comment.replies?.length > 0"
                    class="mt-3 pl-4 border-l-2 border-gray-200 dark:border-gray-700 space-y-2">
                    <div v-for="reply in comment.replies" :key="reply.id"
                      class="bg-white dark:bg-gray-700 rounded p-2 group/reply">
                      <div class="flex items-center justify-between mb-1">
                        <div class="flex items-center gap-2">
                          <span class="font-medium text-xs text-gray-900 dark:text-white">
                            {{ reply.author_name }}
                          </span>
                          <span class="text-xs text-gray-400">{{ reply.time_ago }}</span>
                          <span v-if="reply.is_edited" class="text-xs text-gray-400 italic">{{ t('kanban.edited')
                            }}</span>
                        </div>
                        <!-- Edit/Delete buttons for own replies -->
                        <div v-if="isOwnComment(reply)"
                          class="flex items-center gap-1 opacity-0 group-hover/reply:opacity-100 transition">
                          <button @click.stop="startEditComment(reply)"
                            class="p-0.5 text-gray-400 hover:text-brand-600 text-[10px]" title="Edit">
                            <PencilIcon class="w-3 h-3" />
                          </button>
                          <button @click.stop="deleteComment(reply.id, comment.id)"
                            class="p-0.5 text-gray-400 hover:text-red-500 text-[10px]" title="Delete">
                            <TrashIcon class="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                      <!-- Edit mode for reply -->
                      <div v-if="editingCommentId === reply.id" class="space-y-2">
                        <textarea v-model="editCommentContent" rows="2"
                          class="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-xs resize-none focus:outline-none focus:border-brand-500"></textarea>
                        <div class="flex gap-2">
                          <button @click="saveEditComment" :disabled="!editCommentContent.trim()"
                            class="px-2 py-0.5 bg-brand-600 text-white text-[10px] rounded hover:bg-brand-700 disabled:opacity-50">
                            {{ t('common.save') }}
                          </button>
                          <button @click="cancelEditComment"
                            class="px-2 py-0.5 border border-gray-300 dark:border-gray-600 text-[10px] rounded hover:bg-gray-100 dark:hover:bg-gray-700">
                            {{ t('common.cancel') }}
                          </button>
                        </div>
                      </div>
                      <p v-else class="text-xs text-gray-600 dark:text-gray-300">{{ reply.content
                      }}</p>
                    </div>
                  </div>

                  <!-- Reply Button -->
                  <button @click="setReplyTo(comment)" class="mt-2 text-xs text-brand-600 hover:text-brand-700">
                    {{ t('kanban.reply') }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Activity Tab -->
          <div v-if="activeTab === 'activity'" class="p-4">
            <div v-if="activities.length === 0" class="text-center py-8 text-gray-400">
              <p>{{ t('kanban.noActivityYet') }}</p>
            </div>

            <div class="relative">
              <!-- Timeline Line -->
              <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

              <div v-for="activity in activities" :key="activity.id" class="relative pl-10 pb-4">
                <!-- Timeline Dot -->
                <div
                  :class="['absolute left-2.5 w-3 h-3 rounded-full border-2 border-white dark:border-gray-900', getActivityColor(activity.action)]">
                </div>

                <div class="text-sm">
                  <span class="font-medium text-gray-900 dark:text-white">{{ activity.actor_name }}</span>
                  <span class="ml-1.5 text-gray-600 dark:text-gray-400">{{ activity.action_display.toLowerCase() }}</span>
                  <span v-if="activity.old_value && activity.new_value" class="ml-1 text-gray-500">
                    {{ t('kanban.from') }} <span class="font-medium">{{ activity.old_value }}</span>
                    {{ t('kanban.to') }} <span class="font-medium">{{ activity.new_value }}</span>
                  </span>
                  <div class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ timeAgo(activity.created_at) }} | {{ formatFullLocalDateTime(activity.created_at) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Time Tracking Tab -->
          <div v-if="activeTab === 'time'" class="p-4 space-y-4">
            <!-- Time Summary Card -->
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">{{ t('kanban.timeSummary') }}</h4>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">{{ t('kanban.estimated') }}</div>
                  <div class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ task?.estimated_hours ? formatHours(task.estimated_hours) + 'h' : t('kanban.notSet') }}
                  </div>
                </div>
                <div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">{{ t('kanban.logged') }}</div>
                  <div class="text-lg font-semibold" :class="getTimeStatusClass()">
                    {{ task?.actual_hours ? formatHours(task.actual_hours) + 'h' : '0h' }}
                  </div>
                </div>
              </div>
              <!-- Progress Bar -->
              <div v-if="task?.estimated_hours" class="mt-3">
                <div class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div class="h-full transition-[width] duration-300" :class="getTimeProgressClass()"
                    :style="{ width: Math.min(timeProgressPercentage, 100) + '%' }">
                  </div>
                </div>
                <div class="text-xs text-gray-500 mt-1 text-right">{{ timeProgressPercentage }}%</div>
              </div>
            </div>

            <!-- Timer Widget -->
            <div class="bg-brand-50 dark:bg-brand-900/20 rounded-lg p-4">
              <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium text-brand-700 dark:text-brand-300">{{ t('kanban.timer') }}</h4>
                <div v-if="activeTimer" class="flex items-center gap-2">
                  <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  <span class="text-xs text-green-600 dark:text-green-400">{{ t('kanban.running') }}</span>
                </div>
              </div>

              <!-- Timer Display -->
              <div class="text-center mb-4">
                <div class="text-3xl font-mono font-bold text-brand-700 dark:text-brand-300">
                  {{ formatTimerDisplay }}
                </div>
                <div v-if="activeTimer" class="text-xs text-gray-500 mt-1">
                  {{ t('kanban.started') }} {{ formatDateTime(activeTimer.started_at) }}
                </div>
              </div>

              <!-- Timer Description (when starting) -->
              <div v-if="!activeTimer" class="mb-3">
                <input v-model="timerDescription" type="text" :placeholder="t('kanban.whatWorking')"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm" />
              </div>

              <!-- Timer Buttons -->
              <div class="flex gap-2">
                <button v-if="!activeTimer" @click="startTimer" :disabled="startingTimer"
                  class="flex-1 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 transition flex items-center justify-center gap-2">
                  <HourglassIcon v-if="startingTimer" class="w-4 h-4" />
                  <PlayIcon v-else class="w-4 h-4" />
                  {{ startingTimer ? t('kanban.starting') : t('kanban.startTimer') }}
                </button>
                <button v-else @click="stopTimer" :disabled="stoppingTimer"
                  class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition flex items-center justify-center gap-2">
                  <HourglassIcon v-if="stoppingTimer" class="w-4 h-4" />
                  <StopIcon v-else class="w-4 h-4" />
                  {{ stoppingTimer ? t('kanban.stopping') : t('kanban.stopTimer') }}
                </button>
              </div>
            </div>

            <!-- Time Logs List -->
            <div>
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">{{ t('kanban.timeEntries') }}</h4>
              <div v-if="timeLogs.length === 0" class="text-center py-8 text-gray-400">
                <p>{{ t('kanban.noTimeLogged') }}</p>
              </div>

              <div v-for="log in timeLogs" :key="log.id" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 mb-2 group">
                <div class="flex items-start justify-between">
                  <div>
                    <div class="text-sm text-gray-900 dark:text-white">
                      {{ log.description || t('kanban.timeLoggedLabel') }}
                    </div>
                    <div class="text-xs text-gray-500 mt-1">
                      <span>{{ formatDateTime(log.started_at) }}</span>
                      <span v-if="log.ended_at"> → {{ formatDateTime(log.ended_at) }}</span>
                    </div>
                    <div class="text-xs text-gray-400 mt-0.5">
                      {{ t('kanban.by') }} {{ log.employee_name }}
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="font-medium text-brand-600 dark:text-brand-400">
                      {{ log.duration_formatted || formatMinutes(log.duration_minutes) }}
                    </div>
                    <button v-if="log.employee === currentUserEmployeeId && !log.is_running"
                      @click="deleteTimeLog(log.id)"
                      class="text-xs text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition mt-1">
                      <TrashIcon class="w-3.5 h-3.5 inline" /> {{ t('kanban.deleteEntry') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Attachments Tab -->
          <div v-if="activeTab === 'attachments'" class="p-4 space-y-3">
            <!-- Upload Button -->
            <div class="mb-4">
              <input ref="fileInput" type="file" class="hidden" @change="handleFileUpload"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.log,.ini,.csv,.json,.xml,.zip,.rar,.7z,.png,.jpg,.jpeg,.gif,.svg,.webp,.bmp" />
              <button @click="triggerFileUpload" :disabled="uploadingFile"
                class="w-full px-4 py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-brand-500 transition flex flex-col items-center justify-center gap-1 text-gray-500 hover:text-brand-600">
                <span v-if="uploadingFile">
                  <HourglassIcon class="w-4 h-4 inline" /> {{ t('kanban.uploadingFile') }}
                </span>
                <template v-else>
                  <PaperclipIcon class="w-5 h-5" />
                  <span>{{ t('kanban.dropFilesOrClick') }}</span>
                  <span class="text-xs text-gray-400">{{ t('kanban.fileTypesHint') }}</span>
                </template>
              </button>
            </div>

            <!-- Attachment List -->
            <div v-if="attachments.length === 0" class="text-center py-8 text-gray-400">
              <p>{{ t('kanban.noAttachments') }}</p>
            </div>

            <div v-for="attachment in attachments" :key="attachment.id"
              class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 flex items-center gap-3 group">
              <!-- File Icon -->
              <component :is="getFileIcon(attachment.file_type)" class="w-6 h-6 flex-shrink-0" />

              <!-- File Info -->
              <div class="flex-1 min-w-0">
                <a :href="attachment.file_url || attachment.file" target="_blank"
                  class="font-medium text-sm text-gray-900 dark:text-white hover:text-brand-600 truncate block">
                  {{ attachment.filename }}
                </a>
                <div class="text-xs text-gray-500 flex items-center gap-2">
                  <span>{{ formatFileSize(attachment.file_size) }}</span>
                  <span v-if="attachment.uploaded_by_name">• {{ attachment.uploaded_by_name }}</span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                <a :href="attachment.file_url || attachment.file" download
                  class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-500 hover:text-gray-700">
                  <DownloadIcon class="w-4 h-4" />
                </a>
                <button @click="deleteAttachment(attachment.id)"
                  class="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-gray-400 hover:text-red-500">
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Checklist Tab -->
          <div v-if="activeTab === 'checklist'" class="p-4 space-y-3">
            <!-- Progress Bar -->
            <div v-if="subtasks.length > 0" class="mb-4">
              <div class="flex items-center justify-between text-sm mb-1">
                <span class="text-gray-600 dark:text-gray-400">{{ t('kanban.progress') }}</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ subtaskProgress }} ({{ subtaskPercentage
                  }}%)</span>
              </div>
              <div class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div class="h-full bg-green-500 transition-[width] duration-300"
                  :style="{ width: subtaskPercentage + '%' }">
                </div>
              </div>
            </div>

            <!-- Add Subtask Input -->
            <div class="flex gap-2 mb-4">
              <input v-model="newSubtaskTitle" type="text" :placeholder="t('kanban.addSubtask')"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                @keyup.enter="addSubtask" />
              <button @click="addSubtask" :disabled="!newSubtaskTitle.trim() || addingSubtask"
                class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm">
                {{ addingSubtask ? '...' : t('common.add') }}
              </button>
            </div>

            <!-- Subtask List -->
            <div v-if="subtasks.length === 0" class="text-center py-8 text-gray-400">
              <p>{{ t('kanban.noSubtasksYet') }}</p>
            </div>

            <div v-for="subtask in subtasks" :key="subtask.id"
              class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 flex items-center gap-3 group">
              <!-- Checkbox -->
              <button @click="toggleSubtask(subtask)" :class="[
                'w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition',
                subtask.is_completed
                  ? 'bg-green-500 border-green-500 text-white'
                  : 'border-gray-300 dark:border-gray-600 hover:border-brand-500'
              ]">
                <span v-if="subtask.is_completed" class="text-xs">✓</span>
              </button>

              <!-- Title or Edit Input -->
              <div class="flex-1 min-w-0">
                <template v-if="editingSubtaskId === subtask.id">
                  <input v-model="editSubtaskTitle" type="text"
                    class="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm"
                    @keyup.enter="saveEditSubtask(subtask)" @keyup.escape="cancelEditSubtask" />
                </template>
                <template v-else>
                  <span :class="[
                    'text-sm',
                    subtask.is_completed
                      ? 'text-gray-400 dark:text-gray-500 line-through'
                      : 'text-gray-900 dark:text-white'
                  ]">
                    {{ subtask.title }}
                  </span>
                  <div v-if="subtask.completed_at" class="text-xs text-gray-400">
                    {{ t('kanban.completedBy') }} {{ subtask.completed_by_name }}
                  </div>
                </template>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                <template v-if="editingSubtaskId === subtask.id">
                  <button @click="saveEditSubtask(subtask)"
                    class="p-1 hover:bg-green-100 dark:hover:bg-green-900/20 rounded text-green-600 text-xs">
                    ✓
                  </button>
                  <button @click="cancelEditSubtask"
                    class="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-500 text-xs">
                    ✕
                  </button>
                </template>
                <template v-else>
                  <button @click="startEditSubtask(subtask)"
                    class="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-400 hover:text-gray-600">
                    <PencilIcon class="w-3.5 h-3.5" />
                  </button>
                  <button @click="deleteSubtask(subtask.id)"
                    class="p-1 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-gray-400 hover:text-red-500">
                    <TrashIcon class="w-3.5 h-3.5" />
                  </button>
                </template>
              </div>
            </div>
          </div>

          <!-- Reminders Tab -->
          <div v-if="activeTab === 'reminders'" class="p-4 space-y-3">
            <!-- Add Reminder Button -->
            <button v-if="!showReminderForm" @click="openReminderForm"
              class="w-full px-4 py-3 bg-brand-50 dark:bg-brand-900/20 text-brand-600 rounded-lg hover:bg-brand-100 transition flex items-center justify-center gap-2">
              <BellIcon class="w-5 h-5" />
              <span>{{ t('kanban.addReminder') }}</span>
            </button>

            <!-- Reminder Form -->
            <div v-if="showReminderForm" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3">
              <h4 class="font-medium text-sm text-gray-900 dark:text-white">{{ t('kanban.newReminder') }}</h4>

              <!-- Reminder Type -->
              <div>
                <label class="block text-xs text-gray-500 mb-1">{{ t('kanban.remindMe') }}</label>
                <select v-model="newReminder.reminder_type" @change="onReminderTypeChange"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm">
                  <option value="15min">{{ t('kanban.min15Before') }}</option>
                  <option value="30min">{{ t('kanban.min30Before') }}</option>
                  <option value="1hour">{{ t('kanban.hour1Before') }}</option>
                  <option value="2hours">{{ t('kanban.hours2Before') }}</option>
                  <option value="1day">{{ t('kanban.day1Before') }}</option>
                  <option value="custom">{{ t('kanban.customTime') }}</option>
                </select>
              </div>

              <!-- Custom Time (when custom selected) -->
              <div v-if="newReminder.reminder_type === 'custom'">
                <label class="block text-xs text-gray-500 mb-1">{{ t('kanban.dateAndTime') }}</label>
                <input type="datetime-local" v-model="newReminder.remind_at"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm" />
              </div>

              <!-- Message -->
              <div>
                <label class="block text-xs text-gray-500 mb-1">{{ t('kanban.messageOptional') }}</label>
                <input type="text" v-model="newReminder.message" :placeholder="t('kanban.reminderNote')"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm" />
              </div>

              <!-- Buttons -->
              <div class="flex gap-2">
                <button @click="showReminderForm = false"
                  class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                  {{ t('common.cancel') }}
                </button>
                <button @click="createReminder" :disabled="creatingReminder"
                  class="flex-1 px-3 py-2 bg-brand-600 text-white rounded-lg text-sm hover:bg-brand-700 disabled:opacity-50 transition">
                  {{ creatingReminder ? t('kanban.creating') : t('common.create') }}
                </button>
              </div>
            </div>

            <!-- Reminder List -->
            <div v-if="reminders.length === 0 && !showReminderForm" class="text-center py-8 text-gray-400">
              <p>{{ t('kanban.noRemindersSet') }}</p>
            </div>

            <div v-for="reminder in reminders" :key="reminder.id"
              :class="['rounded-lg p-3 flex items-start gap-3',
                reminder.is_dismissed
                  ? 'bg-gray-100 dark:bg-gray-800 opacity-50'
                  : reminder.is_triggered
                    ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                    : 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800']">

              <!-- Icon -->
              <BellOffIcon v-if="reminder.is_dismissed" class="w-5 h-5 flex-shrink-0" />
              <SuccessIcon v-else-if="reminder.is_triggered" class="w-5 h-5 flex-shrink-0" />
              <BellIcon v-else class="w-5 h-5 flex-shrink-0" />

              <!-- Info -->
              <div class="flex-1 min-w-0">
                <div class="font-medium text-sm text-gray-900 dark:text-white">
                  {{ reminder.reminder_type_display || reminder.reminder_type }}
                </div>
                <div class="text-xs text-gray-500">
                  {{ formatReminderTime(reminder.remind_at) }}
                </div>
                <div v-if="reminder.message" class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {{ reminder.message }}
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-1">
                <button v-if="!reminder.is_dismissed" @click="dismissReminder(reminder.id)"
                  class="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-xs text-gray-500" title="Dismiss">
                  <BellOffIcon class="w-3.5 h-3.5" />
                </button>
                <button @click="deleteReminder(reminder.id)"
                  class="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-xs text-gray-400 hover:text-red-500"
                  title="Delete">
                  <TrashIcon class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Comment Input (Always visible when on comments tab) -->
        <div v-if="activeTab === 'comments'" class="border-t border-gray-200 dark:border-gray-700 p-4">
          <div v-if="replyingTo" class="mb-2 text-xs text-gray-500 flex items-center gap-2">
            <span>{{ t('kanban.replyingTo') }} {{ replyingTo.author_name }}</span>
            <button @click="cancelReply" class="text-red-500 hover:text-red-600">✕</button>
          </div>

          <!-- @Mentions Dropdown -->
          <div v-if="showMentions"
            class="mb-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-32 overflow-y-auto">
            <button v-for="emp in filteredMentions" :key="emp.id" @click="insertMention(emp)"
              class="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2">
              <div class="w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center text-xs">
                {{ getInitials(emp.name) }}
              </div>
              <span>{{ emp.name }}</span>
            </button>
          </div>

          <div class="flex gap-2">
            <textarea ref="commentInput" v-model="newComment" @input="handleCommentInput"
              @keydown.enter.ctrl="submitComment" :placeholder="t('kanban.addCommentPlaceholder')" rows="2"
              class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm resize-none focus:outline-none focus:border-brand-500">
    </textarea>
            <button @click="submitComment" :disabled="!newComment.trim() || submittingComment"
              class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition self-end">
              {{ submittingComment ? '...' : t('kanban.send') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { type Component, computed, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToast } from '@/composables/useToast'
import {
	ArchiveIcon,
	BarChartIcon,
	BellIcon,
	BellOffIcon,
	CalenderIcon,
	ChatIcon,
	CheckIcon,
	ClipboardIcon,
	ClockIcon,
	DocsIcon,
	DownloadIcon,
	FolderIcon,
	HourglassIcon,
	ImageIcon,
	NotepadIcon,
	PageIcon,
	PaperclipIcon,
	PencilIcon,
	PlayIcon,
	PresentationIcon,
	StopIcon,
	SuccessIcon,
	TrashIcon,
	XIcon,
} from '@/icons'
import {
	type CalendarEvent,
	type ReminderType,
	type TaskActivity,
	type TaskAttachment,
	type TaskComment,
	type TaskGroup,
	type TaskReminder,
	type TaskSubtask,
	type TaskTimeLog,
	taskActivityAPI,
	taskAttachmentAPI,
	taskCommentAPI,
	taskGroupAPI,
	taskReminderAPI,
	taskSubtaskAPI,
	taskTimeLogAPI,
} from '@/services/api'
import { type TaskEditor, useTaskWebSocket } from '@/services/websocket'
import { useAuthStore } from '@/stores/auth'
import { useEmployeeStore } from '@/stores/employee'
import { formatFullLocalDateTime, formatLocalDateTime, timeAgo } from '@/utils/dateTime'

const props = defineProps<{
	task: CalendarEvent | null
	isOpen: boolean
}>()

const emit = defineEmits<{
	close: []
	commentAdded: [comment: TaskComment]
}>()

const employeeStore = useEmployeeStore()
const authStore = useAuthStore()
const { showToast } = useToast()
const { confirm: confirmDialog } = useConfirmDialog()
const { t } = useI18n()

// State
const activeTab = ref<'comments' | 'activity' | 'attachments' | 'reminders' | 'checklist' | 'time'>(
	'comments',
)
const comments = ref<TaskComment[]>([])
const activities = ref<TaskActivity[]>([])
const attachments = ref<TaskAttachment[]>([])
const subtasks = ref<TaskSubtask[]>([])
const reminders = ref<TaskReminder[]>([])
const newComment = ref('')
const submittingComment = ref(false)
const replyingTo = ref<TaskComment | null>(null)
const showMentions = ref(false)
const mentionSearch = ref('')
const commentInput = ref<HTMLTextAreaElement | null>(null)
const typingUsers = ref<TaskEditor[]>([])
const typingTimeout = ref<ReturnType<typeof setTimeout> | null>(null)

// Task group data for mention filtering
const taskGroupData = ref<TaskGroup | null>(null)
const taskGroupFetchToken = ref(0)
const loadedTabByTask = ref<Record<string, Partial<Record<typeof activeTab.value, boolean>>>>({})

// Comment edit state
const editingCommentId = ref<number | null>(null)
const editCommentContent = ref('')

// Attachment state
const fileInput = ref<HTMLInputElement | null>(null)
const uploadingFile = ref(false)

// Subtask/Checklist state
const newSubtaskTitle = ref('')
const addingSubtask = ref(false)
const editingSubtaskId = ref<number | null>(null)
const editSubtaskTitle = ref('')

// Reminder state
const showReminderForm = ref(false)
const newReminder = ref({
	reminder_type: '1hour' as ReminderType,
	remind_at: '',
	message: '',
})
const creatingReminder = ref(false)

// Time Tracking state
const timeLogs = ref<TaskTimeLog[]>([])
const activeTimer = ref<TaskTimeLog | null>(null)
const timerDescription = ref('')
const startingTimer = ref(false)
const stoppingTimer = ref(false)
const timerElapsed = ref(0) // seconds
let timerInterval: ReturnType<typeof setInterval> | null = null

// WebSocket
let taskWs: ReturnType<typeof useTaskWebSocket> | null = null

// Get current user's employee ID
const currentUserEmployeeId = computed(() => {
	const currentUser = authStore.user
	if (!currentUser?.worker_id) return null
	const matchingEmployee = employeeStore.employees.find(
		(emp) => emp.emp_id?.toLowerCase() === currentUser.worker_id?.toLowerCase(),
	)
	return matchingEmployee?.id ?? null
})

// Computed
const statusClass = computed(() => {
	switch (props.task?.status) {
		case 'todo':
			return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
		case 'in_progress':
			return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
		case 'done':
			return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
		default:
			return 'bg-gray-100 text-gray-700'
	}
})

const statusLabel = computed(() => {
	switch (props.task?.status) {
		case 'todo':
			return t('kanban.statusTodo')
		case 'in_progress':
			return t('kanban.statusInProgress')
		case 'done':
			return t('kanban.statusDone')
		default:
			return t('kanban.statusUnknown')
	}
})

const priorityClass = computed(() => {
	switch (props.task?.priority) {
		case 'low':
			return 'bg-gray-100 text-gray-600'
		case 'medium':
			return 'bg-blue-100 text-blue-600'
		case 'high':
			return 'bg-orange-100 text-orange-600'
		case 'urgent':
			return 'bg-red-100 text-red-600'
		default:
			return 'bg-gray-100 text-gray-600'
	}
})

const priorityLabel = computed(() => {
	const labels: Record<string, string> = {
		low: t('kanban.priorityLow'),
		medium: t('kanban.priorityMedium'),
		high: t('kanban.priorityHigh'),
		urgent: t('kanban.priorityUrgent'),
	}
	return labels[props.task?.priority || 'medium'] || t('kanban.priorityMedium')
})

// Calculate time budget from created_at to due date (end)
const calculatedTimeBudget = computed(() => {
	if (!props.task?.created_at || !props.task?.end) return null

	const created = new Date(props.task.created_at)
	const due = new Date(props.task.end)
	const diffMs = due.getTime() - created.getTime()

	if (diffMs <= 0) return null

	const diffHours = diffMs / (1000 * 60 * 60)
	const diffDays = Math.floor(diffHours / 24)
	const remainingHours = Math.floor(diffHours % 24)

	if (diffDays > 0) {
		return remainingHours > 0 ? `${diffDays}d ${remainingHours}h` : `${diffDays}d`
	}
	return `${Math.floor(diffHours)}h`
})

const timeBudgetTooltip = computed(() => {
	if (!props.task?.created_at || !props.task?.end) return ''

	const created = new Date(props.task.created_at)
	const due = new Date(props.task.end)
	const diffMs = due.getTime() - created.getTime()

	if (diffMs <= 0) return t('kanban.taskOverdue')

	const diffHours = diffMs / (1000 * 60 * 60)
	const workingHours = Math.floor(diffHours * 0.33) // Assume ~8h/day work, 33% of calendar time

	return `${t('kanban.timeBudgetTooltip')}\n${t('kanban.calendarTime')} ${calculatedTimeBudget.value}\n${t('kanban.estimatedWorkHours')} ${workingHours}h`
})

const filteredMentions = computed(() => {
	// Determine which employees can be mentioned:
	// - Group tasks: only group members
	// - Non-group tasks: only assigned employees
	let allowedIds = new Set<number>()

	if (props.task?.group) {
		if (!taskGroupData.value) {
			return []
		}
		allowedIds = new Set(taskGroupData.value.members)
	} else {
		allowedIds = new Set(props.task?.assigned_to ?? [])
	}

	let candidates = employeeStore.employees
	candidates = candidates.filter((e) => allowedIds.has(e.id))

	if (!mentionSearch.value) return candidates.slice(0, 5)
	return candidates
		.filter((e) => e.name.toLowerCase().includes(mentionSearch.value.toLowerCase()))
		.slice(0, 5)
})

const typingUsersText = computed(() => {
	const count = typingUsers.value.length
	if (count === 0) return ''
	if (count === 1) {
		const user = typingUsers.value[0]
		return user ? user.user_name + ' ' + t('kanban.isTyping') : ''
	}
	if (count <= 3) {
		const names = typingUsers.value.map((u) => u.user_name)
		const last = names.pop()
		return names.join(', ') + ' ' + t('kanban.and') + ' ' + last + ' ' + t('kanban.areTyping')
	}
	return t('kanban.severalPeopleAre')
})

// Computed for pending reminders count (safe array filter)
const pendingRemindersCount = computed(() => {
	if (!Array.isArray(reminders.value)) return 0
	return reminders.value.filter((r) => !r.is_dismissed).length
})

// Computed for subtask progress display
const subtaskProgress = computed(() => {
	if (!Array.isArray(subtasks.value) || subtasks.value.length === 0) return '0/0'
	const completed = subtasks.value.filter((s) => s.is_completed).length
	return `${completed}/${subtasks.value.length}`
})

// Computed for subtask completion percentage
const subtaskPercentage = computed(() => {
	if (!Array.isArray(subtasks.value) || subtasks.value.length === 0) return 0
	const completed = subtasks.value.filter((s) => s.is_completed).length
	return Math.round((completed / subtasks.value.length) * 100)
})

// Time tracking computed properties
const timeProgressPercentage = computed(() => {
	if (!props.task?.estimated_hours || !props.task?.actual_hours) return 0
	const estimated = Number(props.task.estimated_hours)
	const actual = Number(props.task.actual_hours)
	return Math.round((actual / estimated) * 100)
})

const formatTimerDisplay = computed(() => {
	const totalSeconds = timerElapsed.value
	const hours = Math.floor(totalSeconds / 3600)
	const minutes = Math.floor((totalSeconds % 3600) / 60)
	const seconds = totalSeconds % 60
	return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

function getTaskLoadKey(taskId: number): string {
	return String(taskId)
}

async function ensureTabLoaded(tab: typeof activeTab.value, force = false) {
	const taskId = props.task?.id
	if (!taskId) return

	const key = getTaskLoadKey(taskId)
	const tabState = loadedTabByTask.value[key] ?? {}
	if (!force && tabState[tab]) return

	switch (tab) {
		case 'comments':
			await loadComments()
			break
		case 'activity':
			await loadActivities()
			break
		case 'attachments':
			await loadAttachments()
			break
		case 'reminders':
			await loadReminders()
			break
		case 'checklist':
			await loadSubtasks()
			break
		case 'time':
			await loadTimeLogs()
			break
	}

	loadedTabByTask.value[key] = {
		...(loadedTabByTask.value[key] ?? {}),
		[tab]: true,
	}
}

// Watch for task changes
watch(
	() => props.task,
	async (newTask) => {
		if (newTask?.id) {
			const key = getTaskLoadKey(newTask.id)
			loadedTabByTask.value[key] = {}

			// Fetch task group data for mention filtering
			if (newTask.group) {
				taskGroupFetchToken.value += 1
				const fetchToken = taskGroupFetchToken.value
				taskGroupAPI
					.get(newTask.group)
					.then((g) => {
						if (fetchToken !== taskGroupFetchToken.value || props.task?.id !== newTask.id) return
						taskGroupData.value = g
					})
					.catch(() => {
						if (fetchToken !== taskGroupFetchToken.value || props.task?.id !== newTask.id) return
						taskGroupData.value = null
					})
			} else {
				taskGroupFetchToken.value += 1
				taskGroupData.value = null
			}

			await ensureTabLoaded(activeTab.value, true)
			connectWebSocket()
		}
	},
	{ immediate: true },
)

watch(
	() => activeTab.value,
	async (tab) => {
		await ensureTabLoaded(tab)
	},
)

watch(
	() => props.isOpen,
	(isOpen) => {
		if (!isOpen) {
			disconnectWebSocket()
		}
	},
)

// WebSocket connection
function connectWebSocket() {
	if (!props.task?.id) return

	taskWs = useTaskWebSocket(props.task.id)
	taskWs.connect()

	taskWs.onCommentAdded = (comment: TaskComment) => {
		// Add comment if not already in list
		if (!comments.value.find((c) => c.id === comment.id)) {
			comments.value.push(comment)
		}
	}

	taskWs.onUserTyping = (user, isTyping) => {
		if (isTyping) {
			if (!typingUsers.value.find((u) => u.user_id === user.user_id)) {
				typingUsers.value.push(user)
			}
		} else {
			typingUsers.value = typingUsers.value.filter((u) => u.user_id !== user.user_id)
		}
	}
}

function disconnectWebSocket() {
	taskWs?.disconnect()
	taskWs = null
}

onUnmounted(() => {
	disconnectWebSocket()
	stopTimerInterval()
})

// Data loading
async function loadComments() {
	if (!props.task?.id) return
	try {
		const data = await taskCommentAPI.list(props.task.id)
		comments.value = Array.isArray(data) ? data : []
	} catch (error) {
		console.error('Failed to load comments:', error)
		comments.value = []
	}
}

async function loadActivities() {
	if (!props.task?.id) return
	try {
		const data = await taskActivityAPI.list(props.task.id)
		activities.value = Array.isArray(data) ? data : []
	} catch (error) {
		console.error('Failed to load activities:', error)
		activities.value = []
	}
}

async function loadAttachments() {
	if (!props.task?.id) return
	try {
		const data = await taskAttachmentAPI.byTask(props.task.id)
		attachments.value = Array.isArray(data) ? data : []
	} catch (error) {
		console.error('Failed to load attachments:', error)
		attachments.value = []
	}
}

async function loadReminders() {
	if (!props.task?.id) return
	try {
		const data = await taskReminderAPI.byTask(props.task.id)
		reminders.value = Array.isArray(data) ? data : []
	} catch (error) {
		console.error('Failed to load reminders:', error)
		reminders.value = []
	}
}

async function loadSubtasks() {
	if (!props.task?.id) return
	try {
		const data = await taskSubtaskAPI.list(props.task.id)
		subtasks.value = Array.isArray(data) ? data : []
	} catch (error) {
		console.error('Failed to load subtasks:', error)
		subtasks.value = []
	}
}

// loadGroups removed — groups ref was unused in template (dead code)

// Time Tracking Functions
async function loadTimeLogs() {
	if (!props.task?.id) return
	try {
		const data = await taskTimeLogAPI.list(props.task.id)
		timeLogs.value = Array.isArray(data) ? data : []

		// Check for active timer
		const activeLog = timeLogs.value.find((log) => log.is_running)
		if (activeLog) {
			activeTimer.value = activeLog
			startTimerInterval()
		} else {
			activeTimer.value = null
			stopTimerInterval()
		}
	} catch (error) {
		console.error('Failed to load time logs:', error)
		timeLogs.value = []
	}
}

function startTimerInterval() {
	stopTimerInterval() // Clear any existing interval
	if (activeTimer.value) {
		// Calculate initial elapsed time
		const startTime = new Date(activeTimer.value.started_at).getTime()
		timerElapsed.value = Math.floor((Date.now() - startTime) / 1000)

		// Update every second
		timerInterval = setInterval(() => {
			const startTime = new Date(activeTimer.value!.started_at).getTime()
			timerElapsed.value = Math.floor((Date.now() - startTime) / 1000)
		}, 1000)
	}
}

function stopTimerInterval() {
	if (timerInterval) {
		clearInterval(timerInterval)
		timerInterval = null
	}
	timerElapsed.value = 0
}

async function startTimer() {
	if (!props.task?.id) return
	startingTimer.value = true
	try {
		const newLog = await taskTimeLogAPI.startTimer(props.task.id, timerDescription.value || undefined)
		activeTimer.value = newLog
		timerDescription.value = ''
		await loadTimeLogs()
		startTimerInterval()
		showToast(t('kanban.timerStarted'), 'success')
	} catch (error: unknown) {
		console.error('Failed to start timer:', error)
		showToast(t('kanban.timerStartFailed'), 'error')
	} finally {
		startingTimer.value = false
	}
}

async function stopTimer() {
	if (!activeTimer.value?.id) return
	stoppingTimer.value = true
	try {
		await taskTimeLogAPI.stopTimer(activeTimer.value.id)
		activeTimer.value = null
		stopTimerInterval()
		await loadTimeLogs()
		showToast(t('kanban.timerStopped'), 'success')
	} catch (error: unknown) {
		console.error('Failed to stop timer:', error)
		showToast(t('kanban.timerStopFailed'), 'error')
	} finally {
		stoppingTimer.value = false
	}
}

async function deleteTimeLog(logId: number) {
	const ok = await confirmDialog({
		title: t('kanban.deleteTimeEntry'),
		message: t('kanban.deleteTimeEntryConfirm'),
		type: 'danger',
		confirmLabel: t('common.delete'),
		cancelLabel: t('common.cancel'),
	})
	if (!ok) return
	try {
		await taskTimeLogAPI.delete(logId)
		await loadTimeLogs()
		showToast(t('kanban.timeEntryDeleted'), 'success')
	} catch (error: unknown) {
		console.error('Failed to delete time log:', error)
		showToast(t('kanban.timeEntryDeleteFailed'), 'error')
	}
}

// Format hours for display
function formatHours(hours: number | null | undefined): string {
	if (hours === null || hours === undefined) return '0'
	const num = Number(hours)
	return num % 1 === 0 ? num.toString() : num.toFixed(1)
}

// Format minutes as hours and minutes
function formatMinutes(minutes: number | null | undefined): string {
	if (!minutes) return '0m'
	if (minutes < 60) return `${minutes}m`
	const hours = Math.floor(minutes / 60)
	const mins = minutes % 60
	return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
}

// Get time tracking status class
function getTimeStatusClass(): string {
	if (!props.task?.estimated_hours || !props.task?.actual_hours) {
		return 'text-gray-900 dark:text-white'
	}
	const actual = Number(props.task.actual_hours)
	const estimated = Number(props.task.estimated_hours)
	if (actual > estimated) {
		return 'text-red-600 dark:text-red-400'
	} else if (actual >= estimated * 0.8) {
		return 'text-amber-600 dark:text-amber-400'
	}
	return 'text-green-600 dark:text-green-400'
}

// Get time progress bar class
function getTimeProgressClass(): string {
	if (!props.task?.estimated_hours || !props.task?.actual_hours) {
		return 'bg-brand-500'
	}
	const actual = Number(props.task.actual_hours)
	const estimated = Number(props.task.estimated_hours)
	if (actual > estimated) {
		return 'bg-red-500'
	} else if (actual >= estimated * 0.8) {
		return 'bg-amber-500'
	}
	return 'bg-green-500'
}

// Comment handling
function handleCommentInput() {
	// Check for @ mentions
	const cursorPos = commentInput.value?.selectionStart || 0
	const textBeforeCursor = newComment.value.substring(0, cursorPos)
	const lastAt = textBeforeCursor.lastIndexOf('@')

	if (lastAt !== -1 && !textBeforeCursor.substring(lastAt).includes(' ')) {
		showMentions.value = true
		mentionSearch.value = textBeforeCursor.substring(lastAt + 1)
	} else {
		showMentions.value = false
		mentionSearch.value = ''
	}

	// Send typing indicator
	sendTypingIndicator()
}

function sendTypingIndicator() {
	taskWs?.sendTyping(true)

	// Clear previous timeout
	if (typingTimeout.value) {
		clearTimeout(typingTimeout.value)
	}

	// Set timeout to stop typing indicator
	typingTimeout.value = setTimeout(() => {
		taskWs?.sendTyping(false)
	}, 2000)
}

function insertMention(employee: { id: number; name: string }) {
	const cursorPos = commentInput.value?.selectionStart || newComment.value.length
	const textBeforeCursor = newComment.value.substring(0, cursorPos)
	const lastAt = textBeforeCursor.lastIndexOf('@')

	if (lastAt !== -1) {
		newComment.value =
			newComment.value.substring(0, lastAt) +
			`@${employee.name} ` +
			newComment.value.substring(cursorPos)
	}

	showMentions.value = false
	mentionSearch.value = ''
	commentInput.value?.focus()
}

async function submitComment() {
	if (!newComment.value.trim() || !props.task?.id || submittingComment.value) return

	submittingComment.value = true

	try {
		// Extract mentions from comment
		const mentionRegex = /@([^\s]+)/g
		const mentions: number[] = []
		let match: RegExpExecArray | null = mentionRegex.exec(newComment.value)
		while (match !== null) {
			const matchedName = match[1]
			if (matchedName) {
				const emp = employeeStore.employees.find(
					(e) => e.name.toLowerCase() === matchedName.toLowerCase(),
				)
				if (emp) mentions.push(emp.id)
			}
			match = mentionRegex.exec(newComment.value)
		}

		const comment = await taskCommentAPI.create({
			task: props.task.id,
			content: newComment.value,
			parent: replyingTo.value?.id,
			mentions,
		})

		// Add to local list
		if (replyingTo.value) {
			// Add as reply - search both top-level and nested comments
			const parentId = replyingTo.value.id
			let parent = comments.value.find((c) => c.id === parentId)

			// If not found in top-level, search in nested replies
			if (!parent) {
				for (const topComment of comments.value) {
					if (topComment.replies) {
						const nestedParent = topComment.replies.find((r) => r.id === parentId)
						if (nestedParent) {
							// For reply-to-reply, add to the top-level parent's replies
							parent = topComment
							break
						}
					}
				}
			}

			if (parent) {
				parent.replies = [...(parent.replies || []), comment]
				parent.reply_count++
			} else {
				// Fallback: if no parent found, add as top-level (shouldn't happen normally)
				comments.value.push(comment)
			}
		} else {
			comments.value.push(comment)
		}

		// Notify via WebSocket
		taskWs?.notifyCommentAdded(comment)

		// Emit event
		emit('commentAdded', comment)

		// Reset form
		newComment.value = ''
		replyingTo.value = null
		taskWs?.sendTyping(false)

		showToast(t('kanban.commentAdded'), 'success')
	} catch (error: unknown) {
		console.error('Failed to submit comment:', error)
		const errorMessage = error instanceof Error ? error.message : t('kanban.commentAddFailed')
		showToast(errorMessage, 'error', 5000)
	} finally {
		submittingComment.value = false
	}
}

function setReplyTo(comment: TaskComment) {
	replyingTo.value = comment
	commentInput.value?.focus()
}

function cancelReply() {
	replyingTo.value = null
}

// Attachment handling
function triggerFileUpload() {
	fileInput.value?.click()
}

async function handleFileUpload(event: Event) {
	const target = event.target as HTMLInputElement
	const file = target.files?.[0]
	if (!file || !props.task?.id) return

	// Validate file size (10 MB max)
	const MAX_FILE_SIZE = 10 * 1024 * 1024
	if (file.size > MAX_FILE_SIZE) {
		showToast(t('kanban.fileTooLarge'), 'error')
		if (fileInput.value) fileInput.value.value = ''
		return
	}

	uploadingFile.value = true
	try {
		const attachment = await taskAttachmentAPI.upload(props.task.id, file)
		attachments.value.push(attachment)
		showToast(t('kanban.fileUploaded'), 'success')
	} catch (error: unknown) {
		console.error('Failed to upload file:', error)
		showToast(t('kanban.fileUploadFailed'), 'error')
	} finally {
		uploadingFile.value = false
		// Reset file input
		if (fileInput.value) fileInput.value.value = ''
	}
}

async function deleteAttachment(id: number) {
	const ok = await confirmDialog({
		title: t('kanban.deleteAttachment'),
		message: t('kanban.deleteAttachmentConfirm'),
		type: 'danger',
		confirmLabel: t('common.delete'),
		cancelLabel: t('common.cancel'),
	})
	if (!ok) return
	try {
		await taskAttachmentAPI.delete(id)
		attachments.value = attachments.value.filter((a) => a.id !== id)
		showToast(t('kanban.attachmentDeleted'), 'success')
	} catch (error: unknown) {
		console.error('Failed to delete attachment:', error)
		showToast(t('kanban.attachmentDeleteFailed'), 'error')
	}
}

function formatFileSize(bytes: number): string {
	if (bytes < 1024) return bytes + ' B'
	if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
	return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFileIcon(fileType: string): Component {
	if (fileType.startsWith('image/')) return ImageIcon
	if (fileType.includes('pdf')) return DocsIcon
	if (fileType.includes('word') || fileType.includes('document')) return NotepadIcon
	if (fileType.includes('sheet') || fileType.includes('excel') || fileType.includes('csv'))
		return BarChartIcon
	if (fileType.includes('presentation') || fileType.includes('powerpoint')) return PresentationIcon
	if (
		fileType.includes('zip') ||
		fileType.includes('compressed') ||
		fileType.includes('7z') ||
		fileType.includes('rar')
	)
		return ArchiveIcon
	if (
		fileType.includes('text') ||
		fileType.includes('ini') ||
		fileType.includes('log') ||
		fileType.includes('json') ||
		fileType.includes('xml')
	)
		return PageIcon
	return PaperclipIcon
}

// Reminder handling
function openReminderForm() {
	// Set default remind_at to 1 hour from now
	const defaultTime = new Date()
	defaultTime.setHours(defaultTime.getHours() + 1)
	newReminder.value = {
		reminder_type: '1hour',
		remind_at: defaultTime.toISOString().slice(0, 16),
		message: '',
	}
	showReminderForm.value = true
}

function calculateRemindAt(type: ReminderType): string {
	const taskDue = props.task?.end ? new Date(props.task.end) : new Date()
	switch (type) {
		case '15min':
			taskDue.setMinutes(taskDue.getMinutes() - 15)
			break
		case '30min':
			taskDue.setMinutes(taskDue.getMinutes() - 30)
			break
		case '1hour':
			taskDue.setHours(taskDue.getHours() - 1)
			break
		case '2hours':
			taskDue.setHours(taskDue.getHours() - 2)
			break
		case '1day':
			taskDue.setDate(taskDue.getDate() - 1)
			break
		default:
			return new Date().toISOString().slice(0, 16)
	}
	return taskDue.toISOString().slice(0, 16)
}

function onReminderTypeChange() {
	if (newReminder.value.reminder_type !== 'custom') {
		newReminder.value.remind_at = calculateRemindAt(newReminder.value.reminder_type)
	}
}

async function createReminder() {
	if (!props.task?.id) return

	creatingReminder.value = true
	try {
		const reminder = await taskReminderAPI.create({
			task: props.task.id,
			reminder_type: newReminder.value.reminder_type,
			remind_at: new Date(newReminder.value.remind_at).toISOString(),
			message: newReminder.value.message || undefined,
		})
		reminders.value.push(reminder)
		showReminderForm.value = false
		showToast(t('kanban.reminderCreated'), 'success')
	} catch (error: unknown) {
		console.error('Failed to create reminder:', error)
		showToast(t('kanban.reminderCreateFailed'), 'error')
	} finally {
		creatingReminder.value = false
	}
}

async function dismissReminder(id: number) {
	try {
		await taskReminderAPI.dismiss(id)
		const reminder = reminders.value.find((r) => r.id === id)
		if (reminder) reminder.is_dismissed = true
		showToast(t('kanban.reminderDismissed'), 'success')
	} catch (error: unknown) {
		console.error('Failed to dismiss reminder:', error)
		showToast(t('kanban.reminderDismissFailed'), 'error')
	}
}

async function deleteReminder(id: number) {
	const ok = await confirmDialog({
		title: t('kanban.deleteReminder'),
		message: t('kanban.deleteReminderConfirm'),
		type: 'danger',
		confirmLabel: t('common.delete'),
		cancelLabel: t('common.cancel'),
	})
	if (!ok) return
	try {
		await taskReminderAPI.delete(id)
		reminders.value = reminders.value.filter((r) => r.id !== id)
		showToast(t('kanban.reminderDeleted'), 'success')
	} catch (error: unknown) {
		console.error('Failed to delete reminder:', error)
		showToast(t('kanban.reminderDeleteFailed'), 'error')
	}
}

// Subtask/Checklist handling
async function addSubtask() {
	if (!props.task?.id || !newSubtaskTitle.value.trim()) return
	addingSubtask.value = true
	try {
		const subtask = await taskSubtaskAPI.create({
			task: props.task.id,
			title: newSubtaskTitle.value.trim(),
		})
		subtasks.value.push(subtask)
		newSubtaskTitle.value = ''
		showToast(t('kanban.checklistItemAdded'), 'success')
	} catch (error: unknown) {
		console.error('Failed to add subtask:', error)
		const errorMessage = error instanceof Error ? error.message : t('kanban.checklistAddFailed')
		showToast(errorMessage, 'error', 5000)
	} finally {
		addingSubtask.value = false
	}
}

async function toggleSubtask(subtask: TaskSubtask) {
	try {
		const updated = await taskSubtaskAPI.toggle(subtask.id)
		const index = subtasks.value.findIndex((s) => s.id === subtask.id)
		if (index !== -1) {
			subtasks.value[index] = updated
		}
	} catch (error: unknown) {
		console.error('Failed to toggle subtask:', error)
		showToast(t('kanban.checklistToggleFailed'), 'error')
	}
}

function startEditSubtask(subtask: TaskSubtask) {
	editingSubtaskId.value = subtask.id
	editSubtaskTitle.value = subtask.title
}

function cancelEditSubtask() {
	editingSubtaskId.value = null
	editSubtaskTitle.value = ''
}

async function saveEditSubtask(subtask: TaskSubtask) {
	if (!editSubtaskTitle.value.trim()) return
	try {
		const updated = await taskSubtaskAPI.update(subtask.id, {
			title: editSubtaskTitle.value.trim(),
		})
		const index = subtasks.value.findIndex((s) => s.id === subtask.id)
		if (index !== -1) {
			subtasks.value[index] = updated
		}
		cancelEditSubtask()
		showToast(t('kanban.checklistItemUpdated'), 'success')
	} catch (error: unknown) {
		console.error('Failed to update subtask:', error)
		showToast(t('kanban.checklistUpdateFailed'), 'error')
	}
}

async function deleteSubtask(id: number) {
	try {
		await taskSubtaskAPI.delete(id)
		subtasks.value = subtasks.value.filter((s) => s.id !== id)
		showToast(t('kanban.checklistItemDeleted'), 'success')
	} catch (error: unknown) {
		console.error('Failed to delete subtask:', error)
		showToast(t('kanban.checklistDeleteFailed'), 'error')
	}
}

function formatReminderTime(isoStr: string): string {
	return formatLocalDateTime(isoStr)
}

function close() {
	emit('close')
}

// Helpers
function formatDateTime(dateStr: string) {
	return formatLocalDateTime(dateStr)
}

function getInitials(name: string | undefined | null) {
	if (!name) return '??'
	return name
		.split(' ')
		.map((n) => n[0])
		.join('')
		.toUpperCase()
		.slice(0, 2)
}

// Get employee name by ID
function getEmployeeName(empId: number): string {
	if (!empId) return t('kanban.unknown')

	const emp = employeeStore.employees.find((e) => e.id === empId)
	if (!emp) {
		// Debug: Only log once per unknown employee ID
		console.warn(
			`[TaskDetailDrawer] Employee not found for ID: ${empId}. Store has ${employeeStore.employees.length} employees`,
		)
		return t('kanban.unknown')
	}
	return emp.name
}

// Check if comment belongs to current user
function isOwnComment(comment: TaskComment): boolean {
	const userEmpId = currentUserEmployeeId.value
	if (!userEmpId) return false
	return comment.author === userEmpId
}

// Comment edit functions
function startEditComment(comment: TaskComment) {
	editingCommentId.value = comment.id
	editCommentContent.value = comment.content
}

function cancelEditComment() {
	editingCommentId.value = null
	editCommentContent.value = ''
}

async function saveEditComment() {
	if (!editingCommentId.value || !editCommentContent.value.trim()) return

	try {
		const updated = await taskCommentAPI.update(editingCommentId.value, editCommentContent.value)

		// Update in local list
		const comment = comments.value.find((c) => c.id === editingCommentId.value)
		if (comment) {
			comment.content = updated.content
			comment.is_edited = true
		} else {
			// Check in replies
			for (const parent of comments.value) {
				const reply = parent.replies?.find((r) => r.id === editingCommentId.value)
				if (reply) {
					reply.content = updated.content
					reply.is_edited = true
					break
				}
			}
		}

		cancelEditComment()
		showToast(t('kanban.commentUpdated'), 'success')
	} catch (error: unknown) {
		console.error('Failed to update comment:', error)
		showToast(t('kanban.commentUpdateFailed'), 'error')
	}
}

async function deleteComment(commentId: number, parentId?: number) {
	const ok = await confirmDialog({
		title: t('kanban.deleteComment'),
		message: t('kanban.deleteCommentConfirm'),
		type: 'danger',
		confirmLabel: t('common.delete'),
		cancelLabel: t('common.cancel'),
	})
	if (!ok) return

	try {
		await taskCommentAPI.delete(commentId)

		if (parentId) {
			// Remove from parent replies
			const parent = comments.value.find((c) => c.id === parentId)
			if (parent?.replies) {
				parent.replies = parent.replies.filter((r) => r.id !== commentId)
				parent.reply_count = Math.max(0, (parent.reply_count || 0) - 1)
			}
		} else {
			// Remove from main list
			comments.value = comments.value.filter((c) => c.id !== commentId)
		}
		showToast(t('kanban.commentDeleted'), 'success')
	} catch (error: unknown) {
		console.error('Failed to delete comment:', error)
		showToast(t('kanban.commentDeleteFailed'), 'error')
	}
}

function getActivityColor(action: string) {
	const colors: Record<string, string> = {
		created: 'bg-green-500',
		updated: 'bg-blue-500',
		status_changed: 'bg-purple-500',
		priority_changed: 'bg-orange-500',
		assigned: 'bg-cyan-500',
		unassigned: 'bg-gray-400',
		label_added: 'bg-pink-500',
		label_removed: 'bg-gray-400',
		comment_added: 'bg-brand-500',
		due_date_changed: 'bg-yellow-500',
		moved: 'bg-indigo-500',
	}
	return colors[action] || 'bg-gray-400'
}
</script>

<style scoped>
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
