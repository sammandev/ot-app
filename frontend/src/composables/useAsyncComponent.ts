/**
 * Async Component Loader
 * Provides utilities for loading components asynchronously with loading states
 */

import { type Component, defineAsyncComponent } from 'vue'

interface AsyncComponentOptions {
	loader: () => Promise<Component>
	loadingComponent?: Component
	errorComponent?: Component
	delay?: number
	timeout?: number
}

/**
 * Create an async component with default loading and error states
 */
export function createAsyncComponent(options: AsyncComponentOptions) {
	return defineAsyncComponent({
		loader: options.loader,
		loadingComponent: options.loadingComponent,
		errorComponent: options.errorComponent,
		delay: options.delay ?? 200,
		timeout: options.timeout ?? 10000,
	})
}

/**
 * Simple async component loader without loading states
 */
export function lazyLoad(loader: () => Promise<Component>) {
	return defineAsyncComponent(loader)
}
