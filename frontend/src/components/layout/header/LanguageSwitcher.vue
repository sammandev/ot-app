<template>
  <div class="relative" ref="dropdownRef">
    <button @click="isOpen = !isOpen"
      class="relative flex items-center justify-center text-gray-500 transition-colors bg-white border border-gray-200 rounded-full hover:text-dark-900 h-11 w-11 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
      :title="$t('header.language')">
      <span class="text-lg leading-none">{{ currentFlag }}</span>
    </button>

    <Transition enter-active-class="transition duration-100 ease-out" enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-75 ease-in"
      leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
      <div v-if="isOpen"
        class="absolute right-0 z-[99999] mt-1.5 w-40 rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800">
        <button v-for="lang in supportedLocales" :key="lang.code" @click="switchLocale(lang.code)"
          class="flex w-full items-center gap-2.5 px-3 py-2 text-sm transition hover:bg-gray-50 dark:hover:bg-gray-700/50"
          :class="[
            locale === lang.code
              ? 'bg-brand-50 text-brand-700 font-medium dark:bg-brand-900/20 dark:text-brand-400'
              : 'text-gray-700 dark:text-gray-300',
          ]">
          <span class="text-base leading-none">{{ lang.flag }}</span>
          <span>{{ lang.name }}</span>
          <svg v-if="locale === lang.code" class="ml-auto h-4 w-4 text-brand-600 dark:text-brand-400"
            viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd"
              d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
              clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { type SupportedLocale, setLocale, supportedLocales } from '@/i18n'

const { locale } = useI18n()
const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const currentFlag = computed(() => {
	return supportedLocales.find((l) => l.code === locale.value)?.flag ?? '🇺🇸'
})

const currentLabel = computed(() => {
	return supportedLocales.find((l) => l.code === locale.value)?.name ?? 'English'
})

function switchLocale(code: SupportedLocale) {
	setLocale(code)
	isOpen.value = false
}

function handleClickOutside(e: MouseEvent) {
	if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
		isOpen.value = false
	}
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>
