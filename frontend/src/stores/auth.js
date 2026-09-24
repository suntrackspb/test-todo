import { defineStore } from 'pinia'
import api, { setAuthFailureHandler, setTokens, setTokensRefreshedHandler } from '@/api/client'

const STORAGE_KEY = 'notes-app-tokens'

function loadStoredTokens() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function persistTokens(tokens) {
  try {
    if (tokens) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  } catch {
    // localStorage unavailable (private mode, etc.) - non-fatal
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
  }),
  actions: {
    init() {
      const tokens = loadStoredTokens()
      if (tokens) {
        setTokens(tokens)
        this.isAuthenticated = true
      }
      setAuthFailureHandler(() => this.logout())
      setTokensRefreshedHandler((newTokens) => persistTokens(newTokens))
    },
    async login(login, password) {
      const resp = await api.post('/auth/login', { login, password })
      setTokens(resp.data)
      persistTokens(resp.data)
      this.isAuthenticated = true
      await this.fetchMe()
    },
    async fetchMe() {
      const resp = await api.get('/auth/me')
      this.user = resp.data
    },
    logout() {
      setTokens(null)
      persistTokens(null)
      this.user = null
      this.isAuthenticated = false
    },
  },
})
