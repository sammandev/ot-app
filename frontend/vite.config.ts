import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import { defineConfig, loadEnv } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '')
	const apiBase = env.VITE_API_BASE_URL || 'http://localhost:8008/api'

	return {
		plugins: [vue(), vueJsx(), ...(mode !== 'production' ? [vueDevTools()] : [])],
		resolve: {
			alias: {
				'@': fileURLToPath(new URL('./src', import.meta.url)),
			},
		},
		build: {
			sourcemap: false,
			// Split heavy third-party deps into separate cacheable chunks
			rollupOptions: {
				output: {
					manualChunks: {
						'vendor-vue': ['vue', 'vue-router', 'pinia'],
						'vendor-charts': ['apexcharts', 'vue3-apexcharts'],
						'vendor-calendar': [
							'@fullcalendar/core',
							'@fullcalendar/daygrid',
							'@fullcalendar/timegrid',
							'@fullcalendar/list',
							'@fullcalendar/interaction',
							'@fullcalendar/multimonth',
							'@fullcalendar/vue3',
						],
						'vendor-ui': ['flatpickr', 'swiper', 'dropzone', 'axios'],
						'vendor-xlsx': ['@e965/xlsx'],
					},
				},
			},
			// Raise warning threshold — some chunks will be legitimately large
			chunkSizeWarningLimit: 600,
		},
		server: {
			host: '0.0.0.0',
			port: 3334,
			proxy: {
				'/api': {
					target: apiBase.replace(/\/?api\/?$/, ''), // strip trailing /api to avoid double path
					changeOrigin: true,
				},
			},
		},
	}
})
