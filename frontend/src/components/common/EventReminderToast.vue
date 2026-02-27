<template>
    <Teleport to="body">
        <TransitionGroup name="toast-slide" tag="div" class="fixed top-4 right-4 z-[99999] flex flex-col gap-3">
            <div v-for="reminder in visibleReminders" :key="reminder.id" :class="[
                'w-80 rounded-xl border shadow-lg backdrop-blur-sm',
                getToastColorClasses(reminder.type)
            ]">
                <!-- Header -->
                <div class="flex items-start gap-3 p-4">
                    <div
                        :class="['flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full', getIconBgClass(reminder.type)]">
                        <component :is="getIcon(reminder.type)" class="h-5 w-5" />
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between gap-2">
                            <h4 :class="['font-semibold truncate', getTitleClass(reminder.type)]">
                                {{ getReminderTypeLabel(reminder.type) }}
                            </h4>
                            <button @click="dismissReminder(reminder.eventId)"
                                class="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors">
                                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                                    stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <p class="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
                            {{ reminder.message }}
                        </p>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {{ formatEventTime(reminder.eventTime) }}
                        </p>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-2 border-t border-gray-200 dark:border-gray-700 px-4 py-3">
                    <button @click="dismissReminder(reminder.eventId)"
                        class="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                        Don't Remind Me
                    </button>

                    <button @click="snoozeReminder(reminder.eventId, 30)"
                        class="flex-1 flex items-center justify-center gap-1 rounded-lg border border-brand-300 bg-brand-50 px-3 py-2 text-xs font-medium text-brand-700 shadow-sm transition hover:bg-brand-100 dark:border-brand-600 dark:bg-brand-900/30 dark:text-brand-300 dark:hover:bg-brand-900/50">
                        <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Remind me in 30 minutes
                    </button>
                </div>
            </div>
        </TransitionGroup>
    </Teleport>
</template>

