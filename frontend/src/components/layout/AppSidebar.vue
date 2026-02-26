<template>
  <aside v-show="!isHidden || isMobileOpen" :class="[
    'fixed mt-16 flex flex-col lg:mt-0 top-0 left-0 bg-white dark:bg-gray-900 dark:border-gray-800 text-gray-900 h-screen transition-[width,padding,transform] duration-300 ease-in-out z-99999 border-r border-gray-200 will-change-[width,transform]',
    {
      'lg:w-[260px] px-5': isShowingFull && !isHidden,
      'lg:w-[75px] px-2': !isShowingFull && !isHidden,
      'lg:w-0 px-0 border-none': isHidden && !isMobileOpen,
      'translate-x-0 w-[260px] px-5': isMobileOpen,
      '-translate-x-full': !isMobileOpen,
      'lg:translate-x-0': true,
    },
  ]" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
    <div :class="[
      'py-5 flex',
      !isShowingFull ? 'lg:justify-center' : 'justify-start',
    ]">
      <router-link to="/" class="flex items-center gap-3">
        <!-- Collapsed (not hovered, not mobile): show image only -->
        <img v-if="!isShowingFull" src="/images/logo/pegatron-logo.jpg" alt="Pegatron Logo"
          class="w-11 h-11 rounded-sm ring-2 ring-[#465FFF] dark:ring-gray-400" />
        <!-- Expanded or hovered or mobile: show image + text -->
        <div v-else class="flex items-center gap-3">
          <img src="/images/logo/pegatron-logo.jpg" alt="Pegatron Logo"
            class="w-11 h-11 rounded-sm ring-2 ring-[#465FFF] dark:ring-gray-400" />
          <div class="leading-tight">
            <p class="text-xl font-semibold text-gray-900 dark:text-white">{{ configStore.appAcronym }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">{{ configStore.appName }}</p>
          </div>
        </div>
      </router-link>
    </div>
    <div class="flex flex-col overflow-y-auto duration-300 ease-linear no-scrollbar">
      <nav class="mb-6">
        <div class="flex flex-col gap-4">
          <div v-for="(menuGroup, groupIndex) in menuGroups" :key="groupIndex">
            <h2 :class="[
              'mb-4 text-xs uppercase flex leading-[20px] text-gray-400',
              !isShowingFull
                ? 'lg:justify-center'
                : 'justify-start',
            ]">
              <template v-if="isShowingFull">
                {{ menuGroup.title }}
              </template>
              <HorizontalDots v-else />
            </h2>
            <ul class="flex flex-col gap-4">
              <li v-for="(item, index) in menuGroup.items" :key="item.name">
                <button v-if="item.subItems" @click="toggleSubmenu(groupIndex, index)" :class="[
                  'menu-item group w-full',
                  {
                    'menu-item-active': route.path === item.path || (item.subItems && item.subItems.some(sub => sub.path === route.path)),
                    'menu-item-inactive': !(route.path === item.path || (item.subItems && item.subItems.some(sub => sub.path === route.path))),
                  },
                  !isShowingFull
                    ? 'lg:justify-center'
                    : 'lg:justify-start',
                ]">
                  <span :class="[
                    (route.path === item.path || (item.subItems && item.subItems.some(sub => sub.path === route.path)))
                      ? 'menu-item-icon-active'
                      : 'menu-item-icon-inactive',
                  ]">
                    <component :is="item.icon" />
                  </span>
                  <span v-if="isShowingFull" class="menu-item-text">{{ item.name }}</span>
                  <ChevronDownIcon v-if="isShowingFull" :class="[
                    'ml-auto w-5 h-5 transition-transform duration-200',
                    {
                      'rotate-180 text-brand-500': isSubmenuOpen(
                        groupIndex,
                        index
                      ),
                    },
                  ]" />
                </button>
                <router-link v-else-if="item.path" :to="item.path" :class="[
                  'menu-item group w-full',
                  {
                    'menu-item-active': isActive(item.path),
                    'menu-item-inactive': !isActive(item.path),
                  },
                  !isShowingFull
                    ? 'lg:justify-center'
                    : 'lg:justify-start',
                ]">
                  <span :class="[
                    isActive(item.path)
                      ? 'menu-item-icon-active'
                      : 'menu-item-icon-inactive',
                  ]">
                    <component :is="item.icon" />
                  </span>
                  <span v-if="isShowingFull" class="menu-item-text">{{ item.name }}</span>
                </router-link>
                <transition @enter="startTransition" @after-enter="endTransition" @before-leave="startTransition"
                  @after-leave="endTransition">
                  <div v-show="isSubmenuOpen(groupIndex, index) && isShowingFull">
                    <ul class="mt-2 space-y-1">
                      <li v-for="subItem in item.subItems" :key="subItem.name">
                        <router-link :to="subItem.path" :class="[
                          'menu-item group',
                          {
                            'menu-item-active': route.path === subItem.path,
                            'menu-item-inactive': route.path !== subItem.path
                          },
                        ]">
                          <span :class="[
                            route.path === subItem.path
                              ? 'menu-item-icon-active'
                              : 'menu-item-icon-inactive',
                          ]">
                            <DotIcon />
                          </span>
                          <span v-if="isShowingFull" class="menu-item-text">{{ subItem.name
                            }}</span>
                          <span class="flex items-center gap-1 ml-auto">
                            <span v-if="subItem.new" :class="[
                              'menu-dropdown-badge',
                              {
                                'menu-dropdown-badge-active': route.path === subItem.path,
                                'menu-dropdown-badge-inactive': route.path !== subItem.path
                              },
                            ]">
                              new
                            </span>
                            <span v-if="subItem.pro" :class="[
                              'menu-dropdown-badge',
                              {
                                'menu-dropdown-badge-active': route.path === subItem.path,
                                'menu-dropdown-badge-inactive': route.path !== subItem.path
                              },
                            ]">
                              pro
                            </span>
                          </span>
                        </router-link>
                      </li>
                    </ul>
                  </div>
                </transition>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <!-- <SidebarWidget v-if="isExpanded || isHovered || isMobileOpen" /> -->
    </div>
    <!-- Bottom footer (desktop only) -->
    <button @click="toggleExpanded" :class="[
      'mt-auto hidden lg:flex items-center border-t border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 py-3 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors w-full',
      {
        'justify-center gap-2 px-4 md:px-6': isShowingFull,
        'justify-center px-2': !isShowingFull
      }
    ]">
      <CollapseIcon v-if="isExpanded" class="w-5 h-5" />
      <ExpandIcon v-else class="w-5 h-5" />
      <span v-if="isShowingFull">{{ isExpanded ? t('layout.sidebar.collapse') : t('layout.sidebar.expand') }}</span>
    </button>
  </aside>
