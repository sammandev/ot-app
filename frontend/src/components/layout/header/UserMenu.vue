<template>
  <div class="relative" ref="dropdownRef">
    <button class="flex items-center text-gray-700 dark:text-gray-400" @click.prevent="toggleDropdown">
      <span class="mr-3 flex items-center justify-center rounded-full h-11 w-11 bg-brand-100 dark:bg-brand-500/20">
        <span class="text-xs font-semibold text-brand-700 dark:text-brand-300">{{ userInitials }}</span>
      </span>

      <span class="block mr-1 font-medium text-theme-sm">{{ displayName }} </span>

      <ChevronDownIcon :class="{ 'rotate-180': dropdownOpen }" />
    </button>

    <!-- Dropdown Start -->
    <div v-if="dropdownOpen"
      class="absolute right-0 mt-[17px] flex w-[260px] flex-col rounded-2xl border border-gray-200 bg-white p-3 shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark">
      <div>
        <span class="block font-medium text-gray-700 text-theme-sm dark:text-gray-400">
          {{ fullName }}
        </span>
        <span class="mt-0.5 block text-theme-xs text-gray-500 dark:text-gray-400">
          {{ userEmail }}
        </span>
      </div>

      <ul class="flex flex-col gap-1 pt-4 pb-3 border-b border-gray-200 dark:border-gray-800">
        <li v-for="item in menuItems" :key="item.href">
          <router-link :to="item.href"
            class="flex items-center gap-3 px-3 py-2 font-medium text-gray-700 rounded-lg group text-theme-sm hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300">
            <component :is="item.icon" class="text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300" />
            {{ item.text }}
          </router-link>
        </li>
      </ul>
      <button @click="handleSignOut"
        class="flex items-center gap-3 px-3 py-2 mt-3 font-medium text-gray-700 rounded-lg group text-theme-sm hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300">
        <LogoutIcon class="text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300" />
        {{ t('header.signOut') }}
      </button>
    </div>
    <!-- Dropdown End -->
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'
import { ChevronDownIcon, DocsIcon, InfoCircleIcon, LogoutIcon, UserCircleIcon } from '@/icons'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const dropdownOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

// Computed properties from auth store
const fullName = computed(() => {
	const user = authStore.user
	if (!user) return t('header.guest')

	const firstName = user.first_name?.trim() || ''
	const lastName = user.last_name?.trim() || ''

	if (firstName && lastName) {
		return `${firstName} ${lastName}`
	} else if (firstName) {
		return firstName
	} else if (lastName) {
		return lastName
	}
	return user.username
})

const displayName = computed(() => {
	const user = authStore.user
	if (!user) return t('header.guest')

	const firstName = user.first_name?.trim() || ''
	return firstName || user.username
})

const userEmail = computed(() => {
	return authStore.user?.email || ''
})

const userInitials = computed(() => {
	const user = authStore.user
	if (!user?.username) return 'GU'

	const username = user.username
	// Split by underscore or space
	const parts = username.split(/[_\s]+/)

	// Take first letter of first two parts
	if (parts.length >= 2) {
		return (parts[0]!.charAt(0) + parts[1]!.charAt(0)).toUpperCase()
	} else if (parts.length === 1 && parts[0]!.length >= 2) {
		// If single word, take first 2 letters
		return parts[0]!.substring(0, 2).toUpperCase()
	} else {
		return parts[0]!.charAt(0).toUpperCase()
	}
})

const menuItems = computed(() => [
	{ href: '/profile', icon: UserCircleIcon, text: t('header.viewProfile') },
	{ href: '/notes', icon: DocsIcon, text: t('header.privateNotes') },
	{ href: '/about', icon: InfoCircleIcon, text: t('header.aboutPage') },
])

const toggleDropdown = () => {
	dropdownOpen.value = !dropdownOpen.value
}

const closeDropdown = () => {
	dropdownOpen.value = false
}

const handleSignOut = async () => {
	try {
		await authStore.logout()
		closeDropdown()
		router.push('/login')
	} catch (error) {
		console.error('Error logout:', error)
		// Even if logout fails, clear local state and redirect
		closeDropdown()
		router.push('/login')
	}
}

const handleClickOutside = (event: MouseEvent) => {
	if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
		closeDropdown()
	}
}

onMounted(() => {
	document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
	document.removeEventListener('click', handleClickOutside)
})
</script>
