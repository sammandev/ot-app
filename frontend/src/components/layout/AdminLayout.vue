<template>
  <div class="min-h-screen xl:flex">
    <app-sidebar />
    <Backdrop />
    <ConfirmDialog />
    <div class="flex-1 min-w-0 overflow-x-clip transition-[margin] duration-300 ease-in-out flex flex-col"
      :class="[isHidden ? 'lg:ml-0' : (isExpanded || isHovered ? 'lg:ml-[260px]' : 'lg:ml-[75px]')]">
      <app-header />
      <div class="p-4 md:p-6 grow w-full">
        <slot></slot>
      </div>
      <footer class="border-t border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
        <div
          class="flex items-center justify-between px-4 py-3 text-xs text-gray-500 md:px-6 dark:text-gray-400">
          <span>&copy; {{ currentYear }} - Pegaunihan Technology Batam</span>
          <div class="flex items-center gap-2">
            <router-link to="/report" class="text-gray-500 underline-offset-2 transition-colors hover:text-brand-600 hover:underline dark:text-gray-400 dark:hover:text-brand-400" :title="t('layout.footer.reportIssue')">{{ t('layout.footer.reportIssue') }}</router-link>
            <span class="text-gray-300 dark:text-gray-600">|</span>
            <router-link to="/release-notes" class="inline-flex items-center rounded-lg bg-brand-100 px-3 py-1 text-xs font-bold text-brand-700 transition-colors hover:bg-brand-200 dark:bg-brand-900/30 dark:text-brand-400 dark:hover:bg-brand-800/40" :title="t('layout.footer.viewReleaseNotes')">v{{ configStore.version }}</router-link>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import { useSidebar } from '@/composables/useSidebar'
import { useConfigStore } from '@/stores/config'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import Backdrop from './Backdrop.vue'

const { t } = useI18n()
const { isExpanded, isHovered, isHidden } = useSidebar()
const configStore = useConfigStore()

const currentYear = ref(new Date().getFullYear())

onMounted(() => {
	configStore.fetchConfig()
})
</script>
