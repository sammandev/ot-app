<template>
  <router-link to="/" class="lg:hidden flex items-center gap-3">
    <img src="/images/logo/pegatron-logo.jpg" alt="Pegatron Logo"
      class="w-12 h-12 rounded-sm ring-2 ring-[#465FFF] dark:ring-gray-500" />
    <div class="leading-tight">
      <p class="text-xl font-semibold text-gray-900 dark:text-white">{{ configStore.appAcronym }}</p>
      <p class="text-xs text-gray-500 dark:text-gray-400">{{ configStore.appName }}</p>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
</script>
