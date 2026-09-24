import { defineStore } from 'pinia'

const STORAGE_KEY = 'notes-app-theme'

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme)
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: 'light',
  }),
  actions: {
    init() {
      let stored = null
      try {
        stored = localStorage.getItem(STORAGE_KEY)
      } catch {
        // localStorage unavailable — fall back to system preference
      }
      const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
      this.theme = stored || (prefersDark ? 'dark' : 'light')
      applyTheme(this.theme)
    },
    toggle() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      applyTheme(this.theme)
      try {
        localStorage.setItem(STORAGE_KEY, this.theme)
      } catch {
        // non-fatal
      }
    },
  },
})
