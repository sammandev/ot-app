<template>
  <div class="relative min-w-0" ref="multiSelectRef">
    <div
      role="button"
      tabindex="0"
      @click="toggleDropdown"
      @keydown.enter.prevent="toggleDropdown"
      @keydown.space.prevent="toggleDropdown"
      class="dark:bg-dark-900 relative flex min-h-11 w-full cursor-pointer appearance-none items-start rounded-lg border border-gray-300 bg-transparent bg-none px-3.5 py-2 text-left text-sm text-gray-800 shadow-theme-xs transition focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
      :class="[
        isOpen && 'border-brand-300 ring-3 ring-brand-500/10 dark:border-brand-800',
      ]"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
    >
      <div class="flex min-w-0 flex-1 flex-wrap items-center gap-1.5 pr-7">
        <span v-if="selectedItems.length === 0" class="py-1 text-gray-400 dark:text-white/30">{{ placeholder }}</span>
        <div
          v-for="item in selectedItems"
          :key="item.value"
          class="group flex max-w-full items-center gap-1 rounded-full border border-transparent bg-gray-100 py-1 pl-2.5 pr-2 text-sm text-gray-800 transition hover:border-gray-200 dark:bg-gray-800 dark:text-white/90 dark:hover:border-gray-700"
        >
          <span class="truncate">{{ item.label }}</span>
          <button
            @click.stop="removeItem(item)"
            type="button"
            class="cursor-pointer pl-1 text-gray-500 transition group-hover:text-gray-700 dark:text-gray-400 dark:group-hover:text-white/80"
            aria-label="Remove item"
          >
            <svg
              role="button"
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fill-rule="evenodd"
                clip-rule="evenodd"
                d="M3.40717 4.46881C3.11428 4.17591 3.11428 3.70104 3.40717 3.40815C3.70006 3.11525 4.17494 3.11525 4.46783 3.40815L6.99943 5.93975L9.53095 3.40822C9.82385 3.11533 10.2987 3.11533 10.5916 3.40822C10.8845 3.70112 10.8845 4.17599 10.5916 4.46888L8.06009 7.00041L10.5916 9.53193C10.8845 9.82482 10.8845 10.2997 10.5916 10.5926C10.2987 10.8855 9.82385 10.8855 9.53095 10.5926L6.99943 8.06107L4.46783 10.5927C4.17494 10.8856 3.70006 10.8856 3.40717 10.5927C3.11428 10.2998 3.11428 9.8249 3.40717 9.53201L5.93877 7.00041L3.40717 4.46881Z"
                fill="currentColor"
              />
            </svg>
          </button>
        </div>
      </div>

      <svg
        class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 transition-transform"
        :class="{ 'rotate-180': isOpen }"
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M4.79175 7.39551L10.0001 12.6038L15.2084 7.39551"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </div>

    <Teleport to="body">
      <transition
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="scale-95 opacity-0"
        enter-to-class="scale-100 opacity-100"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="scale-100 opacity-100"
        leave-to-class="scale-95 opacity-0"
      >
        <div
          v-if="isOpen"
          ref="dropdownRef"
          class="fixed z-[1400] overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-[0_18px_50px_rgba(15,23,42,0.18)] dark:border-gray-700 dark:bg-gray-900"
          :style="dropdownStyle"
        >
          <div v-if="searchable" class="border-b border-gray-200 px-3 py-2 dark:border-gray-800">
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="searchPlaceholder"
              class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 focus:border-brand-300 focus:outline-hidden focus:ring-2 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
            />
          </div>
          <ul
            class="custom-scrollbar overflow-y-auto divide-y divide-gray-200 dark:divide-gray-800"
            :style="dropdownListStyle"
            role="listbox"
            aria-multiselectable="true"
          >
            <li
              v-for="item in filteredOptions"
              :key="item.value"
              @click="toggleItem(item)"
              class="relative flex w-full items-center px-3 py-2.5 first:rounded-t-lg last:rounded-b-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
              :class="{ 'bg-gray-50 dark:bg-white/[0.03]': isSelected(item) }"
              role="option"
              :aria-selected="isSelected(item)"
            >
              <span class="grow">{{ item.label }}</span>
              <svg
                v-if="isSelected(item)"
                class="h-5 w-5 text-gray-400 dark:text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
            </li>
            <li
              v-if="filteredOptions.length === 0"
              class="px-3 py-3 text-sm text-gray-500 dark:text-gray-400"
            >
              {{ emptyText }}
            </li>
          </ul>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

interface OptionItem {
  value: number | string
	label: string
}

