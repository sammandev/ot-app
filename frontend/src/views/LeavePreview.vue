<template>
  <div class="min-h-[100dvh] overflow-y-auto bg-[linear-gradient(180deg,_#edf3fb_0%,_#f5f8fc_100%)] px-3 py-1.5 text-slate-900 sm:px-4 sm:py-2">
    <div class="mx-auto max-w-[1280px] space-y-1.5">
      <div class="overflow-hidden rounded-[32px] border border-white/70 bg-white/88 backdrop-blur">
        <div class="relative overflow-hidden border-b border-slate-200/80 bg-[linear-gradient(135deg,_#0d3550_0%,_#111b37_58%,_#202b68_100%)] px-8 py-4 text-white sm:px-10">
          <div class="absolute inset-0 opacity-35">
            <div class="absolute -left-12 top-0 h-36 w-36 rounded-full bg-sky-400/30 blur-3xl"></div>
            <div class="absolute right-0 top-8 h-28 w-28 rounded-full bg-amber-300/20 blur-3xl"></div>
          </div>
          <div class="relative flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.32em] text-sky-300">PTB Calendar</p>
              <h1 class="mt-1.5 text-3xl font-semibold tracking-tight text-white sm:text-[2.8rem]">Leave Preview</h1>
              <p class="mt-1.5 max-w-xl text-sm leading-6 text-slate-300">A simple read-only summary of the submitted leave request.</p>
            </div>
            <router-link to="/ptb-calendar" class="inline-flex items-center justify-center rounded-[20px] border border-white/15 bg-white/10 px-7 py-3 text-sm font-semibold text-white transition hover:bg-white/15">
              Open PTB Calendar
            </router-link>
          </div>
        </div>

        <div class="p-4 sm:p-5">
          <div v-if="loading" class="flex min-h-[320px] items-center justify-center">
            <div class="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-5 py-3 text-sm text-slate-600 shadow-sm">
              <span class="h-4 w-4 animate-spin rounded-full border-2 border-sky-500 border-t-transparent"></span>
              Loading leave preview...
            </div>
          </div>

          <div v-else-if="errorMessage" class="rounded-3xl border border-rose-200 bg-rose-50 p-6 text-rose-900">
            <p class="text-sm font-semibold uppercase tracking-[0.24em] text-rose-500">Preview unavailable</p>
            <h2 class="mt-3 text-2xl font-semibold">This preview link cannot be opened.</h2>
            <p class="mt-3 max-w-2xl text-sm leading-6 text-rose-700">{{ errorMessage }}</p>
          </div>

          <div v-else-if="preview" class="space-y-3">
            <section class="grid gap-3 lg:grid-cols-[1.05fr_1.25fr]">
              <div class="rounded-[34px] border border-sky-100 bg-[linear-gradient(135deg,_rgba(244,250,255,0.96),_rgba(255,255,255,0.94))] p-4.5">
                <div class="flex flex-wrap items-start justify-between gap-2.5">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.24em] text-sky-600">Employee</p>
                    <h2 class="mt-1.5 text-[1.95rem] font-semibold tracking-tight text-slate-950 sm:text-[2.65rem]">{{ preview.employee_name }}</h2>
                    <div class="mt-2.5 flex flex-wrap items-center gap-2.5">
                      <p class="inline-flex rounded-full border border-slate-200 bg-white px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">{{ preview.employee_id }}</p>
                      <p class="inline-flex rounded-full border border-slate-200 bg-white px-4 py-1.5 text-xs font-semibold tracking-[0.04em] text-slate-500">{{ preview.employee_email }}</p>
                    </div>
                  </div>
                  <div class="flex h-[96px] w-[86px] flex-col items-center justify-center rounded-[26px] border border-sky-200 bg-white text-center">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-400">Leave</p>
                    <p class="mt-1 text-[2.35rem] font-semibold leading-none text-slate-950">{{ preview.leave_day_count }}</p>
                    <p class="mt-0.5 text-sm text-slate-500">{{ preview.leave_day_count === 1 ? 'day' : 'days' }}</p>
                  </div>
                </div>

                <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-2">
                  <div class="rounded-[22px] border border-sky-200 bg-[linear-gradient(135deg,_#eff8ff_0%,_#ffffff_100%)] px-4 py-3 text-slate-900 shadow-[inset_0_1px_0_rgba(255,255,255,0.9)]">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-sky-700">Agent(s)</p>
                    <p class="mt-2 text-sm font-semibold leading-5 text-slate-900">{{ agentLabel }}</p>
                  </div>
                  <div class="rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-3">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">Note</p>
                    <p class="mt-2 text-sm font-medium leading-5 text-slate-900">{{ preview.note || '-' }}</p>
                  </div>
                  <div class="rounded-[22px] border border-slate-200 bg-white px-5 py-3.5">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">Department</p>
                    <p class="mt-2.5 text-[0.98rem] font-semibold leading-6 text-slate-950">{{ departmentNameCompact }}</p>
                    <p class="mt-1 text-sm text-slate-500">{{ preview.department_code }}</p>
                  </div>
                  <div class="rounded-[22px] border border-slate-200 bg-white px-5 py-3.5">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">Last Update</p>
                    <p class="mt-2.5 text-[0.96rem] leading-6 text-slate-700">{{ compactUpdatedLabel }}</p>
                  </div>
                </div>
              </div>

              <div class="rounded-[34px] border border-slate-200 bg-white p-4.5">
                <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                  <p class="text-xs font-semibold uppercase tracking-[0.24em] text-sky-600">Leave Calendar</p>
                  <p class="text-sm font-medium text-slate-500">{{ previewDatesLabel }}</p>
                </div>

                <div :class="['mt-4 grid gap-3', isSingleMonthPreview ? 'grid-cols-1' : 'xl:grid-cols-2']">
                  <section v-for="month in previewCalendarMonths" :key="month.key" :class="[
                    'rounded-[24px] border border-slate-200 bg-[linear-gradient(180deg,_#fbfdff_0%,_#f5f8fc_100%)]',
                    isSingleMonthPreview ? 'p-4.5' : 'p-3.5',
                  ]">
                    <div class="flex items-center justify-between gap-3">
                      <div>
                        <p :class="[isSingleMonthPreview ? 'text-base' : 'text-sm', 'font-semibold text-slate-950']">{{ month.label }}</p>
                        <p :class="[isSingleMonthPreview ? 'text-sm' : 'text-xs', 'mt-0.5 text-slate-500']">{{ month.leaveCount }} {{ month.leaveCount === 1 ? 'leave day' : 'leave days' }}</p>
                      </div>
                      <span class="inline-flex rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-sky-700">{{ month.shortLabel }}</span>
                    </div>

                    <div :class="[
                      'mt-3 grid grid-cols-7 text-center font-semibold uppercase tracking-[0.14em] text-slate-400',
                      isSingleMonthPreview ? 'gap-1.5 text-[11px]' : 'gap-1 text-[10px]',
                    ]">
                      <span v-for="weekday in calendarWeekdayLabels" :key="`${month.key}-${weekday}`">{{ weekday }}</span>
                    </div>

                    <div :class="['mt-2 grid grid-cols-7', isSingleMonthPreview ? 'gap-1.5' : 'gap-1']">
                      <div v-for="cell in month.cells" :key="cell.key" :class="[
                        'flex items-center justify-center font-semibold',
                        isSingleMonthPreview ? 'h-11 rounded-[16px] text-base' : 'h-9 rounded-[14px] text-sm',
                        !cell.isCurrentMonth && 'text-transparent',
                        cell.isCurrentMonth && !cell.isLeaveDate && !cell.isToday && 'bg-slate-50 text-slate-700',
                        cell.isCurrentMonth && cell.isLeaveDate && !cell.isToday && 'bg-sky-600 text-white',
                        cell.isCurrentMonth && !cell.isLeaveDate && cell.isToday && 'bg-amber-50 text-amber-700 ring-1 ring-amber-300',
                        cell.isCurrentMonth && cell.isLeaveDate && cell.isToday && 'bg-amber-500 text-white ring-2 ring-amber-200'
                      ]">
                        {{ cell.label }}
                      </div>
                    </div>
                  </section>
                </div>

                <div class="mt-4 flex flex-wrap gap-3 text-xs text-slate-500">
                  <span class="inline-flex items-center gap-2"><span class="h-3 w-3 rounded-full bg-sky-600"></span>Leave date</span>
                  <span class="inline-flex items-center gap-2"><span class="h-3 w-3 rounded-full bg-amber-500"></span>Today and leave date</span>
                  <span class="inline-flex items-center gap-2"><span class="h-3 w-3 rounded-full border border-amber-300 bg-amber-50"></span>Today</span>
                </div>
              </div>
            </section>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { employeeLeaveAPI, type EmployeeLeavePreview } from '@/services/api/holiday'
