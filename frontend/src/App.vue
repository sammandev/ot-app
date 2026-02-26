<template>
  <ThemeProvider>
    <SidebarProvider>
      <ToastNotification />
      <EventReminderToast />
      <RouterView />
    </SidebarProvider>
  </ThemeProvider>
</template>

<script setup lang="ts">
import EventReminderToast from './components/common/EventReminderToast.vue'
import ToastNotification from './components/common/Toast.vue'
import SidebarProvider from './components/layout/SidebarProvider.vue'
import ThemeProvider from './components/layout/ThemeProvider.vue'
</script>
