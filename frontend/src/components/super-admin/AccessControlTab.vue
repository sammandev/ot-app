<template>
    <div class="space-y-6">
        <!-- Current User Info -->
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div class="flex items-start gap-3">
                <SettingsIcon class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div>
                    <h3 class="font-medium text-blue-900 dark:text-blue-100">
                        {{ authStore.isDeveloper ? 'Developer Access' : 'Super Admin Access' }}
                    </h3>
                    <p class="text-sm text-blue-700 dark:text-blue-300 mt-1">
                        You are logged in as: <strong>{{ authStore.user?.username }}</strong>
                        <span v-if="authStore.user?.worker_id"> ({{ authStore.user.worker_id }})</span>
                        <span
                            class="ml-2 text-xs px-2 py-0.5 rounded"
                            :class="authStore.isDeveloper
                                ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300'
                                : 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'"
                        >
                            {{ authStore.isDeveloper ? 'Developer' : 'Super Admin' }}
                        </span>
                    </p>
                </div>
            </div>
        </div>

        <!-- Access Control Sections -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- PTB Admin Access -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">PTB Admin Access</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Users with <code class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">is_ptb_admin: true</code> can access:
                </p>
                <ul class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                    <li class="flex items-start gap-2"><CheckIcon class="w-4 h-4 text-green-500 mt-0.5" /><span>OT Regulations Management</span></li>
                    <li class="flex items-start gap-2"><CheckIcon class="w-4 h-4 text-green-500 mt-0.5" /><span>Departments Management</span></li>
                    <li class="flex items-start gap-2"><CheckIcon class="w-4 h-4 text-green-500 mt-0.5" /><span>Employees Management</span></li>
                    <li class="flex items-start gap-2"><CheckIcon class="w-4 h-4 text-green-500 mt-0.5" /><span>Projects Management</span></li>
                </ul>
                <div class="mt-4 p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700">
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                        <strong>Note:</strong> PTB Admin status is managed in the external API at
                        <code class="text-xs">employee_info.is_ptb_admin</code>
                    </p>
                </div>
            </div>

            <!-- Super Admin / Developer Access -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Elevated Access Roles</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Users with <code class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">role: developer</code>
                    or <code class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">role: superadmin</code> can access this page.
                </p>
                <ul class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                    <li class="flex items-start gap-2"><CheckIcon class="w-4 h-4 text-purple-500 mt-0.5" /><span>All PTB Admin features</span></li>
                    <li class="flex items-start gap-2"><CheckIcon class="w-4 h-4 text-purple-500 mt-0.5" /><span>Access Control Management (this page)</span></li>
                    <li class="flex items-start gap-2"><CheckIcon class="w-4 h-4 text-purple-500 mt-0.5" /><span>System-wide configuration</span></li>
                    <li class="flex items-start gap-2"><CheckIcon class="w-4 h-4 text-amber-500 mt-0.5" /><span>Role management <em class="text-xs text-gray-500">(Developer only)</em></span></li>
                </ul>
                <div class="mt-4 p-3 bg-purple-50 dark:bg-purple-900/20 rounded border border-purple-200 dark:border-purple-800">
                    <p class="text-xs text-purple-700 dark:text-purple-300">
                        <strong>Security:</strong> Developer role is hardcoded and cannot be granted through the UI. Only developers can change other users' roles.
                    </p>
                </div>
            </div>

            <!-- Superuser Access -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Superuser Access</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Users with <code class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">is_superuser: true</code> from external API:
                </p>
                <ul class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                    <li class="flex items-start gap-2"><InfoCircleIcon class="w-4 h-4 text-blue-500 mt-0.5" /><span>Full API access permissions</span></li>
                    <li class="flex items-start gap-2"><InfoCircleIcon class="w-4 h-4 text-blue-500 mt-0.5" /><span>Bypass certain validation rules</span></li>
                </ul>
            </div>

            <!-- Staff Access -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Staff Access</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Users with <code class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">is_staff: true</code> from external API:
                </p>
                <ul class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                    <li class="flex items-start gap-2"><InfoCircleIcon class="w-4 h-4 text-blue-500 mt-0.5" /><span>Enhanced permissions for staff operations</span></li>
                    <li class="flex items-start gap-2"><InfoCircleIcon class="w-4 h-4 text-blue-500 mt-0.5" /><span>Access to staff-level features</span></li>
                </ul>
            </div>
        </div>

        <!-- User Role Configuration -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h2 class="text-lg font-semibold text-gray-900 dark:text-white">User Role Configuration</h2>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Manage user access levels and permissions</p>
                </div>
                <button @click="showAddUser = true"
                    class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition text-sm font-medium">
                    Add User
                </button>
            </div>

            <!-- Success Alert -->
            <div v-if="permissionSuccessMessage"
                class="mb-4 flex items-center justify-between gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800 dark:border-emerald-900/50 dark:bg-emerald-900/30 dark:text-emerald-100">
                <span class="flex-1">{{ permissionSuccessMessage }}</span>
                <button type="button" class="text-emerald-600 hover:text-emerald-800 flex-shrink-0"
                    @click="permissionSuccessMessage = ''">
                    <XIcon />
                </button>
            </div>

            <!-- User Search and Filter -->
            <div class="mb-4">
                <div class="relative">
                    <input v-model="searchQuery" type="text" placeholder="Search by username or worker ID..."
                        class="w-full px-4 py-2 pl-10 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-transparent" />
                    <svg class="absolute left-3 top-3 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </div>
            </div>

            <!-- Users Table -->
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead class="bg-gray-50 dark:bg-gray-900">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Username</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Worker ID</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">PTB Admin</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Superuser</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Staff</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Role</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Menu Access</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        <tr v-if="loading">
                            <td colspan="8" class="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">Loading users...</td>
                        </tr>
                        <tr v-else-if="error">
                            <td colspan="8" class="px-4 py-8 text-center text-sm text-red-600 dark:text-red-400">{{ error }}</td>
                        </tr>
                        <tr v-else-if="filteredUsers.length === 0">
                            <td colspan="8" class="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                                {{ searchQuery ? 'No users found matching your search' : 'No users configured yet' }}
                            </td>
                        </tr>
                        <tr v-else v-for="user in filteredUsers" :key="user.id"
                            class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
                                {{ user.username }}
                                <span v-if="isDeveloper(user)"
                                    class="ml-2 text-xs px-2 py-0.5 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded">Developer</span>
                                <span v-else-if="isSuperAdmin(user)"
                                    class="ml-2 text-xs px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">Super Admin</span>
                            </td>
                            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{{ user.worker_id || '-' }}</td>
                            <td class="px-4 py-3 text-sm">
                                <label class="flex items-center cursor-pointer">
                                    <input type="checkbox" :checked="user.is_ptb_admin" @change="togglePtbAdmin(user)" :disabled="isDeveloper(user)"
                                        class="w-4 h-4 text-brand-600 bg-gray-100 border-gray-300 rounded focus:ring-brand-500 dark:focus:ring-brand-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                                    <span class="sr-only">PTB Admin</span>
                                </label>
                            </td>
                            <td class="px-4 py-3 text-sm">
                                <label class="flex items-center cursor-pointer">
                                    <input type="checkbox" :checked="user.is_superuser" @change="toggleSuperuser(user)" :disabled="isDeveloper(user)"
                                        class="w-4 h-4 text-brand-600 bg-gray-100 border-gray-300 rounded focus:ring-brand-500 dark:focus:ring-brand-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                                    <span class="sr-only">Superuser</span>
                                </label>
                            </td>
                            <td class="px-4 py-3 text-sm">
                                <label class="flex items-center cursor-pointer">
                                    <input type="checkbox" :checked="user.is_staff" @change="toggleStaff(user)" :disabled="isDeveloper(user)"
                                        class="w-4 h-4 text-brand-600 bg-gray-100 border-gray-300 rounded focus:ring-brand-500 dark:focus:ring-brand-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                                    <span class="sr-only">Staff</span>
                                </label>
                            </td>
                            <td class="px-4 py-3 text-sm">
                                <select
                                    v-if="authStore.isDeveloper && !isDeveloper(user)"
                                    :value="user.role || 'user'"
                                    @change="changeRole(user, ($event.target as HTMLSelectElement).value)"
                                    class="block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm py-1 px-2 focus:ring-brand-500 focus:border-brand-500">
                                    <option value="user">User</option>
                                    <option value="superadmin">Super Admin</option>
                                </select>
                                <span v-else
                                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                                    :class="isDeveloper(user)
                                        ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300'
                                        : user.role === 'superadmin'
                                            ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'
                                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'">
                                    {{ isDeveloper(user) ? 'Developer' : user.role === 'superadmin' ? 'Super Admin' : 'User' }}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-sm">
                                <button @click="openMenuManager(user)" :disabled="isDeveloper(user)"
                                    class="text-blue-600 hover:text-blue-900 dark:text-blue-400 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
                                    {{ getMenuPermissionLabel(user) }}
                                </button>
                            </td>
                            <td class="px-4 py-3 text-sm">
                                <button @click="deleteUser(user)" :disabled="isDeveloper(user)"
                                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed">
                                    Deactivate
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Info Box -->
            <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
                <p class="text-xs text-blue-700 dark:text-blue-300">
                    <strong>Important:</strong> Changes made here are saved permanently in the backend database. All access control settings persist across sessions and devices.
                </p>
            </div>
        </div>

        <!-- Menu Manager Modal -->
        <div v-if="showMenuManager"
            class="fixed inset-0 bg-black/50 flex items-center justify-center z-[100000] p-4"
            @click.self="closeMenuManager">
            <div role="dialog" aria-modal="true" aria-labelledby="menu-manager-modal-title" class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
                <!-- Sticky Header -->
                <div class="sticky top-0 z-10 bg-white dark:bg-gray-800 px-6 pt-6 pb-4 rounded-t-lg border-b border-gray-200 dark:border-gray-700">
                    <h3 id="menu-manager-modal-title" class="text-lg font-semibold text-gray-900 dark:text-white mb-1">Manage Menu Permissions</h3>
                    <p class="text-sm text-gray-500">User: <strong>{{ selectedUser?.username }}</strong></p>
                </div>

                <!-- Scrollable Body -->
                <div class="flex-1 overflow-y-auto px-6 py-4">
                    <div class="space-y-6">
                        <div v-for="(group, gIdx) in availableResourceGroups" :key="gIdx">
                            <h4 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3 pb-1 border-b">{{ group.title }}</h4>
                            <div class="overflow-x-auto">
                                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                    <thead class="bg-gray-50 dark:bg-gray-900">
                                        <tr>
                                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Resource</th>
                                            <th v-for="action in actions" :key="action.key"
                                                class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase" :title="action.title">
                                                {{ action.label }}
                                            </th>
                                            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Presets</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                                        <tr v-for="item in group.items" :key="item.key">
                                            <td class="px-3 py-2 text-sm text-gray-900 dark:text-white font-medium">
                                                {{ item.name }}
                                                <div v-if="hasAnyAccess(item.key)" class="text-xs text-green-600 dark:text-green-400 font-normal">Active</div>
                                            </td>
                                            <td v-for="action in actions" :key="action.key" class="px-3 py-2 text-center">
                                                <input type="checkbox" :checked="hasAction(item.key, action.key)"
                                                    @change="toggleAction(item.key, action.key)"
                                                    class="rounded border-gray-300 text-brand-600 focus:ring-brand-500 cursor-pointer" />
                                            </td>
                                            <td class="px-3 py-2 text-right space-x-2">
                                                <button @click="setFullAccess(item.key)" class="text-xs text-blue-600 hover:underline">Full</button>
                                                <button @click="setNoAccess(item.key)" class="text-xs text-gray-500 hover:text-red-500 hover:underline">None</button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sticky Footer -->
                <div class="sticky bottom-0 z-10 bg-white dark:bg-gray-800 px-6 py-4 border-t border-gray-200 dark:border-gray-700 rounded-b-lg flex justify-between gap-3">
                    <button @click="resetDefaultAccess"
                        class="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 dark:border-red-700 dark:text-red-400 dark:hover:bg-red-900/20 transition">
                        Reset Default Access
                    </button>
                    <div class="flex gap-3">
                        <button @click="closeMenuManager"
                            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700 transition">
                            Cancel
                        </button>
                        <button @click="saveMenuPermissions"
                            class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition shadow-sm">
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add User Modal -->
        <div v-if="showAddUser" class="fixed inset-0 bg-black/50 flex items-center justify-center z-[99999] p-4"
            @click.self="showAddUser = false">
            <div role="dialog" aria-modal="true" aria-labelledby="add-user-modal-title" class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
                <h3 id="add-user-modal-title" class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Add User Access</h3>
                <form @submit.prevent="addUser" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
                        <input v-model="newUser.username" type="text" required
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                            placeholder="e.g., john_doe" />
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Worker ID <span class="text-gray-500 text-xs">(optional)</span>
                        </label>
                        <input v-model="newUser.worker_id" type="text"
                            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                            placeholder="e.g., AB1234567" />
                    </div>
                    <div class="flex items-center">
                        <input v-model="newUser.is_ptb_admin" type="checkbox" id="new-ptb-admin"
                            class="w-4 h-4 text-brand-600 bg-gray-100 border-gray-300 rounded focus:ring-brand-500 dark:focus:ring-brand-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                        <label for="new-ptb-admin" class="ml-2 text-sm text-gray-700 dark:text-gray-300">Grant PTB Admin access</label>
                    </div>
                    <div class="flex gap-3 pt-4">
                        <button type="submit"
                            class="flex-1 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition text-sm font-medium">
                            Add User
                        </button>
                        <button type="button" @click="cancelAddUser"
                            class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition text-sm font-medium">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Access Levels Reference -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Access Levels Reference</h2>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead class="bg-gray-50 dark:bg-gray-900">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Role</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Identifier</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Access Level</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        <tr>
                            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">Developer</td>
                            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400"><code class="text-xs">role: developer</code></td>
                            <td class="px-4 py-3 text-sm text-amber-600 dark:text-amber-400">Full System Access + Role Management</td>
                        </tr>
                        <tr>
                            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">Super Admin</td>
                            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400"><code class="text-xs">role: superadmin</code></td>
                            <td class="px-4 py-3 text-sm text-purple-600 dark:text-purple-400">Full System Access</td>
                        </tr>
                        <tr>
                            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">PTB Admin</td>
                            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400"><code class="text-xs">is_ptb_admin: true</code></td>
                            <td class="px-4 py-3 text-sm text-green-600 dark:text-green-400">Admin Features</td>
                        </tr>
                        <tr>
                            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">Superuser</td>
                            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400"><code class="text-xs">is_superuser: true</code></td>
                            <td class="px-4 py-3 text-sm text-blue-600 dark:text-blue-400">Full API Access</td>
                        </tr>
                        <tr>
                            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">Staff</td>
                            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400"><code class="text-xs">is_staff: true</code></td>
                            <td class="px-4 py-3 text-sm text-blue-600 dark:text-blue-400">Staff Features</td>
                        </tr>
                        <tr>
                            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">Regular User</td>
                            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400"><code class="text-xs">is_active: true</code></td>
                            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">Basic Features</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToast } from '@/composables/useToast'
