# Skeleton Loading Components

Reusable skeleton loading components for the OT Management System frontend. These provide visual feedback while data is loading from the API.

## Components

### TableSkeleton
Skeleton for table layouts with pagination.

**Props:**
- `rows` (number, default: 5) - Number of table rows to show
- `columns` (number, default: 5) - Number of table columns to show

**Usage:**
```vue
<TableSkeleton :rows="10" :columns="6" />
```

### CardSkeleton
Skeleton for basic card content.

**Props:**
- `lines` (number, default: 3) - Number of content lines
- `showHeader` (boolean, default: true) - Show card header
- `showHeaderAction` (boolean, default: false) - Show header action button

**Usage:**
```vue
<CardSkeleton :lines="4" :show-header="true" />
```

### ChartSkeleton
Skeleton for chart/graph layouts.

**Props:**
- `height` (number, default: 300) - Chart height in pixels
- `bars` (number, default: 8) - Number of bars/data points
- `showHeader` (boolean, default: true) - Show chart header
- `showControls` (boolean, default: false) - Show chart controls

**Usage:**
```vue
<ChartSkeleton :height="350" :bars="12" :show-controls="true" />
```

### FormSkeleton
Skeleton for form layouts.

**Props:**
- `fields` (number, default: 4) - Number of form fields
- `showButtons` (boolean, default: true) - Show form buttons

**Usage:**
```vue
<FormSkeleton :fields="6" :show-buttons="true" />
```

### StatCardSkeleton
Skeleton for statistics/metric cards.

**Props:**
None - Fixed layout optimized for stat cards.

**Usage:**
```vue
<StatCardSkeleton />
```

### ListSkeleton
Skeleton for list layouts.

**Props:**
- `items` (number, default: 5) - Number of list items
- `showHeader` (boolean, default: true) - Show list header
- `showAvatar` (boolean, default: false) - Show avatar/icon
- `showAction` (boolean, default: false) - Show action button

**Usage:**
```vue
<ListSkeleton :items="8" :show-avatar="true" :show-action="true" />
```

### FilterSkeleton
Skeleton for filter/search layouts.

**Props:**
- `filters` (number, default: 4) - Number of filter fields

**Usage:**
```vue
<FilterSkeleton :filters="5" />
```

## Usage Examples

### Admin Pages (Tables)
```vue
<template>
  <div>
    <TableSkeleton v-if="isLoading" :rows="10" :columns="6" />
    <table v-else>
      <!-- Actual table content -->
    </table>
  </div>
</template>
```

### Dashboard Pages (Mixed Layout)
```vue
<template>
  <div class="space-y-6">
    <template v-if="isLoading">
      <FilterSkeleton :filters="4" />
      <div class="grid gap-4 md:grid-cols-4">
        <StatCardSkeleton v-for="i in 4" :key="i" />
      </div>
      <ChartSkeleton :height="350" :bars="12" />
      <TableSkeleton :rows="10" :columns="5" />
    </template>
    
    <template v-else>
      <!-- Actual content -->
    </template>
  </div>
</template>
```

## Implementation Pattern

1. **Import the skeleton:**
```vue
<script setup>
import TableSkeleton from '@/components/skeletons/TableSkeleton.vue'
// or
import { TableSkeleton } from '@/components/skeletons'
</script>
```

2. **Add loading state:**
```vue
const isLoading = ref(false)
```

3. **Show skeleton while loading:**
```vue
<template>
  <TableSkeleton v-if="isLoading" :rows="10" :columns="6" />
  <YourActualContent v-else />
</template>
```

## Design

All skeletons follow the app's design system:
- Uses theme-aware colors (gray-200/gray-700)
- Smooth pulse animation
- Matches actual component layouts
- Responsive and adaptive

## Notes

- Skeletons are purely visual - they don't load data
- Always pair with actual loading state logic
- Match skeleton props to actual content structure
- Use `v-if` for loading state, not `v-show` (prevents unnecessary rendering)