import { extractApiError } from '@/utils/extractApiError'

const route = useRoute()

const loading = ref(false)
const errorMessage = ref('')
const preview = ref<EmployeeLeavePreview | null>(null)

const token = computed(() => {
  const rawToken = route.query.token
  return typeof rawToken === 'string' ? rawToken.trim() : ''
})

const previewDatesLabel = computed(() => {
  if (!preview.value) return ''
  return `${preview.value.leave_day_count} ${preview.value.leave_day_count === 1 ? 'date' : 'dates'} selected`
})

const sortedDates = computed<string[]>(() =>
  [...(preview.value?.dates ?? [])].sort((left, right) => new Date(left).getTime() - new Date(right).getTime()),
)

const calendarWeekdayLabels: string[] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

type PreviewCalendarCell = {
  key: string
  label: string
  isCurrentMonth: boolean
  isLeaveDate: boolean
  isToday: boolean
}

type PreviewCalendarMonth = {
  key: string
  label: string
  shortLabel: string
  leaveCount: number
  cells: PreviewCalendarCell[]
}

const formatLocalDate = (value: Date) => {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const todayDateStr = computed(() => formatLocalDate(new Date()))

const buildCalendarMonth = (year: number, monthIndex: number, leaveDates: string[], todayIso: string): PreviewCalendarMonth => {
  const firstDate = new Date(year, monthIndex, 1)
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate()
  const monthPrefix = `${year}-${String(monthIndex + 1).padStart(2, '0')}-`
  const leaveDateLookup = new Set(leaveDates)
  const leadingEmptyCells = (firstDate.getDay() + 6) % 7
  const cells: PreviewCalendarCell[] = []

  for (let index = 0; index < leadingEmptyCells; index += 1) {
    cells.push({
      key: `${year}-${monthIndex}-empty-start-${index}`,
      label: '',
      isCurrentMonth: false,
      isLeaveDate: false,
      isToday: false,
    })
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    const dateIso = `${monthPrefix}${String(day).padStart(2, '0')}`
    cells.push({
      key: dateIso,
      label: String(day),
      isCurrentMonth: true,
      isLeaveDate: leaveDateLookup.has(dateIso),
      isToday: dateIso === todayIso,
    })
  }

  const trailingCellCount = (7 - (cells.length % 7)) % 7
  for (let index = 0; index < trailingCellCount; index += 1) {
    cells.push({
      key: `${year}-${monthIndex}-empty-end-${index}`,
      label: '',
      isCurrentMonth: false,
      isLeaveDate: false,
      isToday: false,
    })
  }

  const monthDate = new Date(year, monthIndex, 1)
  return {
    key: `${year}-${monthIndex}`,
    label: new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(monthDate),
    shortLabel: new Intl.DateTimeFormat('en-US', { month: 'short' }).format(monthDate),
    leaveCount: leaveDates.filter((dateValue) => dateValue.startsWith(monthPrefix)).length,
    cells,
  }
}

const previewCalendarMonths = computed<PreviewCalendarMonth[]>(() => {
  const months: Array<{ year: number; monthIndex: number }> = []
  const seenMonths = new Set<string>()

  for (const dateValue of sortedDates.value) {
    const date = new Date(dateValue)
    const key = `${date.getFullYear()}-${date.getMonth()}`
    if (seenMonths.has(key)) continue
    seenMonths.add(key)
    months.push({ year: date.getFullYear(), monthIndex: date.getMonth() })
  }

  return months.map(({ year, monthIndex }) => buildCalendarMonth(year, monthIndex, sortedDates.value, todayDateStr.value))
})

const isSingleMonthPreview = computed(() => previewCalendarMonths.value.length <= 1)

const agentLabel = computed(() => {
  if (!preview.value) return '-'
  return preview.value.agents.length > 0 ? preview.value.agents.join(', ') : 'None assigned'
})

const compactUpdatedLabel = computed(() => {
  if (!preview.value) return '-'
  return cleanTimelineLabel(preview.value.updated_at_label || preview.value.created_at_label || preview.value.submitted_by || '-')
})

const departmentNameCompact = computed(() => {
  if (!preview.value) return '-'
  return preview.value.department_name.replace(/-Dept\./g, '-Dept. ')
})

const cleanTimelineLabel = (value: string) => value.replace(/^(submitted|updated)\s*\|\s*/i, '').trim()

const loadPreview = async () => {
  if (!token.value) {
    preview.value = null
    errorMessage.value = 'The preview link is missing its token.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    preview.value = await employeeLeaveAPI.preview(token.value)
  } catch (error) {
    preview.value = null
    errorMessage.value = extractApiError(error, 'This leave preview could not be loaded.')
  } finally {
    loading.value = false
  }
}

watch(token, () => {
  void loadPreview()
})

onMounted(async () => {
  await loadPreview()
})
</script>