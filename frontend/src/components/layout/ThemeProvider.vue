<template>
  <slot></slot>
</template>

<script setup lang="ts">
import { computed, onMounted, provide, ref, watch } from 'vue'

type Theme = 'light' | 'dark'

const theme = ref<Theme>('light')
const isInitialized = ref(false)

const isDarkMode = computed(() => theme.value === 'dark')

const toggleTheme = () => {
	theme.value = theme.value === 'light' ? 'dark' : 'light'
}

onMounted(() => {
	const savedTheme = localStorage.getItem('theme') as Theme | null
	const initialTheme = savedTheme || 'light' // Default to light theme

	theme.value = initialTheme
	isInitialized.value = true
})

watch([theme, isInitialized], ([newTheme, newIsInitialized]) => {
	if (newIsInitialized) {
		localStorage.setItem('theme', newTheme)
		if (newTheme === 'dark') {
			document.documentElement.classList.add('dark')
			document.body.setAttribute('data-color-scheme', 'dark')
		} else {
			document.documentElement.classList.remove('dark')
			document.body.removeAttribute('data-color-scheme')
		}
	}
})

provide('theme', {
	isDarkMode,
	toggleTheme,
})
</script>

<script lang="ts">
import { inject } from 'vue'

export function useTheme() {
  const theme = inject('theme')
  if (!theme) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return theme
}
</script>
