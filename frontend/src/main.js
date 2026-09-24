import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { polyfill as dragDropPolyfill } from 'mobile-drag-drop'
import 'mobile-drag-drop/default.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'
import './style.css'

dragDropPolyfill({ holdToDrag: 300 })

const app = createApp(App)

app.use(createPinia())
app.use(router)

useAuthStore().init()
useThemeStore().init()

app.mount('#app')