<script setup lang="ts">
import { computed, h, onMounted, onUnmounted, ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { type ReminderItem, useReminderStore } from '@/stores/reminder';

defineOptions({
  name: 'EventReminderToast',
});

const reminderStore = useReminderStore();
const autoDismissTimers = ref<Map<number, ReturnType<typeof setTimeout>>>(
  new Map(),
);
let stopAuthWatch: (() => void) | null = null;

const visibleReminders = computed(() =>
  reminderStore.activeReminders.slice(0, 3),
);

// Auto-dismiss reminders after 10 seconds
const startAutoDismissTimer = (eventId: number) => {
  // Clear any existing timer for this event
  if (autoDismissTimers.value.has(eventId)) {
    clearTimeout(autoDismissTimers.value.get(eventId)!);
  }
  // Set new timer
  const timer = setTimeout(() => {
    reminderStore.dismissReminder(eventId);
    autoDismissTimers.value.delete(eventId);
  }, 10000); // 10 seconds
  autoDismissTimers.value.set(eventId, timer);
};

// Watch for new reminders and start auto-dismiss timers
watch(
  () => visibleReminders.value,
  (newReminders, oldReminders) => {
    const oldIds = new Set((oldReminders || []).map((r) => r.eventId));
    newReminders.forEach((reminder) => {
      if (!oldIds.has(reminder.eventId)) {
        startAutoDismissTimer(reminder.eventId);
      }
    });
  },
  { immediate: true },
);

// Cleanup timers and polling on unmount
onUnmounted(() => {
  autoDismissTimers.value.forEach((timer) => clearTimeout(timer));
  autoDismissTimers.value.clear();
  if (stopAuthWatch) {
    stopAuthWatch();
    stopAuthWatch = null;
  }
  reminderStore.stopPolling();
});

const dismissReminder = (eventId: number) => {
  // Clear auto-dismiss timer when manually dismissed
  if (autoDismissTimers.value.has(eventId)) {
    clearTimeout(autoDismissTimers.value.get(eventId)!);
    autoDismissTimers.value.delete(eventId);
  }
  reminderStore.dismissReminder(eventId);
};

const snoozeReminder = (eventId: number, minutes: number) => {
  // Clear auto-dismiss timer when snoozed
  if (autoDismissTimers.value.has(eventId)) {
    clearTimeout(autoDismissTimers.value.get(eventId)!);
    autoDismissTimers.value.delete(eventId);
  }
  reminderStore.snoozeReminder(eventId, minutes);
};

const getToastColorClasses = (type: ReminderItem['type']) => {
  switch (type) {
    case 'meeting':
      return 'border-blue-200 bg-blue-50/95 dark:border-blue-800 dark:bg-blue-900/90';
    case 'task':
      return 'border-emerald-200 bg-emerald-50/95 dark:border-emerald-800 dark:bg-emerald-900/90';
    case 'due_date':
      return 'border-orange-200 bg-orange-50/95 dark:border-orange-800 dark:bg-orange-900/90';
    default:
      return 'border-purple-200 bg-purple-50/95 dark:border-purple-800 dark:bg-purple-900/90';
  }
};

const getIconBgClass = (type: ReminderItem['type']) => {
  switch (type) {
    case 'meeting':
      return 'bg-blue-500 text-white';
    case 'task':
      return 'bg-emerald-500 text-white';
    case 'due_date':
      return 'bg-orange-500 text-white';
    default:
      return 'bg-purple-500 text-white';
  }
};

const getTitleClass = (type: ReminderItem['type']) => {
  switch (type) {
    case 'meeting':
      return 'text-blue-900 dark:text-blue-100';
    case 'task':
      return 'text-emerald-900 dark:text-emerald-100';
    case 'due_date':
      return 'text-orange-900 dark:text-orange-100';
    default:
      return 'text-purple-900 dark:text-purple-100';
  }
};

const getReminderTypeLabel = (type: ReminderItem['type']) => {
  switch (type) {
    case 'meeting':
      return '📅 Meeting Reminder';
    case 'task':
      return '✅ Task Reminder';
    case 'due_date':
      return '⏰ Due Date Alert';
    default:
      return '🔔 Event Reminder';
  }
};

const formatEventTime = (date: Date) => {
  const today = new Date();
  const isToday = date.toDateString() === today.toDateString();

  if (isToday) {
    return `Today at ${date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
  }
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Meeting Icon
const MeetingIcon = () =>
  h(
    'svg',
    {
      class: 'h-5 w-5',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': '2',
    },
    [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
      }),
    ],
  );

// Task Icon
const TaskIcon = () =>
  h(
    'svg',
    {
      class: 'h-5 w-5',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': '2',
    },
    [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
      }),
    ],
  );

// Due Date Icon
const DueDateIcon = () =>
  h(
    'svg',
    {
      class: 'h-5 w-5',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': '2',
    },
    [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
      }),
    ],
  );

// Event Icon
const EventIcon = () =>
  h(
    'svg',
    {
      class: 'h-5 w-5',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': '2',
    },
    [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
      }),
    ],
  );

const getIcon = (type: ReminderItem['type']) => {
  switch (type) {
    case 'meeting':
      return MeetingIcon;
    case 'task':
      return TaskIcon;
    case 'due_date':
      return DueDateIcon;
    default:
      return EventIcon;
  }
};

onMounted(() => {
  const authStore = useAuthStore();
  // Only start polling if user is authenticated
  if (authStore.isAuthenticated) {
    reminderStore.startPolling(5); // Check every 5 minutes
  }

  // Watch for auth changes — start/stop polling accordingly
  stopAuthWatch = watch(
    () => authStore.isAuthenticated,
    (isAuth) => {
      if (isAuth) {
        reminderStore.startPolling(5);
      } else {
        reminderStore.stopPolling();
      }
    },
  );
});
</script>

<style scoped>
.toast-slide-enter-active {
    transition: transform 0.3s ease, opacity 0.3s ease;
}

.toast-slide-leave-active {
    transition: transform 0.3s ease, opacity 0.3s ease;
}

.toast-slide-enter-from {
    opacity: 0;
    transform: translateX(100%);
}

.toast-slide-leave-to {
    opacity: 0;
    transform: translateX(100%);
}

.toast-slide-move {
    transition: transform 0.3s ease;
}

.dropdown-enter-active,
.dropdown-leave-active {
    transition: transform 0.15s ease, opacity 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
    opacity: 0;
    transform: translateY(-4px);
}
</style>
