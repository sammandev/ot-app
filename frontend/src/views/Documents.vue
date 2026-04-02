<template>
  <AdminLayout>
    <div class="space-y-6 overflow-x-hidden">
      <section
        class="relative overflow-hidden rounded-3xl border border-slate-200 bg-[radial-gradient(circle_at_top_left,_rgba(14,116,144,0.14),_transparent_34%),linear-gradient(135deg,_#f8fafc_0%,_#ecfeff_42%,_#f8fafc_100%)] p-6 shadow-sm dark:border-gray-800 dark:bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.14),_transparent_34%),linear-gradient(135deg,_rgba(15,23,42,0.96)_0%,_rgba(8,47,73,0.92)_42%,_rgba(15,23,42,0.96)_100%)]">
        <div
          class="absolute inset-y-0 right-0 hidden w-72 translate-x-24 rounded-full bg-cyan-400/15 blur-3xl dark:block">
        </div>
        <div class="relative flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div class="max-w-2xl">
            <p class="text-sm font-semibold uppercase tracking-[0.24em] text-cyan-700 dark:text-cyan-300">
              {{ t('documents.category') }}
            </p>
            <h1 class="mt-2 font-serif text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">
              {{ t('documents.title') }}
            </h1>
            <p class="mt-3 max-w-xl text-sm leading-6 text-slate-600 dark:text-slate-300">
              {{ t('documents.subtitle') }}
            </p>
          </div>

          <div class="grid gap-3 sm:grid-cols-3 lg:min-w-[360px]">
            <div
              class="rounded-2xl border border-white/70 bg-white/75 px-4 py-3 backdrop-blur dark:border-white/10 dark:bg-white/5">
              <p class="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">{{ t('common.total') }}
              </p>
              <p class="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">{{ totalCount }}</p>
            </div>
            <div
              class="rounded-2xl border border-white/70 bg-white/75 px-4 py-3 backdrop-blur dark:border-white/10 dark:bg-white/5">
              <p class="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">{{
                t('documents.sourceFiles') }}</p>
              <p class="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">{{ fileCount }}</p>
            </div>
            <div
              class="rounded-2xl border border-white/70 bg-white/75 px-4 py-3 backdrop-blur dark:border-white/10 dark:bg-white/5">
              <p class="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">{{
                t('documents.sourceLinks') }}</p>
              <p class="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">{{ linkCount }}</p>
            </div>
          </div>
        </div>
      </section>

      <section
        class="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-white/[0.03]">
        <div class="flex flex-col gap-5">
          <div class="flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-700 dark:text-cyan-300">{{ t('documents.filtersTitle') }}</p>
              <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">{{ t('documents.filtersSubtitle') }}</p>
            </div>
            <button v-if="canCreate" type="button"
              class="inline-flex h-11 items-center justify-center gap-2 self-start rounded-xl bg-cyan-600 px-5 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-cyan-700 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/20"
              @click="openCreateModal">
              {{ t('documents.addDocument') }}
            </button>
          </div>

          <div class="grid gap-3 xl:grid-cols-[minmax(0,2.1fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,0.9fr)_auto_auto]">
            <input v-model="draftSearch" type="text" :placeholder="t('documents.searchPlaceholder')"
              class="h-11 rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-cyan-300 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90" />

            <details class="group relative">
              <summary
                class="flex h-11 cursor-pointer list-none items-center justify-between rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                <span class="truncate">{{ categoryFilterLabel }}</span>
                <ChevronDownIcon class="h-4 w-4 text-gray-400 transition group-open:rotate-180" />
              </summary>
              <div class="absolute left-0 top-full z-30 mt-2 w-full min-w-[18rem] rounded-2xl border border-gray-200 bg-white p-3 shadow-2xl dark:border-gray-700 dark:bg-gray-900">
                <div class="mb-3 flex items-center justify-between gap-3">
                  <div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                    <FunnelIcon class="h-3.5 w-3.5" />
                    {{ t('documents.categoryLabel') }}
                  </div>
                  <button type="button" class="text-xs font-medium text-cyan-700 transition hover:text-cyan-800 dark:text-cyan-300 dark:hover:text-cyan-200"
                    @click.prevent="clearCategorySelection">
                    {{ t('documents.clearFilter') }}
                  </button>
                </div>
                <div v-if="availableCategories.length === 0" class="rounded-xl bg-gray-50 px-3 py-4 text-sm text-gray-500 dark:bg-gray-950 dark:text-gray-400">
                  {{ t('documents.noCategoryOptions') }}
                </div>
                <div v-else class="max-h-64 space-y-1 overflow-auto pr-1">
                  <label v-for="category in availableCategories" :key="category"
                    class="flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-white/5">
                    <input type="checkbox" :checked="selectedCategories.includes(category)"
                      class="h-4 w-4 rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                      @change="toggleCategorySelection(category)" />
                    <span class="min-w-0 flex-1 truncate">{{ category }}</span>
                    <CheckIcon v-if="selectedCategories.includes(category)" class="h-4 w-4 text-cyan-600 dark:text-cyan-300" />
                  </label>
                </div>
              </div>
            </details>

            <details class="group relative">
              <summary
                class="flex h-11 cursor-pointer list-none items-center justify-between rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                <span class="truncate">{{ tagFilterLabel }}</span>
                <ChevronDownIcon class="h-4 w-4 text-gray-400 transition group-open:rotate-180" />
              </summary>
              <div class="absolute left-0 top-full z-30 mt-2 w-full min-w-[18rem] rounded-2xl border border-gray-200 bg-white p-3 shadow-2xl dark:border-gray-700 dark:bg-gray-900">
                <div class="mb-3 flex items-center justify-between gap-3">
                  <div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                    <FunnelIcon class="h-3.5 w-3.5" />
                    {{ t('documents.tagsLabel') }}
                  </div>
                  <button type="button" class="text-xs font-medium text-cyan-700 transition hover:text-cyan-800 dark:text-cyan-300 dark:hover:text-cyan-200"
                    @click.prevent="clearTagSelection">
                    {{ t('documents.clearFilter') }}
                  </button>
                </div>
                <div v-if="availableTags.length === 0" class="rounded-xl bg-gray-50 px-3 py-4 text-sm text-gray-500 dark:bg-gray-950 dark:text-gray-400">
                  {{ t('documents.noTagOptions') }}
                </div>
                <div v-else class="max-h-64 space-y-1 overflow-auto pr-1">
                  <label v-for="tag in availableTags" :key="tag"
                    class="flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-white/5">
                    <input type="checkbox" :checked="selectedTags.includes(tag)"
                      class="h-4 w-4 rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                      @change="toggleTagSelection(tag)" />
                    <span class="min-w-0 flex-1 truncate">{{ tag }}</span>
                    <CheckIcon v-if="selectedTags.includes(tag)" class="h-4 w-4 text-cyan-600 dark:text-cyan-300" />
                  </label>
                </div>
              </div>
            </details>

            <details class="group relative">
              <summary
                class="flex h-11 cursor-pointer list-none items-center justify-between rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs transition hover:bg-gray-50 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
                <span class="truncate">{{ sourceFilterLabel }}</span>
                <ChevronDownIcon class="h-4 w-4 text-gray-400 transition group-open:rotate-180" />
              </summary>
              <div class="absolute left-0 top-full z-30 mt-2 w-full min-w-[18rem] rounded-2xl border border-gray-200 bg-white p-3 shadow-2xl dark:border-gray-700 dark:bg-gray-900">
                <div class="mb-3 flex items-center justify-between gap-3">
                  <div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                    <FunnelIcon class="h-3.5 w-3.5" />
                    {{ t('documents.sourceType') }}
                  </div>
                  <button type="button" class="text-xs font-medium text-cyan-700 transition hover:text-cyan-800 dark:text-cyan-300 dark:hover:text-cyan-200"
                    @click.prevent="sourceTypeFilter = ''">
                    {{ t('documents.clearFilter') }}
                  </button>
                </div>
                <div class="space-y-1">
                  <button type="button"
                    class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-white/5"
                    @click="sourceTypeFilter = ''">
                    <span class="min-w-0 flex-1 truncate">{{ t('documents.sourceAll') }}</span>
                    <CheckIcon v-if="sourceTypeFilter === ''" class="h-4 w-4 text-cyan-600 dark:text-cyan-300" />
                  </button>
                  <button type="button"
                    class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-white/5"
                    @click="sourceTypeFilter = 'file'">
                    <span class="min-w-0 flex-1 truncate">{{ t('documents.sourceFiles') }}</span>
                    <CheckIcon v-if="sourceTypeFilter === 'file'" class="h-4 w-4 text-cyan-600 dark:text-cyan-300" />
                  </button>
                  <button type="button"
                    class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-white/5"
                    @click="sourceTypeFilter = 'link'">
                    <span class="min-w-0 flex-1 truncate">{{ t('documents.sourceLinks') }}</span>
                    <CheckIcon v-if="sourceTypeFilter === 'link'" class="h-4 w-4 text-cyan-600 dark:text-cyan-300" />
                  </button>
                </div>
              </div>
            </details>
            <label for="documents-pinned-only-filter" class="inline-flex h-11 cursor-pointer items-center gap-2 rounded-xl border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 shadow-theme-xs dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300">
              <input id="documents-pinned-only-filter" v-model="pinnedOnly" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-cyan-600 focus:ring-cyan-500" />
              {{ t('documents.pinnedOnly') }}
            </label>
            <div class="flex gap-2 xl:justify-end">
              <button type="button"
                class="h-11 rounded-xl border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-700 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:hover:bg-white/5"
                @click="resetFilters">
                {{ t('common.reset') }}
              </button>
            </div>
          </div>

          <div v-if="selectedCategories.length || selectedTags.length" class="flex flex-wrap gap-2">
            <button v-for="category in selectedCategories" :key="`selected-category-${category}`" type="button"
              class="inline-flex items-center gap-2 rounded-full bg-cyan-50 px-3 py-1.5 text-xs font-semibold text-cyan-700 transition hover:bg-cyan-100 dark:bg-cyan-500/10 dark:text-cyan-300 dark:hover:bg-cyan-500/20"
              @click="toggleCategorySelection(category)">
              <span>{{ category }}</span>
              <XIcon class="h-3.5 w-3.5" />
            </button>
            <button v-for="tag in selectedTags" :key="`selected-tag-${tag}`" type="button"
              class="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-300 dark:hover:bg-emerald-500/20"
              @click="toggleTagSelection(tag)">
              <span>#{{ tag }}</span>
              <XIcon class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </section>

      <section
        class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-white/[0.03]">
        <div v-if="errorMessage"
          class="border-b border-rose-200 bg-rose-50 px-6 py-4 text-sm text-rose-700 dark:border-rose-900/40 dark:bg-rose-900/20 dark:text-rose-200">
          {{ errorMessage }}
        </div>

        <div v-if="loading" class="px-6 py-16 text-center text-sm text-gray-500 dark:text-gray-400">
          {{ t('common.loading') }}
        </div>

        <div v-else-if="documents.length === 0" class="px-6 py-16 text-center">
          <div
            class="mx-auto max-w-md rounded-3xl border border-dashed border-gray-300 bg-gray-50 px-6 py-10 dark:border-gray-700 dark:bg-gray-900/40">
            <DocsIcon class="mx-auto h-10 w-10 text-gray-400 dark:text-gray-500" />
            <p class="mt-4 text-base font-semibold text-gray-900 dark:text-white">{{ t('documents.noDocumentsFound') }}
            </p>
            <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">{{ t('documents.emptyDescription') }}</p>
            <button v-if="canCreate" type="button"
              class="mt-5 inline-flex h-11 items-center gap-2 rounded-xl bg-cyan-600 px-5 text-sm font-semibold text-white transition hover:bg-cyan-700"
              @click="openCreateModal">
              {{ t('documents.addDocument') }}
            </button>
          </div>
        </div>

        <div v-else>
          <div v-if="selectedIds.length > 0" class="flex flex-wrap items-center gap-3 border-b border-gray-200 bg-cyan-50 px-4 py-3 dark:border-gray-800 dark:bg-cyan-500/10">
            <span class="text-sm font-medium text-cyan-700 dark:text-cyan-300">{{ t('documents.selected', { count: selectedIds.length }) }}</span>
            <div class="ml-auto flex flex-wrap gap-2">
              <button v-if="canUpdate" type="button" class="h-9 rounded-lg bg-cyan-600 px-4 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-50" :disabled="isBulkUpdating" @click="handleBulkPin(true)">
                {{ t('documents.pinSelected') }}
              </button>
              <button v-if="canUpdate" type="button" class="h-9 rounded-lg border border-cyan-300 bg-white px-4 text-sm font-semibold text-cyan-700 transition hover:bg-cyan-50 disabled:opacity-50 dark:border-cyan-500/30 dark:bg-gray-900 dark:text-cyan-300 dark:hover:bg-cyan-500/10" :disabled="isBulkUpdating" @click="handleBulkPin(false)">
                {{ t('documents.unpinSelected') }}
              </button>
              <button v-if="canDelete" type="button" class="h-9 rounded-lg bg-rose-600 px-4 text-sm font-semibold text-white transition hover:bg-rose-700 disabled:opacity-50" :disabled="isBulkUpdating" @click="openBulkDeleteModal">
                {{ t('documents.deleteSelected') }}
              </button>
              <button type="button" class="h-9 rounded-lg border border-gray-300 bg-white px-4 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5" @click="clearSelection">
                {{ t('documents.clearSelection') }}
              </button>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead class="border-b border-gray-200 bg-gray-50/80 dark:border-gray-800 dark:bg-gray-900/70">
                <tr>
                  <th v-if="canUpdate || canDelete" class="w-12 px-4 py-4 text-left">
                    <input type="checkbox" :checked="isAllCurrentPageSelected" :indeterminate="isPartiallySelected" @change="toggleSelectAll"
                      class="h-4 w-4 rounded border-gray-300 text-cyan-600 focus:ring-cyan-500 dark:border-gray-600 dark:bg-gray-800" />
                  </th>
                  <th class="px-6 py-4 text-left font-semibold text-gray-900 dark:text-white">
                    <button type="button" class="inline-flex items-center gap-2 transition hover:text-cyan-700 dark:hover:text-cyan-300" @click="toggleSort('title')">
                      <span>{{ t('common.name') }}</span>
                      <span class="text-xs font-medium text-gray-400 dark:text-gray-500">{{ sortIndicator('title') }}</span>
                    </button>
                  </th>
                  <th class="px-4 py-4 text-left font-semibold text-gray-900 dark:text-white">
                    <button type="button" class="inline-flex items-center gap-2 transition hover:text-cyan-700 dark:hover:text-cyan-300" @click="toggleSort('source_type')">
                      <span>{{ t('documents.sourceType') }}</span>
                      <span class="text-xs font-medium text-gray-400 dark:text-gray-500">{{ sortIndicator('source_type') }}</span>
                    </button>
                  </th>
                  <th class="px-4 py-4 text-left font-semibold text-gray-900 dark:text-white">{{
                    t('documents.categoryLabel') }}</th>
                  <th class="px-4 py-4 text-left font-semibold text-gray-900 dark:text-white">{{
                    t('documents.tagsLabel') }}</th>
                  <th class="px-4 py-4 text-left font-semibold text-gray-900 dark:text-white">{{
                    t('documents.metaLabel') }}</th>
                  <th class="px-4 py-4 text-center font-semibold text-gray-900 dark:text-white">{{ t('common.actions')
                  }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
                <tr v-for="document in documents" :key="document.id" class="cursor-pointer hover:bg-gray-50/80 dark:hover:bg-white/5"
                  :class="{ 'bg-cyan-50/60 dark:bg-cyan-500/5': selectedIds.includes(document.id) }" @click="openDetails(document)">
                  <td v-if="canUpdate || canDelete" class="px-4 py-4" @click.stop>
                    <input type="checkbox" :checked="selectedIds.includes(document.id)" @change="toggleSelect(document.id)"
                      class="h-4 w-4 rounded border-gray-300 text-cyan-600 focus:ring-cyan-500 dark:border-gray-600 dark:bg-gray-800" />
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-start gap-3 text-left">
                      <span class="mt-0.5 inline-flex h-11 w-11 items-center justify-center rounded-2xl" :class="document.preview_type === 'image'
                        ? 'bg-cyan-100 text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-300'
                        : document.preview_type === 'pdf'
                          ? 'bg-rose-100 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300'
                          : document.preview_type === 'text'
                            ? 'bg-sky-100 text-sky-700 dark:bg-sky-500/10 dark:text-sky-300'
                            : document.preview_type === 'csv'
                              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'
                          : document.is_external
                            ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'
                            : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'">
                        <ImageIcon v-if="document.preview_type === 'image'" class="h-5 w-5" />
                        <PageIcon v-else-if="document.preview_type === 'pdf'" class="h-5 w-5" />
                        <DocsIcon v-else-if="document.preview_type === 'text'" class="h-5 w-5" />
                        <PageIcon v-else-if="document.preview_type === 'csv'" class="h-5 w-5" />
                        <PaperclipIcon v-else-if="document.is_external" class="h-5 w-5" />
                        <DocsIcon v-else class="h-5 w-5" />
                      </span>
                      <span class="min-w-0">
                        <span class="flex items-center gap-2">
                          <span class="truncate font-semibold text-gray-900 dark:text-white">{{ document.title }}</span>
                          <span v-if="document.is_pinned"
                            class="rounded-full bg-cyan-100 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-300">
                            {{ t('documents.pinned') }}
                          </span>
                        </span>
                        <span class="mt-1 block text-xs text-gray-500 dark:text-gray-400">
                          {{ document.original_filename || document.host || '—' }}
                        </span>
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-4">
                    <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="document.is_external
                      ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'
                      : 'bg-slate-100 text-slate-700 dark:bg-slate-700/70 dark:text-slate-200'">
                      {{ sourceLabel(document.source_type) }}
                    </span>
                  </td>
                  <td class="px-4 py-4 text-gray-700 dark:text-gray-300">{{ document.category || '—' }}</td>
                  <td class="px-4 py-4">
                    <div class="flex flex-wrap gap-1.5">
                      <span v-for="tag in document.tags.slice(0, 3)" :key="tag"
                        class="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                        {{ tag }}
                      </span>
                      <span v-if="document.tags.length === 0" class="text-gray-400">—</span>
                    </div>
                  </td>
                  <td class="px-4 py-4 text-gray-700 dark:text-gray-300">
                    <div v-if="document.is_external">{{ document.link_site_name || document.host || '—' }}</div>
                    <div v-else>{{ formatBytes(document.stored_file_size) }}</div>
                  </td>
                  <td class="px-4 py-4" @click.stop>
                    <div class="flex justify-center gap-2">
                      <button type="button"
                        class="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-gray-300 text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
                        :title="t('documents.viewDetails')" :aria-label="t('documents.viewDetails')"
                        @click="openDetails(document)">
                        <InfoCircleIcon class="h-4 w-4" />
                      </button>
                      <button type="button"
                        class="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-gray-300 text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
                        :title="document.is_external ? t('documents.openLink') : t('common.download')" :aria-label="document.is_external ? t('documents.openLink') : t('common.download')"
                        @click="handleOpen(document)">
                        <component :is="document.is_external ? PaperclipIcon : DownloadIcon" class="h-4 w-4" />
                      </button>
                      <button v-if="document.is_external" type="button"
                        class="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-gray-300 text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
                        :title="t('documents.copyLink')" :aria-label="t('documents.copyLink')"
                        @click="copyDocumentLink(document)">
                        <ClipboardIcon class="h-4 w-4" />
                      </button>
                      <button v-if="canUpdate" type="button"
                        class="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-300 text-cyan-700 transition hover:bg-cyan-50 dark:border-cyan-500/30 dark:text-cyan-300 dark:hover:bg-cyan-500/10"
                        :title="document.is_pinned ? t('documents.unpin') : t('documents.pin')" :aria-label="document.is_pinned ? t('documents.unpin') : t('documents.pin')"
                        @click="togglePin(document)">
                        <StaredIcon class="h-4 w-4" />
                      </button>
                      <button v-if="canUpdate" type="button"
                        class="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-brand-300 text-brand-600 transition hover:bg-brand-50 dark:border-brand-500/30 dark:text-brand-300 dark:hover:bg-brand-500/10"
                        :title="t('common.edit')" :aria-label="t('common.edit')"
                        @click="openEditModal(document)">
                        <PencilIcon class="h-4 w-4" />
                      </button>
                      <button v-if="canDelete" type="button"
                        class="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-rose-300 text-rose-600 transition hover:bg-rose-50 dark:border-rose-500/30 dark:text-rose-300 dark:hover:bg-rose-500/10"
                        :title="t('common.delete')" :aria-label="t('common.delete')"
                        @click="openDeleteModal(document)">
                        <TrashIcon class="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div
            class="flex flex-col gap-3 border-t border-gray-200 px-6 py-4 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-center gap-3">
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ t('common.showing') }} {{ rangeStart }}-{{ rangeEnd }} {{ t('common.of') }} {{ totalCount }}
              </p>
              <select v-model.number="pageSize"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                @change="handlePageSizeChange">
                <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} / {{ t('common.page') }}
                </option>
              </select>
            </div>
            <div class="flex items-center gap-2">
              <button type="button"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5"
                :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
                {{ t('common.prev') }}
              </button>
              <span class="text-sm text-gray-600 dark:text-gray-400">{{ currentPage }} / {{ totalPages }}</span>
              <button type="button"
                class="h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-800 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5"
                :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
                {{ t('common.next') }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <div v-if="showFormModal" class="fixed inset-0 z-[100000] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" @click="closeFormModal"></div>
        <div
          class="relative z-10 flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-900">
          <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-800">
            <div>
              <h2 class="font-serif text-2xl font-semibold text-gray-900 dark:text-white">
                {{ editingId ? t('documents.editTitle') : t('documents.createTitle') }}
              </h2>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ form.source_type === 'file' ?
                t('documents.fileHint') : t('documents.linkHint') }}</p>
            </div>
            <button type="button" class="text-gray-400 transition hover:text-gray-600 dark:hover:text-gray-200"
              @click="closeFormModal">
              <XIcon class="h-6 w-6" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto px-6 py-5">
            <div v-if="formError"
              class="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900/50 dark:bg-rose-900/20 dark:text-rose-200">
              {{ formError }}
            </div>

            <div class="mb-5 grid gap-2 sm:grid-cols-2">
              <button type="button" class="rounded-2xl border px-4 py-4 text-left transition" :class="form.source_type === 'file'
                ? 'border-cyan-500 bg-cyan-50 text-cyan-900 dark:bg-cyan-500/10 dark:text-cyan-100'
                : 'border-gray-200 bg-white text-gray-700 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300'"
                @click="form.source_type = 'file'">
                <p class="font-semibold">{{ t('documents.uploadFile') }}</p>
                <p class="mt-1 text-xs opacity-80">{{ t('documents.fileHint') }}</p>
              </button>
              <button type="button" class="rounded-2xl border px-4 py-4 text-left transition" :class="form.source_type === 'link'
                ? 'border-cyan-500 bg-cyan-50 text-cyan-900 dark:bg-cyan-500/10 dark:text-cyan-100'
                : 'border-gray-200 bg-white text-gray-700 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300'"
                @click="form.source_type = 'link'">
                <p class="font-semibold">{{ t('documents.saveLink') }}</p>
                <p class="mt-1 text-xs opacity-80">{{ t('documents.linkHint') }}</p>
              </button>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="space-y-2 sm:col-span-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('common.name') }}</label>
                <input v-model="form.title" type="text"
                  class="h-11 w-full rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs focus:border-cyan-300 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white/90" />
              </div>

              <div v-if="form.source_type === 'file'" class="space-y-2 sm:col-span-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('documents.uploadFile')
                }}</label>
                <input type="file"
                  class="block w-full rounded-xl border border-dashed border-gray-300 bg-gray-50 px-4 py-4 text-sm text-gray-700 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-300"
                  @change="handleFileChange" />
                <p v-if="editingDocument?.original_filename && !form.file"
                  class="text-xs text-gray-500 dark:text-gray-400">
                  {{ t('documents.currentFile') }}: {{ editingDocument.original_filename }}
                </p>
              </div>

              <div v-else class="space-y-2 sm:col-span-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('documents.externalUrl')
                }}</label>
                <input v-model="form.external_url" type="url"
                  class="h-11 w-full rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs focus:border-cyan-300 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white/90" />
              </div>

              <div class="space-y-2 sm:col-span-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('documents.categoryLabel')
                }}</label>
                <input v-model="form.category" type="text" :placeholder="t('documents.categoryPlaceholder')"
                  class="h-11 w-full rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs focus:border-cyan-300 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white/90" />
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('documents.tagsLabel')
                }}</label>
                <input v-model="form.tagsText" type="text" :placeholder="t('documents.tagsPlaceholder')"
                  class="h-11 w-full rounded-xl border border-gray-300 bg-white px-4 text-sm text-gray-800 shadow-theme-xs focus:border-cyan-300 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white/90" />
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('documents.tagsHelp') }}</p>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('documents.pinned') }}</label>
                <label
                  class="inline-flex h-11 w-full items-center gap-3 rounded-xl border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-300">
                  <input v-model="form.is_pinned" type="checkbox"
                    class="h-4 w-4 rounded border-gray-300 text-cyan-600 focus:ring-cyan-500" />
                  {{ t('documents.pinned') }}
                </label>
              </div>

              <div class="space-y-2 sm:col-span-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('common.description')
                }}</label>
                <textarea v-model="form.description" rows="4" :placeholder="t('documents.descriptionPlaceholder')"
                  class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-sm text-gray-800 shadow-theme-xs focus:border-cyan-300 focus:outline-hidden focus:ring-3 focus:ring-cyan-500/10 dark:border-gray-700 dark:bg-gray-950 dark:text-white/90"></textarea>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 border-t border-gray-200 px-6 py-4 dark:border-gray-800">
            <button type="button"
              class="rounded-xl border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
              @click="closeFormModal">
              {{ t('common.cancel') }}
            </button>
            <button type="button"
              class="rounded-xl bg-cyan-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-50"
              :disabled="formSaving" @click="saveDocument">
              {{ formSaving ? t('common.saving') : t('common.save') }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="showDetailModal" class="fixed inset-0 z-[100000] flex items-center justify-center overflow-hidden"
        :class="isDetailFullscreen ? '' : 'p-4'">
        <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" @click="closeDetails"></div>
        <div :class="[
          'relative z-10 flex flex-col overflow-hidden bg-white shadow-2xl transition-[width,height,border-radius] duration-300 dark:bg-gray-900',
          isDetailFullscreen
            ? 'fixed inset-0 h-full w-full'
            : 'max-h-[92vh] w-full max-w-6xl rounded-3xl border border-gray-200 dark:border-gray-700'
        ]">
          <div class="sticky top-0 z-20 flex items-center justify-between border-b border-gray-200 bg-white/95 px-6 py-4 backdrop-blur dark:border-gray-800 dark:bg-gray-900/95">
            <div class="min-w-0">
              <h2 class="font-serif text-2xl font-semibold text-gray-900 dark:text-white">{{ t('documents.detailsTitle') }}</h2>
              <p class="mt-1 truncate text-sm text-gray-500 dark:text-gray-400">{{ selectedDocument?.title }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button type="button"
                class="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                :title="isDetailFullscreen ? t('documents.exitFullscreen') : t('documents.enterFullscreen')"
                :aria-label="isDetailFullscreen ? t('documents.exitFullscreen') : t('documents.enterFullscreen')"
                @click="toggleDetailsFullscreen">
                <svg v-if="!isDetailFullscreen" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
                <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                </svg>
              </button>
              <button type="button"
                class="rounded-lg p-2 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-200"
                @click="closeDetails">
                <XIcon class="h-6 w-6" />
              </button>
            </div>
          </div>

          <div class="min-h-0 flex-1 overflow-y-auto px-6 py-5">
            <div v-if="detailLoading" class="py-16 text-center text-sm text-gray-500 dark:text-gray-400">
              {{ t('common.loading') }}
            </div>
            <div v-else-if="selectedDocument" class="grid gap-6" :class="selectedDocument.is_external ? 'lg:grid-cols-[minmax(0,1.2fr)_minmax(18rem,0.8fr)]' : 'lg:grid-cols-[minmax(0,1.45fr)_minmax(20rem,0.95fr)]'">
              <div v-if="!selectedDocument.is_external">
                <div
                  class="overflow-hidden rounded-3xl border border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-950">
                  <img v-if="selectedDocument.preview_type === 'image' && selectedDocument.file_url"
                    :src="selectedDocument.file_url" :alt="selectedDocument.title"
                    class="max-h-[28rem] w-full object-contain bg-white dark:bg-gray-950" />
                  <iframe v-else-if="selectedDocument.preview_type === 'pdf' && selectedDocument.file_url"
                    :src="selectedDocument.file_url" class="h-[28rem] w-full bg-white"></iframe>
                  <div v-else-if="selectedDocument.preview_type === 'text'"
                    class="h-[28rem] overflow-auto bg-slate-950">
                    <div v-if="inlinePreviewLoading" class="flex h-full items-center justify-center px-8 text-sm text-slate-300">
                      {{ t('common.loading') }}
                    </div>
                    <div v-else-if="inlinePreviewError" class="flex h-full flex-col items-center justify-center px-8 text-center">
                      <DocsIcon class="h-10 w-10 text-slate-500" />
                      <p class="mt-4 text-base font-semibold text-white">{{ t('documents.previewUnavailable') }}</p>
                      <p class="mt-2 text-sm text-slate-300">{{ inlinePreviewError }}</p>
                    </div>
                    <div v-else class="h-full overflow-auto px-5 py-4">
                      <pre class="whitespace-pre-wrap break-words font-mono text-[13px] leading-6 text-slate-100">{{ inlinePreviewText || t('documents.previewEmpty') }}</pre>
                    </div>
                  </div>
                  <div v-else-if="selectedDocument.preview_type === 'csv'"
                    class="h-[28rem] overflow-hidden bg-white dark:bg-gray-950">
                    <div v-if="inlinePreviewLoading" class="flex h-full items-center justify-center px-8 text-sm text-gray-500 dark:text-gray-400">
                      {{ t('common.loading') }}
                    </div>
                    <div v-else-if="inlinePreviewError" class="flex h-full flex-col items-center justify-center px-8 text-center">
                      <DocsIcon class="h-10 w-10 text-gray-400 dark:text-gray-500" />
                      <p class="mt-4 text-base font-semibold text-gray-900 dark:text-white">{{ t('documents.previewUnavailable') }}</p>
                      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">{{ inlinePreviewError }}</p>
                    </div>
                    <div v-else-if="inlinePreviewRows.length === 0" class="flex h-full items-center justify-center px-8 text-sm text-gray-500 dark:text-gray-400">
                      {{ t('documents.previewEmpty') }}
                    </div>
                    <div v-else class="h-full overflow-auto">
                      <table class="min-w-full divide-y divide-gray-200 text-sm dark:divide-gray-800">
                        <tbody class="divide-y divide-gray-100 dark:divide-gray-900/60">
                          <tr v-for="(row, rowIndex) in inlinePreviewRows" :key="`row-${rowIndex}`" class="align-top">
                            <td v-for="(cell, cellIndex) in row" :key="`cell-${rowIndex}-${cellIndex}`"
                              class="max-w-[220px] whitespace-pre-wrap break-words border-r border-gray-100 px-3 py-2 font-mono text-xs text-gray-700 last:border-r-0 dark:border-gray-800 dark:text-gray-200">
                              {{ cell || ' ' }}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div v-else class="flex h-[28rem] flex-col items-center justify-center px-8 text-center">
                    <DocsIcon class="h-10 w-10 text-gray-400 dark:text-gray-500" />
                    <p class="mt-4 text-base font-semibold text-gray-900 dark:text-white">{{ t('documents.previewUnavailable') }}</p>
                    <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">{{ t('documents.previewUnavailableHelp') }}</p>
                  </div>
                </div>
              </div>

              <div class="space-y-4">
                <template v-if="selectedDocument.is_external">
                  <div class="rounded-3xl border border-amber-200 bg-[linear-gradient(135deg,_rgba(255,251,235,0.95)_0%,_rgba(255,247,237,0.92)_100%)] p-5 dark:border-amber-500/20 dark:bg-[linear-gradient(135deg,_rgba(69,26,3,0.22)_0%,_rgba(31,41,55,0.55)_100%)]">
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-amber-700 dark:text-amber-300">{{ t('documents.linkTarget') }}</p>
                    <p class="mt-3 break-all text-base font-semibold text-slate-900 dark:text-white">{{ selectedDocument.external_url }}</p>
                  </div>

                  <div class="rounded-3xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-800 dark:bg-gray-950">
                    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-700 dark:text-cyan-300">{{ t('common.description') }}</p>
                    <p class="mt-3 whitespace-pre-wrap text-sm leading-6 text-gray-700 dark:text-gray-300">{{ selectedDocument.description || '—' }}</p>
                  </div>
				</template>

                <div v-else class="rounded-3xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-950">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('documents.sourceType') }}</p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="selectedDocument.is_external
                        ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'
                        : 'bg-slate-100 text-slate-700 dark:bg-slate-700/70 dark:text-slate-200'">
                        {{ sourceLabel(selectedDocument.source_type) }}
                      </span>
                      <span v-if="selectedDocument.category" class="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-300">
                        {{ selectedDocument.category }}
                      </span>
                      <span v-if="selectedDocument.is_pinned" class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                        {{ t('documents.pinned') }}
                      </span>
                    </div>
                  </div>

                  <dl class="mt-5 grid gap-3 sm:grid-cols-2">
                    <div v-for="item in detailInfoItems" :key="item.label" class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900/70" :class="item.fullWidth ? 'sm:col-span-2' : ''">
                      <dt class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ item.label }}</dt>
                      <dd class="mt-1 text-sm font-medium text-gray-900 dark:text-white" :class="item.breakAll ? 'break-all' : ''">{{ item.value }}</dd>
                    </div>

                    <div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900/70 sm:col-span-2">
                      <dt class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('documents.tagsLabel') }}</dt>
                      <dd class="mt-2 flex flex-wrap gap-1.5">
                        <span v-for="tag in selectedDocument.tags" :key="tag"
                          class="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-gray-700 shadow-theme-xs dark:bg-gray-800 dark:text-gray-300">{{ tag }}</span>
                        <span v-if="selectedDocument.tags.length === 0" class="text-sm text-gray-400">—</span>
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>

              <div v-if="selectedDocument.is_external" class="rounded-3xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-950">
                <div class="grid gap-3 sm:grid-cols-2">
                  <div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900/70">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('documents.siteName') }}</p>
                    <p class="mt-1 text-sm font-medium text-gray-900 dark:text-white">{{ selectedDocument.link_site_name || selectedDocument.host || '—' }}</p>
                  </div>
                  <div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900/70">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('documents.createdBy') }}</p>
                    <p class="mt-1 text-sm font-medium text-gray-900 dark:text-white">{{ selectedDocument.created_by_name || '—' }}</p>
                  </div>
                  <div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900/70">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('documents.createdAt') }}</p>
                    <p class="mt-1 text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(selectedDocument.created_at) }}</p>
                  </div>
                  <div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900/70">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('documents.updatedAt') }}</p>
                    <p class="mt-1 text-sm font-medium text-gray-900 dark:text-white">{{ formatDate(selectedDocument.updated_at) }}</p>
                  </div>
                  <div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900/70 sm:col-span-2">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">{{ t('documents.tagsLabel') }}</p>
                    <div class="mt-2 flex flex-wrap gap-1.5">
                      <span v-for="tag in selectedDocument.tags" :key="tag"
                        class="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-gray-700 shadow-theme-xs dark:bg-gray-800 dark:text-gray-300">{{ tag }}</span>
                      <span v-if="selectedDocument.tags.length === 0" class="text-sm text-gray-400">—</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="!selectedDocument.is_external" class="lg:col-span-2 rounded-3xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-800 dark:bg-gray-950">
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-700 dark:text-cyan-300">{{ t('common.description') }}</p>
                <p class="mt-3 whitespace-pre-wrap text-sm leading-6 text-gray-700 dark:text-gray-300">{{ selectedDocument.description || '—' }}</p>
                <div v-if="selectedDocument.preview_type === 'text' || selectedDocument.preview_type === 'csv'" class="mt-4 space-y-2">
                  <p v-if="inlinePreviewTruncated" class="text-xs font-medium text-amber-700 dark:text-amber-300">{{ t('documents.previewTruncated') }}</p>
                  <p v-if="inlinePreviewRowLimitReached" class="text-xs font-medium text-amber-700 dark:text-amber-300">{{ t('documents.csvRowLimitNotice', { count: MAX_CSV_PREVIEW_ROWS }) }}</p>
                  <p v-if="inlinePreviewColumnLimitReached" class="text-xs font-medium text-amber-700 dark:text-amber-300">{{ t('documents.csvColumnLimitNotice', { count: MAX_CSV_PREVIEW_COLUMNS }) }}</p>
                </div>
              </div>

            </div>
          </div>

          <div v-if="selectedDocument" class="sticky bottom-0 z-20 border-t border-gray-200 bg-white/95 px-6 py-4 backdrop-blur dark:border-gray-800 dark:bg-gray-900/95">
            <div class="flex flex-wrap items-center justify-end gap-3">
              <button type="button"
                class="rounded-xl bg-cyan-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-cyan-700"
                @click="handleOpen(selectedDocument)">
                {{ selectedDocument.is_external ? t('documents.openLink') : t('common.download') }}
              </button>
              <button v-if="selectedDocument.is_external" type="button"
                class="inline-flex items-center gap-2 rounded-xl border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
                @click="copyDocumentLink(selectedDocument)">
                <ClipboardIcon class="h-4 w-4" />
                {{ t('documents.copyLink') }}
              </button>
              <button v-if="canUpdate" type="button"
                class="inline-flex items-center gap-2 rounded-xl border border-brand-300 px-4 py-2 text-sm font-medium text-brand-600 transition hover:bg-brand-50 dark:border-brand-500/30 dark:text-brand-300 dark:hover:bg-brand-500/10"
                @click="editFromDetails">
                <PencilIcon class="h-4 w-4" />
                {{ t('common.edit') }}
              </button>
              <button v-if="canDelete" type="button"
                class="inline-flex items-center gap-2 rounded-xl border border-rose-300 px-4 py-2 text-sm font-medium text-rose-600 transition hover:bg-rose-50 dark:border-rose-500/30 dark:text-rose-300 dark:hover:bg-rose-500/10"
                @click="openDeleteFromDetails">
                <TrashIcon class="h-4 w-4" />
                {{ t('common.delete') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showDeleteModal && pendingDeleteDocument" class="fixed inset-0 z-[100000] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="closeDeleteModal"></div>
        <div class="relative z-10 w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-900">
          <h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">{{ t('documents.deleteConfirmTitle') }}</h2>
          <p class="mb-6 text-gray-600 dark:text-gray-300">{{ t('documents.deleteConfirmMessage') }}</p>
          <div class="flex gap-3">
            <button @click="closeDeleteModal" class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.cancel') }}
            </button>
            <button @click="confirmDelete" :disabled="isDeleting" class="h-11 flex-1 rounded-lg bg-error-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 disabled:opacity-50">
              {{ isDeleting ? t('common.deleting') : t('common.delete') }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="showBulkDeleteModal" class="fixed inset-0 z-[100000] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showBulkDeleteModal = false"></div>
        <div class="relative z-10 w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-900">
          <h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">{{ t('documents.deleteSelectedTitle') }}</h2>
          <p class="mb-6 text-gray-600 dark:text-gray-300">{{ t('documents.deleteSelectedMessage', { count: selectedIds.length }) }}</p>
          <div class="flex gap-3">
            <button @click="showBulkDeleteModal = false" class="h-11 flex-1 rounded-lg border border-gray-300 bg-white px-6 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:hover:bg-white/5">
              {{ t('common.cancel') }}
            </button>
            <button @click="confirmBulkDelete" :disabled="isDeleting || isBulkUpdating" class="h-11 flex-1 rounded-lg bg-error-600 px-6 text-sm font-semibold text-white shadow-theme-xs transition hover:bg-error-700 disabled:opacity-50">
              {{ isDeleting || isBulkUpdating ? t('common.deleting') : t('documents.deleteSelected') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import { useToast } from '@/composables/useToast'
import { usePagePermission } from '@/composables/usePagePermission'
import {
  CheckIcon,
  ChevronDownIcon,
  DownloadIcon,
  FunnelIcon,
  ClipboardIcon,
  DocsIcon,
  ImageIcon,
  InfoCircleIcon,
  PageIcon,
  PaperclipIcon,
  PencilIcon,
  StaredIcon,
  TrashIcon,
  XIcon,
} from '@/icons'
import {
  documentAPI,
  type DocumentFilterOptions,
  type DocumentDetail,
  type DocumentSourceType,
  type DocumentSummary,
} from '@/services/api/documents'
import { extractApiError } from '@/utils/extractApiError'
import { toSafeExternalUrl } from '@/utils/safeUrl'

type DocumentFormState = {
  source_type: DocumentSourceType
  title: string
  description: string
  external_url: string
  category: string
  tagsText: string
  is_pinned: boolean
  file: File | null
}

type DetailInfoItem = {
  label: string
  value: string
  fullWidth?: boolean
  breakAll?: boolean
}

const { t } = useI18n()
const { showToast } = useToast()
const { canCreate, canUpdate, canDelete } = usePagePermission('documents')

const documents = ref<DocumentSummary[]>([])
const selectedDocument = ref<DocumentDetail | null>(null)
const editingDocument = ref<DocumentDetail | null>(null)
const loading = ref(false)
const detailLoading = ref(false)
const formSaving = ref(false)
const showFormModal = ref(false)
const showDetailModal = ref(false)
const isDetailFullscreen = ref(false)
const showDeleteModal = ref(false)
const showBulkDeleteModal = ref(false)
const errorMessage = ref('')
const formError = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const totalPages = ref(1)
const editingId = ref<number | null>(null)
const isDeleting = ref(false)
const isBulkUpdating = ref(false)
const pendingDeleteDocument = ref<DocumentSummary | null>(null)
const selectedIds = ref<number[]>([])
const inlinePreviewLoading = ref(false)
const inlinePreviewError = ref('')
const inlinePreviewText = ref('')
const inlinePreviewRows = ref<string[][]>([])
const inlinePreviewTruncated = ref(false)
const inlinePreviewRowLimitReached = ref(false)
const inlinePreviewColumnLimitReached = ref(false)
const availableCategories = ref<string[]>([])
const availableTags = ref<string[]>([])

const draftSearch = ref('')
const selectedCategories = ref<string[]>([])
const selectedTags = ref<string[]>([])
const searchQuery = ref('')
const categoryFilter = ref<string[]>([])
const tagFilter = ref<string[]>([])
const sourceTypeFilter = ref<DocumentSourceType | ''>('')
const pinnedOnly = ref(false)
const sortField = ref<'title' | 'source_type'>('title')
const sortDirection = ref<'asc' | 'desc'>('asc')

const pageSizeOptions = [10, 25, 50]
const MAX_INLINE_PREVIEW_BYTES = 1024 * 1024
const MAX_TEXT_PREVIEW_CHARACTERS = 20000
const MAX_CSV_PREVIEW_ROWS = 50
const MAX_CSV_PREVIEW_COLUMNS = 12

let inlinePreviewRequestId = 0
let filterDebounceTimer: ReturnType<typeof setTimeout> | null = null

const form = reactive<DocumentFormState>({
  source_type: 'file',
  title: '',
  description: '',
  external_url: '',
  category: '',
  tagsText: '',
  is_pinned: false,
  file: null,
})

const fileCount = computed(() => documents.value.filter((item) => item.source_type === 'file').length)
const linkCount = computed(() => documents.value.filter((item) => item.source_type === 'link').length)
const rangeStart = computed(() => (totalCount.value === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1))
const rangeEnd = computed(() => Math.min(currentPage.value * pageSize.value, totalCount.value))
const categoryFilterLabel = computed(() => buildFilterLabel(selectedCategories.value, t('documents.allCategories')))
const tagFilterLabel = computed(() => buildFilterLabel(selectedTags.value, t('documents.allTags')))
const sourceFilterLabel = computed(() => {
  if (sourceTypeFilter.value === 'file') return t('documents.sourceFiles')
  if (sourceTypeFilter.value === 'link') return t('documents.sourceLinks')
  return t('documents.sourceAll')
})
const isAllCurrentPageSelected = computed(() =>
  documents.value.length > 0 && documents.value.every((item) => selectedIds.value.includes(item.id)),
)
const isPartiallySelected = computed(() => {
  const count = documents.value.filter((item) => selectedIds.value.includes(item.id)).length
  return count > 0 && count < documents.value.length
})
const detailInfoItems = computed<DetailInfoItem[]>(() => {
  if (!selectedDocument.value) return []

  const document = selectedDocument.value
  const items: DetailInfoItem[] = [
    {
      label: t('documents.createdBy'),
      value: document.created_by_name || '—',
    },
  ]

  if (document.is_external) {
    items.unshift(
      {
        label: t('documents.siteName'),
        value: document.link_site_name || document.host || '—',
      },
      {
        label: t('documents.linkTarget'),
        value: document.external_url || '—',
        fullWidth: true,
        breakAll: true,
      },
    )
  } else {
    items.unshift(
      {
        label: t('documents.fileName'),
        value: document.original_filename || '—',
        fullWidth: true,
        breakAll: true,
      },
      {
        label: t('documents.fileSize'),
        value: formatBytes(document.stored_file_size),
      },
    )
  }

  items.push(
    {
      label: t('documents.createdAt'),
      value: formatDate(document.created_at),
    },
    {
      label: t('documents.updatedAt'),
      value: formatDate(document.updated_at),
    },
  )

  return items
})

function sourceLabel(sourceType: DocumentSourceType) {
  return sourceType === 'link' ? t('documents.sourceLinks') : t('documents.sourceFiles')
}

function sortIndicator(field: 'title' | 'source_type') {
  if (sortField.value !== field) return '↕'
  return sortDirection.value === 'asc' ? '↑' : '↓'
}

function toggleSort(field: 'title' | 'source_type') {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
  currentPage.value = 1
  void loadDocuments()
}

function buildOrderingValue() {
  const sortPrefix = sortDirection.value === 'desc' ? '-' : ''
  return `-is_pinned,${sortPrefix}${sortField.value}`
}

function formatBytes(size: number | null) {
  if (!size) return '—'
  const units = ['B', 'KB', 'MB', 'GB']
  let value = size
  let unitIndex = 0
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }
  return `${value.toFixed(value >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function buildTags() {
  return form.tagsText
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function buildFilterLabel(values: string[], emptyLabel: string) {
  if (values.length === 0) return emptyLabel
  if (values.length === 1) return values[0]
  if (values.length === 2) return `${values[0]}, ${values[1]}`
  return t('documents.filterSelectionCount', { count: values.length })
}

function toggleSelection(values: string[], value: string) {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value]
}

function toggleCategorySelection(category: string) {
  selectedCategories.value = toggleSelection(selectedCategories.value, category)
}

function toggleTagSelection(tag: string) {
  selectedTags.value = toggleSelection(selectedTags.value, tag)
}

function clearCategorySelection() {
  selectedCategories.value = []
}

function clearTagSelection() {
  selectedTags.value = []
}

async function loadFilterOptions() {
  try {
    const data: DocumentFilterOptions = await documentAPI.getFilterOptions()
    availableCategories.value = data.categories
    availableTags.value = data.tags
  } catch {
    availableCategories.value = []
    availableTags.value = []
  }
}

function scheduleFilterApply() {
  if (filterDebounceTimer) {
    clearTimeout(filterDebounceTimer)
  }
  filterDebounceTimer = setTimeout(() => {
    applyFilters()
  }, 250)
}

function resetInlinePreview(cancelPending = true) {
  if (cancelPending) {
    inlinePreviewRequestId += 1
  }
  inlinePreviewLoading.value = false
  inlinePreviewError.value = ''
  inlinePreviewText.value = ''
  inlinePreviewRows.value = []
  inlinePreviewTruncated.value = false
  inlinePreviewRowLimitReached.value = false
  inlinePreviewColumnLimitReached.value = false
}

function getDocumentExtension(document: DocumentSummary | DocumentDetail) {
  return (document.extension || document.original_filename.split('.').pop() || '').toLowerCase().replace(/^\./, '')
}

function formatTextPreview(document: DocumentSummary | DocumentDetail, rawContent: string) {
  const normalized = rawContent.replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n')
  const extension = getDocumentExtension(document)

  if (extension === 'json' || (document.mime_type || '').toLowerCase() === 'application/json') {
    try {
      return JSON.stringify(JSON.parse(normalized), null, 2)
    } catch {
      return normalized
    }
  }

  return normalized
}

function parseCsvPreview(rawContent: string) {
  const text = rawContent.replace(/^\uFEFF/, '')
  const rows: string[][] = []
  let currentRow: string[] = []
  let currentCell = ''
  let inQuotes = false
  let rowLimitReached = false
  let columnLimitReached = false

  const pushRow = () => {
    const normalizedRow = [...currentRow, currentCell]
    if (normalizedRow.length > MAX_CSV_PREVIEW_COLUMNS) {
      columnLimitReached = true
    }
    rows.push(normalizedRow.slice(0, MAX_CSV_PREVIEW_COLUMNS))
    currentRow = []
    currentCell = ''
    if (rows.length >= MAX_CSV_PREVIEW_ROWS) {
      rowLimitReached = true
    }
  }

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index]
    const nextChar = text[index + 1]

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        currentCell += '"'
        index += 1
      } else {
        inQuotes = !inQuotes
      }
      continue
    }

    if (!inQuotes && char === ',') {
      currentRow.push(currentCell)
      currentCell = ''
      continue
    }

    if (!inQuotes && (char === '\n' || char === '\r')) {
      if (char === '\r' && nextChar === '\n') {
        index += 1
      }
      pushRow()
      if (rowLimitReached) {
        break
      }
      continue
    }

    currentCell += char
  }

  if (!rowLimitReached && (currentCell.length > 0 || currentRow.length > 0 || text.endsWith(','))) {
    pushRow()
  }

  return {
    rows,
    rowLimitReached,
    columnLimitReached,
  }
}

async function loadInlinePreview(document: DocumentDetail) {
  resetInlinePreview(false)
  if (!document.file_url || !document.can_preview || !document.preview_type || !['text', 'csv'].includes(document.preview_type)) {
    return
  }

  if ((document.stored_file_size ?? 0) > MAX_INLINE_PREVIEW_BYTES) {
    inlinePreviewError.value = t('documents.previewTooLarge')
    return
  }

  const requestId = ++inlinePreviewRequestId
  inlinePreviewLoading.value = true

  try {
    const content = await documentAPI.loadPreviewContent(document.file_url)
    if (requestId !== inlinePreviewRequestId) return

    if (document.preview_type === 'csv') {
      const parsed = parseCsvPreview(content)
      inlinePreviewRows.value = parsed.rows
      inlinePreviewRowLimitReached.value = parsed.rowLimitReached
      inlinePreviewColumnLimitReached.value = parsed.columnLimitReached
      inlinePreviewTruncated.value = parsed.rowLimitReached || parsed.columnLimitReached
      return
    }

    const formattedText = formatTextPreview(document, content)
    if (formattedText.length > MAX_TEXT_PREVIEW_CHARACTERS) {
      inlinePreviewText.value = `${formattedText.slice(0, MAX_TEXT_PREVIEW_CHARACTERS)}\n\n...`
      inlinePreviewTruncated.value = true
    } else {
      inlinePreviewText.value = formattedText
    }
  } catch {
    if (requestId !== inlinePreviewRequestId) return
    inlinePreviewError.value = t('documents.previewLoadFailed')
  } finally {
    if (requestId === inlinePreviewRequestId) {
      inlinePreviewLoading.value = false
    }
  }
}

async function loadDocuments() {
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await documentAPI.list({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      categories: categoryFilter.value.length ? categoryFilter.value : undefined,
      tags: tagFilter.value.length ? tagFilter.value : undefined,
      source_type: sourceTypeFilter.value || undefined,
      pinned: pinnedOnly.value ? true : undefined,
      ordering: buildOrderingValue(),
    })
    documents.value = data.results
    totalCount.value = data.count
    totalPages.value = Math.max(1, Math.ceil(data.count / pageSize.value))
  } catch (err: unknown) {
    errorMessage.value = extractApiError(err, t('documents.loadFailed'))
    documents.value = []
    totalCount.value = 0
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

function resetFormState() {
  editingId.value = null
  editingDocument.value = null
  form.source_type = 'file'
  form.title = ''
  form.description = ''
  form.external_url = ''
  form.category = ''
  form.tagsText = ''
  form.is_pinned = false
  form.file = null
  formError.value = ''
}

function openCreateModal() {
  resetFormState()
  showFormModal.value = true
}

async function openEditModal(document: DocumentSummary) {
  showFormModal.value = true
  formError.value = ''
  form.file = null
  editingId.value = document.id
  try {
    const detail = await documentAPI.get(document.id)
    editingDocument.value = detail
    form.source_type = detail.source_type
    form.title = detail.title
    form.description = detail.description
    form.external_url = detail.external_url
    form.category = detail.category
    form.tagsText = detail.tags.join(', ')
    form.is_pinned = detail.is_pinned
  } catch (err: unknown) {
    showFormModal.value = false
    errorMessage.value = extractApiError(err, t('documents.loadFailed'))
  }
}

function closeFormModal() {
  showFormModal.value = false
  resetFormState()
}

async function saveDocument() {
  formError.value = ''
  if (form.source_type === 'file' && !editingId.value && !form.file) {
    formError.value = t('documents.fileRequired')
    return
  }
  if (form.source_type === 'link' && !form.external_url.trim()) {
    formError.value = t('documents.urlRequired')
    return
  }

  formSaving.value = true
  try {
    const payload = {
      source_type: form.source_type,
      title: form.title.trim() || undefined,
      description: form.description.trim(),
      external_url: form.source_type === 'link' ? form.external_url.trim() : undefined,
      category: form.category.trim(),
      tags: buildTags(),
      is_pinned: form.is_pinned,
      file: form.source_type === 'file' ? form.file : null,
    }

    if (editingId.value) {
      await documentAPI.update(editingId.value, payload)
    } else {
      await documentAPI.create(payload)
    }

    closeFormModal()
    await loadDocuments()
    await loadFilterOptions()
  } catch (err: unknown) {
    formError.value = extractApiError(err, t('documents.saveFailed'))
  } finally {
    formSaving.value = false
  }
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  form.file = input.files?.[0] ?? null
  if (form.file && !form.title.trim()) {
    form.title = form.file.name
  }
}

async function openDetails(document: DocumentSummary) {
  showDetailModal.value = true
  isDetailFullscreen.value = false
  detailLoading.value = true
  selectedDocument.value = null
  resetInlinePreview()
  try {
    selectedDocument.value = await documentAPI.get(document.id)
    await loadInlinePreview(selectedDocument.value)
  } catch (err: unknown) {
    errorMessage.value = extractApiError(err, t('documents.loadFailed'))
    showDetailModal.value = false
  } finally {
    detailLoading.value = false
  }
}

function closeDetails() {
  showDetailModal.value = false
  isDetailFullscreen.value = false
  selectedDocument.value = null
  detailLoading.value = false
  resetInlinePreview()
}

function toggleDetailsFullscreen() {
  isDetailFullscreen.value = !isDetailFullscreen.value
}

function handleDocumentModalKeydown(event: KeyboardEvent) {
  if (!showDetailModal.value) return

  if (event.key === ' ' || event.code === 'Space') {
    event.preventDefault()
    toggleDetailsFullscreen()
    return
  }

  if (event.key === 'Escape' || event.code === 'Escape') {
    closeDetails()
  }
}

async function copyTextToClipboard(value: string) {
  if (window.isSecureContext && navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value)
      return true
    } catch {
      // Fall through to the manual copy path.
    }
  }

  const textarea = window.document.createElement('textarea')
  textarea.value = value
  textarea.setAttribute('readonly', 'true')
  textarea.style.position = 'fixed'
  textarea.style.top = '0'
  textarea.style.left = '0'
  textarea.style.opacity = '0'
  window.document.body.appendChild(textarea)
  textarea.focus()
  textarea.select()
  textarea.setSelectionRange(0, textarea.value.length)

  let copied = false
  try {
    copied = window.document.execCommand('copy')
  } catch {
    copied = false
  }

  window.document.body.removeChild(textarea)
  return copied
}

async function editFromDetails() {
  if (!selectedDocument.value) return
  const documentToEdit = selectedDocument.value
  closeDetails()
  await openEditModal(documentToEdit)
}

function handleOpen(item: DocumentSummary | DocumentDetail) {
	const targetUrl = item.is_external ? item.external_url : item.file_url
	if (!targetUrl) return

	if (item.is_external) {
		const safeUrl = toSafeExternalUrl(targetUrl)
		if (!safeUrl) {
			showToast(t('documents.copyFailed'), 'error')
			return
		}
		window.open(safeUrl, '_blank', 'noopener,noreferrer')
		return
	}

  const anchor = window.document.createElement('a')
  anchor.href = targetUrl
  anchor.download = item.original_filename || item.title || 'document'
  anchor.rel = 'noopener'
  window.document.body.appendChild(anchor)
  anchor.click()
  window.document.body.removeChild(anchor)
}

async function copyDocumentLink(document: DocumentSummary | DocumentDetail) {
	const targetUrl = document.is_external
		? toSafeExternalUrl(document.external_url)
		: document.file_url
	if (!targetUrl) return
	const copied = await copyTextToClipboard(targetUrl)
  if (copied) {
    showToast(t('documents.copySuccess'), 'success')
    return
  }
  showToast(t('documents.copyFailed'), 'error')
}

async function togglePin(document: DocumentSummary) {
  try {
    await documentAPI.update(document.id, {
      source_type: document.source_type,
      is_pinned: !document.is_pinned,
    })
    await loadDocuments()
  } catch (err: unknown) {
    errorMessage.value = extractApiError(err, t('documents.updateFailed'))
  }
}

function openDeleteModal(document: DocumentSummary) {
  pendingDeleteDocument.value = document
  showDeleteModal.value = true
}

function closeDeleteModal() {
  showDeleteModal.value = false
  pendingDeleteDocument.value = null
}

function openDeleteFromDetails() {
  if (!selectedDocument.value) return
  openDeleteModal(selectedDocument.value)
}

async function confirmDelete() {
  if (!pendingDeleteDocument.value) return
  const documentId = pendingDeleteDocument.value.id
  isDeleting.value = true
  try {
    const shouldCloseDetails = selectedDocument.value?.id === documentId
    await documentAPI.delete(documentId)
    closeDeleteModal()
    if (shouldCloseDetails) {
      closeDetails()
    }
    selectedIds.value = selectedIds.value.filter((id) => id !== documentId)
    if (currentPage.value > 1 && documents.value.length === 1) {
      currentPage.value -= 1
    }
    await loadDocuments()
    await loadFilterOptions()
  } catch (err: unknown) {
    errorMessage.value = extractApiError(err, t('documents.deleteFailed'))
  } finally {
    isDeleting.value = false
  }
}

function toggleSelect(id: number) {
  const index = selectedIds.value.indexOf(id)
  if (index >= 0) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

function toggleSelectAll() {
  const pageIds = new Set(documents.value.map((item) => item.id))
  if (isAllCurrentPageSelected.value) {
    selectedIds.value = selectedIds.value.filter((id) => !pageIds.has(id))
    return
  }
  const nextIds = documents.value.map((item) => item.id).filter((id) => !selectedIds.value.includes(id))
  selectedIds.value.push(...nextIds)
}

function clearSelection() {
  selectedIds.value = []
}

async function handleBulkPin(pinned: boolean) {
  if (selectedIds.value.length === 0) return
  isBulkUpdating.value = true
  try {
    await documentAPI.bulkPin(selectedIds.value, pinned)
    clearSelection()
    await loadDocuments()
  } catch (err: unknown) {
    errorMessage.value = extractApiError(err, t('documents.updateFailed'))
  } finally {
    isBulkUpdating.value = false
  }
}

function openBulkDeleteModal() {
  showBulkDeleteModal.value = true
}

async function confirmBulkDelete() {
  if (selectedIds.value.length === 0) return
  const deleteCount = selectedIds.value.length
  isBulkUpdating.value = true
  try {
    await documentAPI.bulkDelete(selectedIds.value)
    showBulkDeleteModal.value = false
    clearSelection()
    if (currentPage.value > 1 && deleteCount === documents.value.length) {
      currentPage.value -= 1
    }
    await loadDocuments()
    await loadFilterOptions()
  } catch (err: unknown) {
    errorMessage.value = extractApiError(err, t('documents.deleteFailed'))
  } finally {
    isBulkUpdating.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  searchQuery.value = draftSearch.value.trim()
  categoryFilter.value = [...selectedCategories.value]
  tagFilter.value = [...selectedTags.value]
  void loadDocuments()
}

function resetFilters() {
  if (filterDebounceTimer) {
    clearTimeout(filterDebounceTimer)
    filterDebounceTimer = null
  }
  draftSearch.value = ''
  selectedCategories.value = []
  selectedTags.value = []
  searchQuery.value = ''
  categoryFilter.value = []
  tagFilter.value = []
  sourceTypeFilter.value = ''
  pinnedOnly.value = false
  currentPage.value = 1
  void loadDocuments()
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  void loadDocuments()
}

function handlePageSizeChange() {
  currentPage.value = 1
  void loadDocuments()
}

watch([draftSearch, selectedCategories, selectedTags, sourceTypeFilter, pinnedOnly], () => {
  scheduleFilterApply()
}, { deep: true })

onBeforeUnmount(() => {
  if (filterDebounceTimer) {
    clearTimeout(filterDebounceTimer)
  }
  window.removeEventListener('keydown', handleDocumentModalKeydown)
})

onMounted(() => {
  window.addEventListener('keydown', handleDocumentModalKeydown)
  void Promise.all([loadDocuments(), loadFilterOptions()])
})
</script>
