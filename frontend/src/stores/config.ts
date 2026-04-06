import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/services/api/client'

export type LeaveNotificationRecipientMode = 'global' | 'department' | 'custom'

export interface LeaveNotificationDepartmentRecipient {
	department_code: string
	recipients: string[]
}

export interface LeaveNotificationEmployeeGroup {
	id: string
	name: string
	employee_ids: number[]
	recipients: string[]
}

export interface LeaveNotificationEmployeeRecipient {
	employee_id: number
	recipients: string[]
	group_ids: string[]
}

export type ActivityLogCleanupTime = `${number}${number}:${number}${number}`

interface SystemConfig {
	app_name?: string
	app_acronym?: string
	version?: string
	build_date?: string
	tab_icon_url?: string | null
	sidebar_logo_url?: string | null
	event_reminders_disabled_globally?: boolean
	event_reminders_disabled_roles?: string[]
	event_reminders_disabled_users?: number[]
	notification_email_host?: string
	notification_email_port?: number
	leave_notification_recipients?: string[]
	leave_notification_sender_name?: string
	leave_notification_recipient_mode?: LeaveNotificationRecipientMode
	leave_notification_department_recipients?: LeaveNotificationDepartmentRecipient[]
	leave_notification_employee_recipients?: LeaveNotificationEmployeeRecipient[]
	leave_notification_employee_groups?: LeaveNotificationEmployeeGroup[]
	user_activity_log_retention_days?: number | null
	user_activity_log_cleanup_time?: ActivityLogCleanupTime
	leave_notification_subject_template?: string
	leave_notification_body_template?: string
	leave_notification_footer_template?: string
}

