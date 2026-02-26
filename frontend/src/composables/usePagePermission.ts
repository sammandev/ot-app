/**
 * Composable for checking CRUD permissions on a page/resource.
 * Use in views to conditionally show/hide create, update, delete buttons.
 *
 * Usage:
 *   const { canCreate, canRead, canUpdate, canDelete } = usePagePermission('ot_history')
 *   <button v-if="canCreate">Add New</button>
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function usePagePermission(resourceKey: string) {
	const authStore = useAuthStore()

	const canCreate = computed(() => authStore.hasPermission(resourceKey, 'create'))
	const canRead = computed(() => authStore.hasPermission(resourceKey, 'read'))
	const canUpdate = computed(() => authStore.hasPermission(resourceKey, 'update'))
	const canDelete = computed(() => authStore.hasPermission(resourceKey, 'delete'))

	return { canCreate, canRead, canUpdate, canDelete }
}
