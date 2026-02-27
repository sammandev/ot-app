<template>
  <ThemeProvider>
    <SidebarProvider>
      <ToastNotification />
      <EventReminderToast />
      <ErrorBoundary>
        <RouterView />
      </ErrorBoundary>
    </SidebarProvider>
  </ThemeProvider>
</template>

<script setup lang="ts">
import ErrorBoundary from './components/common/ErrorBoundary.vue'
import EventReminderToast from './components/common/EventReminderToast.vue'
import ToastNotification from './components/common/Toast.vue'
import SidebarProvider from './components/layout/SidebarProvider.vue'
import ThemeProvider from './components/layout/ThemeProvider.vue'
</script>
