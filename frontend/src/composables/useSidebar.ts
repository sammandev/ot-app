import type { Ref } from 'vue' //
import { computed, inject, onMounted, onUnmounted, provide, ref } from 'vue'

interface SidebarContextType {
	isExpanded: Ref<boolean>
	isMobileOpen: Ref<boolean>
	isHovered: Ref<boolean>
	isHidden: Ref<boolean>
	activeItem: Ref<string | null>
	openSubmenu: Ref<string | null>
	toggleSidebar: () => void
	toggleExpanded: () => void
	toggleMobileSidebar: () => void
	setIsHovered: (isHovered: boolean) => void
	setActiveItem: (item: string | null) => void
	toggleSubmenu: (item: string) => void
}

const SidebarSymbol = Symbol()

export function useSidebarProvider() {
	const isExpanded = ref(false)
	const isMobileOpen = ref(false)
	const isMobile = ref(false)
	const isHovered = ref(false)
	const isHidden = ref(false)
	const activeItem = ref<string | null>(null)
	const openSubmenu = ref<string | null>(null)
	// No click counters; hide/restore and expand/collapse are separate controls now.

	const handleResize = () => {
		const mobile = window.innerWidth < 768
		isMobile.value = mobile
		if (!mobile) {
			isMobileOpen.value = false
		}
	}

	onMounted(() => {
		handleResize()
		window.addEventListener('resize', handleResize)
		try {
			const hidden = localStorage.getItem('sidebarHidden')
			isHidden.value = hidden === '1'
			const expanded = localStorage.getItem('sidebarExpanded')
			if (expanded !== null) {
				// Only apply expanded state when not hidden
				if (!isHidden.value) {
					isExpanded.value = expanded === '1'
				}
			}
		} catch {
			/* ignore */
		}
	})

	onUnmounted(() => {
		window.removeEventListener('resize', handleResize)
	})

	const toggleSidebar = () => {
		// Mobile: open/close overlay
		if (isMobile.value) {
			isMobileOpen.value = !isMobileOpen.value
			return
		}
		// Desktop: only hide or restore
		if (isHidden.value) {
			// Restore and default to expanded for clarity
			isHidden.value = false
			isExpanded.value = true
			try {
				localStorage.setItem('sidebarHidden', '0')
			} catch {
				/* ignore */
			}
			try {
				localStorage.setItem('sidebarExpanded', '1')
			} catch {
				/* ignore */
			}
			window.dispatchEvent(
				new CustomEvent('sidebar-restored', {
					detail: { message: 'Sidebar restored.' },
				}),
			)
		} else {
			isHidden.value = true
			try {
				localStorage.setItem('sidebarHidden', '1')
			} catch {
				/* ignore */
			}
			window.dispatchEvent(
				new CustomEvent('sidebar-hidden', {
					detail: { message: 'Sidebar hidden.' },
				}),
			)
		}
	}

	const toggleExpanded = () => {
		// Desktop-only; ignore when hidden or on mobile overlay
		if (isHidden.value || isMobile.value) return
		isExpanded.value = !isExpanded.value
		try {
			localStorage.setItem('sidebarExpanded', isExpanded.value ? '1' : '0')
		} catch {
			/* ignore */
		}
	}

	const toggleMobileSidebar = () => {
		isMobileOpen.value = !isMobileOpen.value
	}

	const setIsHovered = (value: boolean) => {
		isHovered.value = value
	}

	const setActiveItem = (item: string | null) => {
		activeItem.value = item
	}

	const toggleSubmenu = (item: string) => {
		openSubmenu.value = openSubmenu.value === item ? null : item
	}

	const context: SidebarContextType = {
		isExpanded: computed(() => (isMobile.value ? false : isExpanded.value)),
		isMobileOpen,
		isHovered,
		isHidden,
		activeItem,
		openSubmenu,
		toggleSidebar,
		toggleExpanded,
		toggleMobileSidebar,
		setIsHovered,
		setActiveItem,
		toggleSubmenu,
	}

	provide(SidebarSymbol, context)

	return context
}

export function useSidebar(): SidebarContextType {
	const context = inject<SidebarContextType>(SidebarSymbol)
	if (!context) {
		throw new Error(
			'useSidebar must be used within a component that has SidebarProvider as an ancestor',
		)
	}
	return context
}
