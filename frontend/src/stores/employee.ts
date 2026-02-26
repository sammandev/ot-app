/**
 * Employee Store
 * Manages employee data and API calls
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { type Employee, employeeAPI, type PaginatedResponse } from '@/services/api'

export const useEmployeeStore = defineStore('employee', () => {
	// State
	const employees = ref<Employee[]>([])
	const currentEmployee = ref<Employee | null>(null)
	const loading = ref(false)
	const error = ref<string | null>(null)
	const totalCount = ref(0)
	const currentPage = ref(1)
	const pageSize = ref(50)

	// Cache timestamp
	const lastFetched = ref<number | null>(null)
	const CACHE_DURATION = 2 * 60 * 1000 // 2 minutes — employees rarely change

	// Computed
	const enabledEmployees = computed(() => employees.value.filter((e) => e.is_enabled))

	const getEmployeeById = computed(() => {
		return (id: number) => employees.value.find((e) => e.id === id)
	})

	const getEmployeeByEmpId = computed(() => {
		return (empId: string) => employees.value.find((e) => e.emp_id === empId)
	})

	const isCacheValid = computed(() => {
		if (!lastFetched.value) return false
		return Date.now() - lastFetched.value < CACHE_DURATION
	})

	// Actions
	const fetchEmployees = async (params?: {
		page?: number
		page_size?: number
		search?: string
		department_id?: number
	}) => {
		// Use cache if valid and no specific params
		if (!params && isCacheValid.value && employees.value.length > 0) {
			return employees.value
		}

		loading.value = true
		error.value = null

		try {
			// Fetch all employees by default (set high page_size)
			const fetchParams = params || { page_size: 1000 }
			const response: PaginatedResponse<Employee> = await employeeAPI.list(fetchParams)
			employees.value = response.results
			totalCount.value = response.count
			lastFetched.value = Date.now()
			return response.results
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to fetch employees'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const fetchEmployeeById = async (id: number) => {
		loading.value = true
		error.value = null

		try {
			const employee = await employeeAPI.get(id)
			currentEmployee.value = employee

			// Update in list if exists
			const index = employees.value.findIndex((e) => e.id === id)
			if (index > -1) {
				employees.value[index] = employee
			}

			return employee
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to fetch employee'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const createEmployee = async (payload: {
		name: string
		emp_id: string
		department_id?: number | null
		is_enabled?: boolean
		exclude_from_reports?: boolean
	}) => {
		loading.value = true
		error.value = null

		try {
			const employee = await employeeAPI.create(payload)
			employees.value.unshift(employee)
			totalCount.value += 1
			return employee
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to create employee'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const updateEmployee = async (
		id: number,
		payload: {
			name?: string
			emp_id?: string
			department_id?: number | null
			is_enabled?: boolean
			exclude_from_reports?: boolean
		},
	) => {
		loading.value = true
		error.value = null

		try {
			const employee = await employeeAPI.update(id, payload)

			// Update in list
			const index = employees.value.findIndex((e) => e.id === id)
			if (index > -1) {
				employees.value[index] = employee
			}

			if (currentEmployee.value?.id === id) {
				currentEmployee.value = employee
			}

			return employee
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to update employee'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const deleteEmployee = async (id: number) => {
		loading.value = true
		error.value = null

		try {
			await employeeAPI.delete(id)

			// Remove from list
			const index = employees.value.findIndex((e) => e.id === id)
			if (index > -1) {
				employees.value.splice(index, 1)
				totalCount.value -= 1
			}

			if (currentEmployee.value?.id === id) {
				currentEmployee.value = null
			}
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to delete employee'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const setEnabled = async (id: number, enabled: boolean) => {
		loading.value = true
		error.value = null

		try {
			const employee = await employeeAPI.update(id, { is_enabled: enabled })

			// Update in list
			const index = employees.value.findIndex((e) => e.id === id)
			if (index > -1) {
				employees.value[index] = employee
			}

			return employee
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to update employee status'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const clearCache = () => {
		lastFetched.value = null
	}

	const reset = () => {
		employees.value = []
		currentEmployee.value = null
		loading.value = false
		error.value = null
		totalCount.value = 0
		currentPage.value = 1
		lastFetched.value = null
	}

	return {
		// State
		employees,
		currentEmployee,
		loading,
		error,
		totalCount,
		currentPage,
		pageSize,

		// Computed
		enabledEmployees,
		getEmployeeById,
		getEmployeeByEmpId,
		isCacheValid,

		// Actions
		fetchEmployees,
		fetchEmployeeById,
		createEmployee,
		updateEmployee,
		deleteEmployee,
		setEnabled,
		clearCache,
		reset,
	}
})