import { CheckIcon, InfoCircleIcon, SettingsIcon, XIcon } from '@/icons'
import { type UserAccessControl, userAccessAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

type MenuPermissions = Record<string, string[]>

const users = defineModel<UserAccessControl[]>('users', { required: true })

const authStore = useAuthStore()
const { showToast } = useToast()
const confirmDialog = useConfirmDialog()

const searchQuery = ref('')
const showAddUser = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
const permissionSuccessMessage = ref('')
const newUser = ref({
	username: '',
	worker_id: '',
	is_ptb_admin: false,
	is_superuser: false,
	is_staff: false,
})

// Menu Management
const showMenuManager = ref(false)
const selectedUser = ref<UserAccessControl | null>(null)
const menuPermissions = reactive<MenuPermissions>({})

const availableResourceGroups = [
	{
		title: 'Overtime',
		items: [
			{ name: 'OT Form', key: 'ot_form' },
			{ name: 'OT History', key: 'ot_history' },
			{ name: 'OT Summary', key: 'ot_summary' },
		],
	},
	{
		title: 'Core Features',
		items: [
			{ name: 'PTB Calendar', key: 'calendar' },
			{ name: 'Task Board', key: 'kanban' },
			{ name: 'Purchasing', key: 'purchasing' },
			{ name: 'Assets', key: 'assets' },
			{ name: 'Personal Notes', key: 'personal_notes' },
		],
	},
	{
		title: 'Admin Pages',
		items: [
			{ name: 'Employees', key: 'admin_employees' },
			{ name: 'Projects', key: 'projects' },
			{ name: 'Departments', key: 'departments' },
			{ name: 'OT Regulations', key: 'admin_regulations' },
		],
	},
	{
		title: 'Other Pages',
		items: [
			{ name: 'Submit a Report', key: 'report' },
			{ name: 'Release Notes', key: 'release_notes' },
			{ name: 'Super Admin Dashboard', key: 'super_admin_access' },
		],
	},
]

const actions = [
	{ key: 'create', label: 'C', title: 'Create' },
	{ key: 'read', label: 'R', title: 'Read' },
	{ key: 'update', label: 'U', title: 'Update' },
	{ key: 'delete', label: 'D', title: 'Delete' },
]

const openMenuManager = (user: UserAccessControl) => {
	if (!user) return
	if (isDeveloper(user)) {
		showToast('Cannot modify developer permissions', 'warning')
		return
	}
	selectedUser.value = user
	for (const key of Object.keys(menuPermissions)) {
		delete menuPermissions[key]
	}

	const up = user.menu_permissions
	if (Array.isArray(up)) {
		up.forEach((key) => {
			menuPermissions[key] = ['read']
		})
	} else if (up && typeof up === 'object') {
		Object.entries(up).forEach(([key, val]) => {
			if (Array.isArray(val)) {
				menuPermissions[key] = [...val]
			}
		})
	}

	showMenuManager.value = true
}

const closeMenuManager = () => {
	showMenuManager.value = false
	selectedUser.value = null
}

const hasAction = (resource: string, action: string) => {
	return menuPermissions[resource]?.includes(action) || false
}

const toggleAction = (resource: string, action: string) => {
	if (!menuPermissions[resource]) {
		menuPermissions[resource] = []
	}

	const assigned = menuPermissions[resource]
	const idx = assigned.indexOf(action)

	if (idx > -1) {
		assigned.splice(idx, 1)
		if (action === 'read') {
			menuPermissions[resource] = []
		}
	} else {
		assigned.push(action)
		if (action !== 'read' && !assigned.includes('read')) {
			assigned.push('read')
		}
	}
}

const setFullAccess = (resource: string) => {
	menuPermissions[resource] = ['create', 'read', 'update', 'delete']
}

const setNoAccess = (resource: string) => {
	menuPermissions[resource] = []
}

const resetDefaultAccess = () => {
	for (const key of Object.keys(menuPermissions)) {
		delete menuPermissions[key]
	}
}

const hasAnyAccess = (resource: string) => {
	return !!menuPermissions[resource] && menuPermissions[resource].length > 0
}

const getMenuPermissionLabel = (user: UserAccessControl) => {
	const p = user.menu_permissions
	if (!p) return 'Default'
	if (Array.isArray(p)) return p.length > 0 ? `${p.length} views` : 'Default'
	const keys = Object.keys(p)
	if (keys.length === 0) return 'Default'
	const activeKeys = keys.filter((k) => Array.isArray(p[k]) && p[k].length > 0)
	return activeKeys.length > 0 ? `${activeKeys.length} resources` : 'Default'
}

const saveMenuPermissions = async () => {
	if (!selectedUser.value || !selectedUser.value.id) {
		showToast('No user selected', 'warning')
		return
	}

	loading.value = true
	try {
		const userId = selectedUser.value.id
		const userName = selectedUser.value.username
		const updated = await userAccessAPI.update(userId, {
			menu_permissions: menuPermissions,
		})

		const index = users.value.findIndex((u) => u.id === userId)
		if (index !== -1) {
			users.value[index] = updated
		}
		closeMenuManager()

		permissionSuccessMessage.value = `Permissions saved for ${userName}! Changes are applied in real-time.`
		setTimeout(() => {
			permissionSuccessMessage.value = ''
		}, 8000)
	} catch (err: unknown) {
		const e = err as { response?: { data?: { error?: string } } }
		console.error('Failed to update permissions:', e)
		showToast(e.response?.data?.error || 'Failed to update permissions', 'error')
	} finally {
		loading.value = false
	}
}

const loadUsers = async () => {
	loading.value = true
	error.value = null
	try {
		const res = await userAccessAPI.getAll()
		users.value = res
	} catch (err: unknown) {
		const e = err as { response?: { data?: { error?: string } } }
		console.error('Failed to load users:', e)
		error.value = e.response?.data?.error || 'Failed to load users'
	} finally {
		loading.value = false
	}
}

const filteredUsers = computed(() => {
	const validUsers = users.value.filter((user) => user && user.id != null)
	if (!searchQuery.value) return validUsers
	const query = searchQuery.value.toLowerCase()
	return validUsers.filter(
		(user) =>
			user.username?.toLowerCase().includes(query) || user.worker_id?.toLowerCase().includes(query),
	)
})

const isSuperAdmin = (user: UserAccessControl) => {
	if (!user) return false
	const role = user.role || ''
	return role === 'developer' || role === 'superadmin'
}

const isDeveloper = (user: UserAccessControl) => {
	if (!user) return false
	const role = user.role || ''
	return role === 'developer'
}

const togglePtbAdmin = async (user: UserAccessControl) => {
	if (!user || !user.id) return
	if (isDeveloper(user)) {
		showToast('Cannot modify developer', 'warning')
		return
	}
	try {
		const userId = user.id
		const updated = await userAccessAPI.update(userId, { is_ptb_admin: !user.is_ptb_admin })
		const idx = users.value.findIndex((u) => u.id === userId)
		if (idx !== -1) users.value[idx] = updated
	} catch (err: unknown) {
		const e = err as { response?: { data?: { error?: string } } }
		showToast(e.response?.data?.error || 'Error', 'error')
	}
}

const changeRole = async (user: UserAccessControl, newRole: string) => {
	if (!user || !user.id) return
	if (isDeveloper(user)) {
		showToast('Cannot modify developer role', 'warning')
		return
	}
	if (!authStore.isDeveloper) {
		showToast('Only developer can change user roles', 'warning')
		return
	}
	const previousRole = user.role || 'user'
	try {
		const userId = user.id
		const updated = await userAccessAPI.update(userId, {
			role: newRole as 'developer' | 'superadmin' | 'user',
		})
		const idx = users.value.findIndex((u) => u.id === userId)
		if (idx !== -1) users.value[idx] = updated
		showToast(`Role updated to ${newRole} for ${user.username}`, 'success')
	} catch (err: unknown) {
		const e = err as { response?: { data?: { error?: string } } }
		const idx = users.value.findIndex((u) => u.id === user.id)
		if (idx !== -1) {
			users.value[idx] = Object.assign({}, users.value[idx], { role: previousRole })
		}
		showToast(e.response?.data?.error || 'Failed to update role', 'error')
	}
}

const toggleSuperuser = async (user: UserAccessControl) => {
	if (!user || !user.id) return
	if (isDeveloper(user)) {
		showToast('Cannot modify developer', 'warning')
		return
	}
	try {
		const userId = user.id
		const updated = await userAccessAPI.update(userId, { is_superuser: !user.is_superuser })
		const idx = users.value.findIndex((u) => u.id === userId)
		if (idx !== -1) users.value[idx] = updated
	} catch (err: unknown) {
		const e = err as { response?: { data?: { error?: string } } }
		showToast(e.response?.data?.error || 'Error', 'error')
	}
}

const toggleStaff = async (user: UserAccessControl) => {
	if (!user || !user.id) return
	if (isDeveloper(user)) {
		showToast('Cannot modify developer', 'warning')
		return
	}
	try {
		const userId = user.id
		const updated = await userAccessAPI.update(userId, { is_staff: !user.is_staff })
		const idx = users.value.findIndex((u) => u.id === userId)
		if (idx !== -1) users.value[idx] = updated
	} catch (err: unknown) {
		const e = err as { response?: { data?: { error?: string } } }
		showToast(e.response?.data?.error || 'Error', 'error')
	}
}

const deleteUser = async (user: UserAccessControl) => {
	if (!user || !user.id) return
	if (isDeveloper(user)) {
		showToast('Cannot modify developer', 'warning')
		return
	}
	const ok = await confirmDialog.confirm({
		title: 'Deactivate User',
		message: `Deactivate ${user.username}? This will force the user to log out immediately and prevent them from logging in again.`,
		type: 'danger',
		confirmLabel: 'Deactivate',
	})
	if (!ok) return
	try {
		const userId = user.id
		const userName = user.username
		const updated = await userAccessAPI.update(userId, { is_active: false })
		const idx = users.value.findIndex((u) => u.id === userId)
		if (idx !== -1) users.value[idx] = updated

		permissionSuccessMessage.value = `⚠️ User ${userName} has been deactivated and will be forced to logout.`
		setTimeout(() => {
			permissionSuccessMessage.value = ''
		}, 8000)
	} catch (err: unknown) {
		const e = err as { response?: { data?: { error?: string } } }
		showToast(e.response?.data?.error || 'Error', 'error')
	}
}

const addUser = () => {
	showToast('User management is synced from external API.', 'info')
	cancelAddUser()
}

const cancelAddUser = () => {
	showAddUser.value = false
	newUser.value = {
		username: '',
		worker_id: '',
		is_ptb_admin: false,
		is_superuser: false,
		is_staff: false,
	}
}

onMounted(() => {
	loadUsers()
})
</script>