</template>

<script setup lang="ts">
import { type Component, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
// import SidebarWidget from "./SidebarWidget.vue";
import { useSidebar } from '@/composables/useSidebar'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'
import {
	ArchiveIcon,
	BarChartIcon,
	BoxIcon,
	CalenderIcon,
	CartIcon,
	ChevronDownIcon,
	CollapseIcon,
	DocsIcon,
	DotIcon,
	ExpandIcon,
	FlagIcon,
	HistoryIcon,
	HorizontalDots,
	KanbanIcon,
	ListIcon,
	OfficeIcon,
	SettingsIcon,
	UserGroupIcon,
} from '../../icons'

const { t } = useI18n()
const route = useRoute()
const authStore = useAuthStore()
const configStore = useConfigStore()

type SubItem = {
	name: string
	path: string
	new?: boolean
	pro?: boolean
	key?: string
}
type MenuItem = {
	icon: Component
	name: string
	path?: string
	subItems?: SubItem[]
	key?: string
	hideForPtbAdmin?: boolean
	showOnlyForPtbAdmin?: boolean
}
type MenuGroup = {
	title: string
	items: MenuItem[]
	requiresAdmin?: boolean
	requiresSuperAdmin?: boolean
}

const { isExpanded, isMobileOpen, isHovered, openSubmenu, isHidden, toggleExpanded } = useSidebar()

// Single computed for "is sidebar showing full-width content" — avoids
// repeating `isExpanded || isHovered || isMobileOpen` in every template binding.
const isShowingFull = computed(() => isExpanded.value || isHovered.value || isMobileOpen.value)

// Debounced hover: small delay before expanding on hover to prevent flicker
// when the cursor briefly passes over the collapsed sidebar.
let hoverTimer: ReturnType<typeof setTimeout> | null = null

function handleMouseEnter() {
	if (isExpanded.value) return
	hoverTimer = setTimeout(() => {
		isHovered.value = true
	}, 75)
}

function handleMouseLeave() {
	if (hoverTimer) {
		clearTimeout(hoverTimer)
		hoverTimer = null
	}
	isHovered.value = false
}

onUnmounted(() => {
	if (hoverTimer) clearTimeout(hoverTimer)
})

const allMenuGroups = computed<MenuGroup[]>(() => [
	{
		title: t('menu.overtime'),
		items: [
			{
				icon: ListIcon,
				name: t('menu.otForm'),
				path: '/ot/form',
				key: 'ot_form',
			},
			{
				icon: HistoryIcon,
				name: t('menu.otHistory'),
				path: '/ot/history',
				key: 'ot_history',
			},
			{
				icon: BarChartIcon,
				name: t('menu.otSummary'),
				path: '/ot/summary',
				key: 'ot_summary',
			},
		],
	},
	{
		title: t('menu.others'),
		items: [
			{
				icon: CalenderIcon,
				name: t('menu.ptbCalendar'),
				path: '/ptb-calendar',
				key: 'calendar',
			},
			{
				icon: KanbanIcon,
				name: t('menu.taskBoard'),
				path: '/kanban',
				key: 'kanban',
			},
			{
				icon: CartIcon,
				name: t('menu.purchasing'),
				subItems: [
					{ name: t('menu.purchasingList'), path: '/purchasing/list', key: 'purchasing' },
					{
						name: t('menu.requestPurchase'),
						path: '/purchasing/request',
						key: 'purchasing',
					},
				],
				key: 'purchasing',
			},
			{
				icon: BoxIcon,
				name: t('menu.assets'),
				path: '/asset-management',
				key: 'assets',
			},
			{
				icon: FlagIcon,
				name: t('menu.reportIssue'),
				path: '/report',
				key: 'report',
			},
			{
				icon: OfficeIcon,
				name: t('menu.departments'),
				path: '/admin/departments',
				key: 'departments',
				hideForPtbAdmin: true, // Hide from Others section for PTB admins
			},
			{
				icon: ArchiveIcon,
				name: t('menu.projects'),
				path: '/admin/projects',
				key: 'projects',
				hideForPtbAdmin: true, // Hide from Others section for PTB admins
			},
		],
	},
	{
		title: t('menu.admin'),
		requiresAdmin: true,
		items: [
			{
				icon: OfficeIcon,
				name: t('menu.departments'),
				path: '/admin/departments',
				key: 'departments',
				showOnlyForPtbAdmin: true, // Show in Admin section only for PTB admins
			},
			{
				icon: ArchiveIcon,
				name: t('menu.projects'),
				path: '/admin/projects',
				key: 'projects',
				showOnlyForPtbAdmin: true, // Show in Admin section only for PTB admins
			},
			{
				icon: UserGroupIcon,
				name: t('menu.employees'),
				path: '/admin/employees',
				key: 'admin_employees',
			},
			{
				icon: DocsIcon,
				name: t('menu.otRegulations'),
				path: '/admin/ot-regulations',
				key: 'admin_regulations',
			},
		],
	},
	{
		title: t('menu.superAdmin'),
		requiresSuperAdmin: true,
		items: [
			{
				icon: SettingsIcon,
				name: t('menu.accessControl'),
				path: '/super-admin/access-control',
				key: 'super_admin_access',
			},
		],
	},
])

// Filter menu groups based on user permissions
const menuGroups = computed(() => {
	// Guard: if user is not loaded yet, return empty menu
	if (!authStore.user) {
		return []
	}

	const isPtbAdmin = authStore.isPtbAdmin
	const isSuperAdmin = authStore.isSuperAdmin

	return allMenuGroups.value
		.map((group) => {
			// Role filtering
			if (group.requiresSuperAdmin && !isSuperAdmin) {
				return null
			}
			if (group.requiresAdmin && !isPtbAdmin && !isSuperAdmin) {
				// Additional check: Does regular user have explicit permissions to access admin items?
				// If not, hide the whole admin group unless they have at least one item allowed
				const hasAccessToAnyItem = group.items.some((item) => {
					if (!item.key) return false
					// Skip items that are only for PTB admins when checking regular user access
					if (item.showOnlyForPtbAdmin) return false
					return authStore.hasAnyPermission(item.key)
				})
				if (!hasAccessToAnyItem) return null
			}

			// Item filtering
			const filteredItems = group.items.filter((item) => {
				// Hide items marked for PTB admins in Others section when user is PTB admin or super admin
				if (item.hideForPtbAdmin && (isPtbAdmin || isSuperAdmin)) {
					return false
				}

				// Show items marked for PTB admin only when user is PTB admin or super admin
				if (item.showOnlyForPtbAdmin && !isPtbAdmin && !isSuperAdmin) {
					return false
				}

				// Check if user has any permission for this resource (show menu if they have any access)
				if (item.key) {
					return authStore.hasAnyPermission(item.key)
				}
				return true
			})

			if (filteredItems.length === 0) return null

			return { ...group, items: filteredItems }
		})
		.filter((group): group is MenuGroup => group !== null)
})

const isActive = (path: string) => route.path === path

const toggleSubmenu = (groupIndex: number, itemIndex: number) => {
	const key = `${groupIndex}-${itemIndex}`
	openSubmenu.value = openSubmenu.value === key ? null : key
}

const isAnySubmenuRouteActive = computed(() => {
	return menuGroups.value.some((group) =>
		group.items.some((item) => item.subItems?.some((subItem) => isActive(subItem.path))),
	)
})

const isSubmenuOpen = (groupIndex: number, itemIndex: number) => {
	const key = `${groupIndex}-${itemIndex}`
	return (
		openSubmenu.value === key ||
		(isAnySubmenuRouteActive.value &&
			!!menuGroups.value[groupIndex]?.items[itemIndex]?.subItems?.some((subItem) =>
				isActive(subItem.path),
			))
	)
}

const startTransition = (el: Element) => {
	const node = el as HTMLElement
	node.style.height = 'auto'
	const height = node.scrollHeight
	node.style.height = '0px'
	void node.offsetHeight // force reflow
	node.style.height = height + 'px'
}

const endTransition = (el: Element) => {
	;(el as HTMLElement).style.height = ''
}
</script>
