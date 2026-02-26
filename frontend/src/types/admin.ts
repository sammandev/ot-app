/**
 * Admin entity types for Department, Employee, and Project management
 */

export interface Department {
	id: number
	code: string
	name: string
	is_enabled: boolean
	created_at?: string
	updated_at?: string
}

export interface Project {
	id: number
	name: string
	is_enabled: boolean
	created_at?: string
	updated_at?: string
}

export interface Employee {
	id: number
	name: string
	emp_id: string
	department?: Department | null
	department_id?: number | null
	is_enabled: boolean
	exclude_from_reports?: boolean
	created_at?: string
	updated_at?: string
}

export interface AdminListResponse<T> {
	count: number
	next: string | null
	previous: string | null
	results: T[]
}

export interface CreateDepartmentPayload {
	code: string
	name: string
	is_enabled?: boolean
}

export type UpdateDepartmentPayload = Partial<CreateDepartmentPayload>

export interface CreateProjectPayload {
	name: string
	is_enabled?: boolean
}

export type UpdateProjectPayload = Partial<CreateProjectPayload>

export interface CreateEmployeePayload {
	name: string
	emp_id: string
	department_id?: number | null
	is_enabled?: boolean
	exclude_from_reports?: boolean
}

export type UpdateEmployeePayload = Partial<CreateEmployeePayload>

export interface OvertimeRegulation {
	id: number
	content: string
	order: number
	is_active: boolean
	created_at?: string
	updated_at?: string
}

export interface CreateOvertimeRegulationPayload {
	content: string
	order?: number
	is_active?: boolean
}

export type UpdateOvertimeRegulationPayload = Partial<CreateOvertimeRegulationPayload>
