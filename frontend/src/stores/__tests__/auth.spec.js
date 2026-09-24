import { describe, expect, it, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/api/client', () => {
  return {
    default: { post: vi.fn(), get: vi.fn() },
    setTokens: vi.fn(),
    setAuthFailureHandler: vi.fn(),
    setTokensRefreshedHandler: vi.fn(),
  }
})

import api from '@/api/client'
import { useAuthStore } from '../auth'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('logs in, stores tokens and fetches current user', async () => {
    api.post.mockResolvedValueOnce({ data: { access_token: 'a', refresh_token: 'r' } })
    api.get.mockResolvedValueOnce({ data: { id: 1, login: 'alice', display_name: 'Alice' } })

    const store = useAuthStore()
    await store.login('alice', 'secret')

    expect(store.isAuthenticated).toBe(true)
    expect(store.user.login).toBe('alice')
  })

  it('logs out and clears user/auth state', async () => {
    api.post.mockResolvedValueOnce({ data: { access_token: 'a', refresh_token: 'r' } })
    api.get.mockResolvedValueOnce({ data: { id: 1, login: 'alice', display_name: 'Alice' } })

    const store = useAuthStore()
    await store.login('alice', 'secret')
    store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBe(null)
  })

  it('rejects login on failure and does not mark authenticated', async () => {
    api.post.mockRejectedValueOnce(new Error('401'))

    const store = useAuthStore()
    await expect(store.login('alice', 'wrong')).rejects.toThrow()
    expect(store.isAuthenticated).toBe(false)
  })
})
