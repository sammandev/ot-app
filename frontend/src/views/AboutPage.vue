<template>
    <admin-layout>
        <div class="space-y-6">
            <!-- Page Header -->
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.about.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{ t('pages.about.title', { appAcronym: configStore.appAcronym }) }}
                    </h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.about.subtitle') }}</p>
                </div>
                <nav>
                    <ol class="flex items-center gap-2 text-sm">
                        <li><router-link
                                class="font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                                to="/">{{ t('common.home') }}</router-link></li>
                        <li class="text-gray-400 dark:text-gray-500">/</li>
                        <li class="font-medium text-brand-500">{{ t('pages.about.title', { appAcronym: configStore.appAcronym }) }}</li>
                    </ol>
                </nav>
            </div>

            <!-- Main Content Card -->
            <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex flex-col gap-6">
                    <!-- Hero Section with Gradient -->
                    <div class="text-center">
                        <div class="mb-6 flex justify-center">
                            <div
                                class="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-400 text-3xl font-bold text-white shadow-lg">
                                {{ configStore.appAcronym }}
                            </div>
                        </div>
                        <h1 class="mb-4 text-3xl font-bold text-gray-900 dark:text-white sm:text-4xl">
                            {{ configStore.appName }}
                        </h1>
                        <p class="mx-auto max-w-[700px] text-base leading-relaxed text-gray-600 dark:text-gray-400">
                            {{ t('about.description') }}
                        </p>
                    </div>

                    <!-- Feature Cards -->
                    <div class="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                        <div
                            class="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-[border-color,box-shadow] hover:border-brand-500/50 hover:shadow-md dark:border-gray-700 dark:bg-gray-800/50 dark:hover:border-brand-500/50">
                            <div
                                class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-400 text-white shadow-md ring-4 ring-brand-500/10 transition-transform group-hover:scale-110">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="1.5" stroke="currentColor" class="h-6 w-6">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">{{ t('about.realTimeTracking') }}</h3>
                            <p class="text-sm leading-relaxed text-gray-600 dark:text-gray-400">
                                {{ t('about.realTimeTrackingDesc') }}
                            </p>
                        </div>

                        <div
                            class="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-[border-color,box-shadow] hover:border-brand-500/50 hover:shadow-md dark:border-gray-700 dark:bg-gray-800/50 dark:hover:border-brand-500/50">
                            <div
                                class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-400 text-white shadow-md ring-4 ring-brand-500/10 transition-transform group-hover:scale-110">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="1.5" stroke="currentColor" class="h-6 w-6">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">{{ t('about.smartApprovals') }}</h3>
                            <p class="text-sm leading-relaxed text-gray-600 dark:text-gray-400">
                                {{ t('about.smartApprovalsDesc') }}
                            </p>
                        </div>

                        <div
                            class="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-[border-color,box-shadow] hover:border-brand-500/50 hover:shadow-md dark:border-gray-700 dark:bg-gray-800/50 dark:hover:border-brand-500/50">
                            <div
                                class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-400 text-white shadow-md ring-4 ring-brand-500/10 transition-transform group-hover:scale-110">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="1.5" stroke="currentColor" class="h-6 w-6">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                                </svg>
                            </div>
                            <h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">{{ t('about.detailedAnalytics') }}</h3>
                            <p class="text-sm leading-relaxed text-gray-600 dark:text-gray-400">
                                {{ t('about.detailedAnalyticsDesc') }}
                            </p>
                        </div>
                    </div>

                    <!-- System Information Section -->
                    <div class="mt-8 border-t border-gray-200 pt-8 dark:border-gray-700">
                        <div
                            class="mx-auto max-w-2xl rounded-xl border border-gray-200 bg-gray-50 p-6 dark:border-gray-700 dark:bg-gray-800/50">
                            <h4 class="mb-5 text-center text-lg font-semibold text-gray-900 dark:text-white">
                                {{ t('about.systemInfo') }}
                            </h4>
                            <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
                                <div class="text-center">
                                    <p
                                        class="mb-1 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                        {{ t('about.version') }}</p>
                                    <p class="text-lg font-semibold text-brand-600 dark:text-brand-400">{{ configStore.version }}</p>
                                </div>
                                <div class="text-center">
                                    <p
                                        class="mb-1 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                        {{ t('about.buildDate') }}</p>
                                    <p class="text-lg font-semibold text-brand-600 dark:text-brand-400">{{ configStore.buildDate }}</p>
                                </div>
                                <div class="text-center">
                                    <p
                                        class="mb-1 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                        {{ t('about.developedFor') }}</p>
                                    <p class="text-lg font-semibold text-brand-600 dark:text-brand-400">{{ t('about.ptbInternalUse') }}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </admin-layout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { useConfigStore } from '@/stores/config'

const { t } = useI18n()

const configStore = useConfigStore()

// Ensure fresh system info is loaded
onMounted(() => {
	configStore.fetchConfig()
})
</script>