export const useConfigStore = defineStore('config', () => {
	const appName = ref('OT Management System')
	const appAcronym = ref('OMS')
	const version = ref('2.0.0')
	const buildDate = ref('January 2026')
	const tabIconUrl = ref<string | null>(null)
	const sidebarLogoUrl = ref<string | null>(null)
	const loading = ref(false)
	const error = ref<string | null>(null)

	// Event Reminder Admin Controls
	const eventRemindersDisabledGlobally = ref(false)
	const eventRemindersDisabledRoles = ref<string[]>([])
	const eventRemindersDisabledUsers = ref<number[]>([])
	const notificationEmailHost = ref('mail.pegatroncorp.com')
	const notificationEmailPort = ref(25)
	const leaveNotificationRecipients = ref<string[]>([])
	const leaveNotificationSenderName = ref('OMS')
	const leaveNotificationRecipientMode = ref<LeaveNotificationRecipientMode>('global')
	const leaveNotificationDepartmentRecipients = ref<LeaveNotificationDepartmentRecipient[]>([])
	const leaveNotificationEmployeeRecipients = ref<LeaveNotificationEmployeeRecipient[]>([])
	const leaveNotificationEmployeeGroups = ref<LeaveNotificationEmployeeGroup[]>([])
	const userActivityLogRetentionDays = ref<number | null>(null)
	const userActivityLogCleanupTime = ref<ActivityLogCleanupTime>('00:15')
	const leaveNotificationSubjectTemplate = ref(
		'[PTB Calendar] Leave Request {action_label} - {employee_name} ({leave_day_label})',
	)
	const leaveNotificationBodyTemplate = ref(
		'Hello Team,\n\nA leave request has been {action_label_lower} in PTB Calendar.\n\nEmployee: {employee_name} ({employee_id})\nDepartment: {department_name} ({department_code})\nLeave Dates: {leave_dates}\nTotal Days: {leave_day_count}\nAgent(s): {agents}\nNote: {note}\nSubmitted By: {submitted_by}\n{updated_by_line}\nPlease review the leave coverage details.',
	)
	const leaveNotificationFooterTemplate = ref(
		'Best regards,\n{sender_name}\n\nThis is an automated notification from PTB Calendar.',
	)

	// Cache TTL — config rarely changes
	const lastFetch = ref<number | null>(null)
	const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

	async function fetchConfig(force = false) {
		if (!force && lastFetch.value && Date.now() - lastFetch.value < CACHE_DURATION) {
			return
		}

		loading.value = true

		try {
			const response = await apiClient.get<SystemConfig>('/v1/system/config/')
			const data = response.data

			if (data) {
				appName.value = data.app_name ?? appName.value
				appAcronym.value = data.app_acronym ?? appAcronym.value
				version.value = data.version ?? version.value
				buildDate.value = data.build_date ?? buildDate.value
				tabIconUrl.value = data.tab_icon_url ?? null
				sidebarLogoUrl.value = data.sidebar_logo_url ?? null
				// Event reminder settings
				if (data.event_reminders_disabled_globally !== undefined) {
					eventRemindersDisabledGlobally.value = data.event_reminders_disabled_globally
				}
				if (data.event_reminders_disabled_roles !== undefined) {
					eventRemindersDisabledRoles.value = data.event_reminders_disabled_roles
				}
				if (data.event_reminders_disabled_users !== undefined) {
					eventRemindersDisabledUsers.value = data.event_reminders_disabled_users
				}
				if (data.notification_email_host !== undefined) {
					notificationEmailHost.value = data.notification_email_host
				}
				if (data.notification_email_port !== undefined) {
					notificationEmailPort.value = data.notification_email_port
				}
				if (data.leave_notification_recipients !== undefined) {
					leaveNotificationRecipients.value = data.leave_notification_recipients
				}
				if (data.leave_notification_sender_name !== undefined) {
					leaveNotificationSenderName.value = data.leave_notification_sender_name
				}
				if (data.leave_notification_recipient_mode !== undefined) {
					leaveNotificationRecipientMode.value = data.leave_notification_recipient_mode
				}
				if (data.leave_notification_department_recipients !== undefined) {
					leaveNotificationDepartmentRecipients.value = data.leave_notification_department_recipients
				}
				if (data.leave_notification_employee_recipients !== undefined) {
					leaveNotificationEmployeeRecipients.value = data.leave_notification_employee_recipients
				}
				if (data.leave_notification_employee_groups !== undefined) {
					leaveNotificationEmployeeGroups.value = data.leave_notification_employee_groups
				}
				if (data.user_activity_log_retention_days !== undefined) {
					userActivityLogRetentionDays.value = data.user_activity_log_retention_days
				}
				if (data.user_activity_log_cleanup_time !== undefined) {
					userActivityLogCleanupTime.value = data.user_activity_log_cleanup_time
				}
				if (data.leave_notification_subject_template !== undefined) {
					leaveNotificationSubjectTemplate.value = data.leave_notification_subject_template
				}
				if (data.leave_notification_body_template !== undefined) {
					leaveNotificationBodyTemplate.value = data.leave_notification_body_template
				}
				if (data.leave_notification_footer_template !== undefined) {
					leaveNotificationFooterTemplate.value = data.leave_notification_footer_template
				}
			}
			lastFetch.value = Date.now()
		} catch (err) {
			error.value = 'Failed to fetch system config'
			console.error('Failed to fetch system config:', err)
		} finally {
			loading.value = false
		}
	}

	async function updateConfig(newConfig: Partial<SystemConfig>) {
		loading.value = true

		try {
			const response = await apiClient.patch<SystemConfig>('/v1/system/config/', newConfig)

			const data = response.data
			if (data) {
				appName.value = data.app_name ?? appName.value
				appAcronym.value = data.app_acronym ?? appAcronym.value
				version.value = data.version ?? version.value
				buildDate.value = data.build_date ?? buildDate.value
				tabIconUrl.value = data.tab_icon_url || null
				sidebarLogoUrl.value = data.sidebar_logo_url ?? sidebarLogoUrl.value
				notificationEmailHost.value = data.notification_email_host ?? notificationEmailHost.value
				notificationEmailPort.value = data.notification_email_port ?? notificationEmailPort.value
				leaveNotificationRecipients.value = data.leave_notification_recipients ?? leaveNotificationRecipients.value
				leaveNotificationSenderName.value = data.leave_notification_sender_name ?? leaveNotificationSenderName.value
				leaveNotificationRecipientMode.value = data.leave_notification_recipient_mode ?? leaveNotificationRecipientMode.value
				leaveNotificationDepartmentRecipients.value = data.leave_notification_department_recipients ?? leaveNotificationDepartmentRecipients.value
				leaveNotificationEmployeeRecipients.value = data.leave_notification_employee_recipients ?? leaveNotificationEmployeeRecipients.value
				leaveNotificationEmployeeGroups.value = data.leave_notification_employee_groups ?? leaveNotificationEmployeeGroups.value
				userActivityLogRetentionDays.value = data.user_activity_log_retention_days ?? userActivityLogRetentionDays.value
				userActivityLogCleanupTime.value = data.user_activity_log_cleanup_time ?? userActivityLogCleanupTime.value
				leaveNotificationSubjectTemplate.value = data.leave_notification_subject_template ?? leaveNotificationSubjectTemplate.value
				leaveNotificationBodyTemplate.value = data.leave_notification_body_template ?? leaveNotificationBodyTemplate.value
				leaveNotificationFooterTemplate.value = data.leave_notification_footer_template ?? leaveNotificationFooterTemplate.value
			}
			lastFetch.value = Date.now()
			return data
		} catch (err: unknown) {
			const axiosErr = err as { response?: { data?: { detail?: string } } }
			error.value = axiosErr.response?.data?.detail || 'Failed to update config'
			throw err
		} finally {
			loading.value = false
		}
	}

	return {
		appName,
		appAcronym,
		version,
		buildDate,
		tabIconUrl,
		sidebarLogoUrl,
		eventRemindersDisabledGlobally,
		eventRemindersDisabledRoles,
		eventRemindersDisabledUsers,
		notificationEmailHost,
		notificationEmailPort,
		leaveNotificationRecipients,
		leaveNotificationSenderName,
		leaveNotificationRecipientMode,
		leaveNotificationDepartmentRecipients,
		leaveNotificationEmployeeRecipients,
		leaveNotificationEmployeeGroups,
		userActivityLogRetentionDays,
		userActivityLogCleanupTime,
		leaveNotificationSubjectTemplate,
		leaveNotificationBodyTemplate,
		leaveNotificationFooterTemplate,
		loading,
		error,
		fetchConfig,
		updateConfig,
	}
})
