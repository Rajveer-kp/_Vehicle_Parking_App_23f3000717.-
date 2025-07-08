import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Clear old authentication data on app start
import './utils/clearOldAuth.js'

// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Bootstrap Icons - Import from package (install with: npm install bootstrap-icons)
// If this fails, the CDN link in index.html will be used as fallback
import 'bootstrap-icons/font/bootstrap-icons.css'

createApp(App).use(router).mount('#app')
