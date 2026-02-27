<!-- @vue/component -->
<template>
    <AdminLayout>
        <div class="space-y-6">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm font-semibold text-brand-500">{{ t('pages.purchasingRequest.category') }}</p>
                    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">{{
                        t('pages.purchasingRequest.title') }}</h1>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('pages.purchasingRequest.subtitle') }}</p>
                </div>
                <router-link to="/purchasing/list"
                    class="h-11 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5 flex items-center">
                    {{ t('purchasing.backToList') }}
                </router-link>
            </div>

            <!-- Request Form -->
            <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
                <form @submit.prevent="handleSubmit" class="space-y-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <!-- Request Date -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                {{ t('purchasing.requestDate') }} <span class="text-error-500">*</span>
                            </label>
                            <input ref="requestDateInput" type="text" v-model="form.request_date"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :class="errors.request_date ? 'border-error-300 dark:border-error-700' : ''"
                                :placeholder="t('purchasing.selectDate')" required />
                            <p v-if="errors.request_date" class="text-xs text-error-500">{{ errors.request_date }}</p>
                        </div>

                        <!-- Owner -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                {{ t('purchasing.owner') }} <span class="text-error-500">*</span>
                            </label>
                            <input v-model="form.owner" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :class="errors.owner ? 'border-error-300 dark:border-error-700' : ''"
                                :placeholder="t('purchasing.enterOwner')" required />
                            <p v-if="errors.owner" class="text-xs text-error-500">{{ errors.owner }}</p>
                        </div>

                        <!-- Doc ID -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('purchasing.docId')
                                }}</label>
                            <input v-model="form.doc_id" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.documentId')" />
                        </div>

                        <!-- Part No. -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.partNo') }}</label>
                            <input v-model="form.part_no" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.partNumber')" />
                        </div>

                        <!-- Material Category -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.materialCategory') }}</label>
                            <input v-model="form.material_category" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.materialCategory')" />
                        </div>

                        <!-- Qty -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('purchasing.qty')
                                }}</label>
                            <input v-model.number="form.qty" type="number" min="1"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                placeholder="1" />
                        </div>

                        <!-- Description-Spec (full width) -->
                        <div class="space-y-2 md:col-span-2 lg:col-span-3">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.descriptionSpec') }}</label>
                            <textarea v-model="form.description_spec" rows="3"
                                class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.enterDescription')"></textarea>
                        </div>

                        <!-- Purpose/Desc. -->
                        <div class="space-y-2 md:col-span-2 lg:col-span-3">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.purposeDesc') }}</label>
                            <textarea v-model="form.purpose_desc" rows="2"
                                class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.enterPurpose')"></textarea>
                        </div>

                        <!-- Plant -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('purchasing.plant')
                                }}</label>
                            <input v-model="form.plant" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.plant')" />
                        </div>

                        <!-- Project Code -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.projectCode') }}</label>
                            <input v-model="form.project_code" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.projectCode')" />
                        </div>

                        <!-- PR Type -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.prType') }}</label>
                            <input v-model="form.pr_type" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.prType')" />
                        </div>

                        <!-- MRPID -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('purchasing.mrpid')
                                }}</label>
                            <input v-model="form.mrp_id" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.mrpid')" />
                        </div>

                        <!-- Purch. Org. -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.purchOrg') }}</label>
                            <input v-model="form.purch_org" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.purchOrg')" />
                        </div>

                        <!-- Sourcer Price -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.sourcerPrice') }}</label>
                            <input v-model="form.sourcer_price" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.sourcerPrice')" />
                        </div>

                        <!-- PR No. -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('purchasing.prNo')
                                }}</label>
                            <input v-model="form.pr_no" type="text"
                                class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.prNo')" />
                        </div>

                        <!-- Status -->
                        <div class="space-y-2">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.status') }}</label>
                            <select v-model="form.status"
                                class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90">
                                <option value="pending">{{ t('purchasing.pending') }}</option>
                                <option value="done">{{ t('purchasing.doneStat') }}</option>
                                <option value="canceled">{{ t('purchasing.canceled') }}</option>
                            </select>
                        </div>

                        <!-- Remarks (full width) -->
                        <div class="space-y-2 md:col-span-2 lg:col-span-3">
                            <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{
                                t('purchasing.remarks') }}</label>
                            <textarea v-model="form.remarks" rows="3"
                                class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                                :placeholder="t('purchasing.additionalRemarks')"></textarea>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="flex gap-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                        <button type="button" @click="resetForm"
                            class="h-11 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                            {{ t('common.reset') }}
                        </button>
                        <button type="submit" :disabled="isSubmitting || !canCreate"
                            class="h-11 rounded-lg bg-brand-600 px-8 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-brand-700 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 disabled:opacity-50">
                            {{ isSubmitting ? t('purchasing.creatingRequest') : t('purchasing.createRequest') }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </AdminLayout>
</template>

<script setup lang="ts">
import flatpickr from 'flatpickr'
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { usePagePermission } from '@/composables/usePagePermission'
import { useToast } from '@/composables/useToast'
import { purchaseRequestAPI } from '@/services/api/purchase-request'

const router = useRouter()
const { t } = useI18n()
const { showToast } = useToast()
const { canCreate } = usePagePermission('purchasing')

// Form state
const form = ref({
	request_date: '',
	owner: '',
	doc_id: '',
	part_no: '',
	description_spec: '',
	material_category: '',
	purpose_desc: '',
	qty: 1,
	plant: '',
	project_code: '',
	pr_type: '',
	mrp_id: '',
	purch_org: '',
	sourcer_price: '',
	pr_no: '',
	remarks: '',
	status: 'pending' as 'pending' | 'done' | 'canceled',
})

const errors = ref<Record<string, string>>({})
const isSubmitting = ref(false)
const requestDateInput = ref<HTMLInputElement | null>(null)
let requestDatePicker: flatpickr.Instance | null = null

const validateForm = () => {
	errors.value = {}

	if (!form.value.request_date) {
		errors.value.request_date = t('purchasing.requestDateRequired')
	}
	if (!form.value.owner) {
		errors.value.owner = t('purchasing.ownerRequired')
	}

	return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
	if (!validateForm()) {
		showToast(t('purchasing.fillRequired'), 'error')
		return
	}

	isSubmitting.value = true
	try {
		await purchaseRequestAPI.create(form.value)
		showToast(t('purchasing.requestCreated'), 'success')
		router.push('/purchasing/list')
	} catch (error) {
		console.error('Failed to create purchase request:', error)
		showToast(t('purchasing.requestCreateFailed'), 'error')
	} finally {
		isSubmitting.value = false
	}
}

const resetForm = () => {
	form.value = {
		request_date: '',
		owner: '',
		doc_id: '',
		part_no: '',
		description_spec: '',
		material_category: '',
		purpose_desc: '',
		qty: 1,
		plant: '',
		project_code: '',
		pr_type: '',
		mrp_id: '',
		purch_org: '',
		sourcer_price: '',
		pr_no: '',
		remarks: '',
		status: 'pending',
	}
	errors.value = {}

	if (requestDatePicker) {
		requestDatePicker.clear()
	}
}

const initDatePicker = () => {
	if (requestDateInput.value) {
		requestDatePicker = flatpickr(requestDateInput.value, {
			dateFormat: 'Y-m-d',
			defaultDate: new Date(),
			onChange: (selectedDates) => {
				if (selectedDates.length > 0 && selectedDates[0]) {
					const dateStr = selectedDates[0].toISOString().split('T')[0]
					form.value.request_date = dateStr ?? ''
				}
			},
		})
		// Set today's date as default
		const today = new Date().toISOString().split('T')[0]
		form.value.request_date = today ?? ''
	}
}

onMounted(() => {
	initDatePicker()
})

onUnmounted(() => {
	if (requestDatePicker) {
		requestDatePicker.destroy()
	}
})
</script>