const props = withDefaults(
	defineProps<{
		options: OptionItem[]
		modelValue?: OptionItem[]
    placeholder?: string
    searchable?: boolean
    searchPlaceholder?: string
    emptyText?: string
	}>(),
	{
		modelValue: () => [],
    placeholder: 'Select items...',
    searchable: false,
    searchPlaceholder: 'Search options...',
    emptyText: 'No options found.',
	},
)

const emit = defineEmits<(event: 'update:modelValue', value: OptionItem[]) => void>()

const isOpen = ref(false)
const selectedItems = ref<OptionItem[]>([...props.modelValue])
const multiSelectRef = ref<HTMLElement | null>(null)
const dropdownRef = ref<HTMLElement | null>(null)
const searchQuery = ref('')
const dropdownStyle = ref<Record<string, string>>({})
const dropdownListStyle = ref<Record<string, string>>({ maxHeight: '320px' })

const placeholder = computed(() => props.placeholder)
const searchable = computed(() => props.searchable)
const searchPlaceholder = computed(() => props.searchPlaceholder)
const emptyText = computed(() => props.emptyText)

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value.trim()) {
    return props.options
  }

  const query = searchQuery.value.trim().toLowerCase()
  return props.options.filter((item) => item.label.toLowerCase().includes(query))
})

const updateDropdownPosition = () => {
  if (!multiSelectRef.value || typeof window === 'undefined') {
    return
  }

  const rect = multiSelectRef.value.getBoundingClientRect()
  const viewportPadding = 12
  const dropdownOffset = 8
  const spaceBelow = window.innerHeight - rect.bottom - viewportPadding
  const spaceAbove = rect.top - viewportPadding
  const shouldOpenAbove = spaceBelow < 220 && spaceAbove > spaceBelow
  const availableHeight = Math.max(
    140,
    Math.min(320, (shouldOpenAbove ? spaceAbove : spaceBelow) - dropdownOffset),
  )
  const left = Math.max(viewportPadding, rect.left)
  const maxWidth = window.innerWidth - left - viewportPadding

  dropdownStyle.value = {
    top: `${Math.round(shouldOpenAbove ? rect.top - dropdownOffset : rect.bottom + dropdownOffset)}px`,
    left: `${Math.round(left)}px`,
    width: `${Math.round(Math.min(rect.width, maxWidth))}px`,
    transform: shouldOpenAbove ? 'translateY(-100%)' : 'translateY(0)',
    transformOrigin: shouldOpenAbove ? 'bottom center' : 'top center',
  }
  dropdownListStyle.value = {
    maxHeight: `${Math.round(availableHeight)}px`,
  }
}

const toggleDropdown = () => {
	isOpen.value = !isOpen.value
  if (isOpen.value) {
    void nextTick(() => {
      updateDropdownPosition()
    })
  }
  if (!isOpen.value) {
    searchQuery.value = ''
  }
}

const toggleItem = (item: OptionItem) => {
	const index = selectedItems.value.findIndex((selected) => selected.value === item.value)
	if (index === -1) {
		selectedItems.value.push(item)
	} else {
		selectedItems.value.splice(index, 1)
	}
  emit('update:modelValue', [...selectedItems.value])
}

const removeItem = (item: OptionItem) => {
	const index = selectedItems.value.findIndex((selected) => selected.value === item.value)
	if (index !== -1) {
		selectedItems.value.splice(index, 1)
    emit('update:modelValue', [...selectedItems.value])
	}
}

const isSelected = (item: OptionItem) => {
	return selectedItems.value.some((selected) => selected.value === item.value)
}

const handleClickOutside = (event: MouseEvent) => {
	if (
		multiSelectRef.value &&
		event.target instanceof Node &&
    !multiSelectRef.value.contains(event.target) &&
    !dropdownRef.value?.contains(event.target)
	) {
		isOpen.value = false
    searchQuery.value = ''
	}
}

const handleViewportChange = () => {
  if (!isOpen.value) {
    return
  }
  updateDropdownPosition()
}

watch(
  () => props.modelValue,
  (newValue) => {
    selectedItems.value = [...newValue]
  },
  { deep: true },
)

watch(
  () => props.options,
  (newOptions) => {
    selectedItems.value = selectedItems.value
      .map((selected) => newOptions.find((option) => option.value === selected.value) ?? selected)
      .filter((selected) => newOptions.some((option) => option.value === selected.value))
  },
  { deep: true },
)

watch(isOpen, (open) => {
  if (!open) {
    return
  }
  void nextTick(() => {
    updateDropdownPosition()
  })
})

onMounted(() => {
	document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', handleViewportChange)
  document.addEventListener('scroll', handleViewportChange, true)
})

onBeforeUnmount(() => {
	document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', handleViewportChange)
  document.removeEventListener('scroll', handleViewportChange, true)
})
</script>
