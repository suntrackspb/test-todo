import { describe, expect, it, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/api/client', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import api from '@/api/client'
import { useProjectsStore } from '../projects'

describe('projects store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches the project tree', async () => {
    const tree = [{ id: 1, title: 'Work', children: [] }]
    api.get.mockResolvedValueOnce({ data: tree })

    const store = useProjectsStore()
    await store.fetchTree()

    expect(store.tree).toEqual(tree)
  })

  it('creates a project and refreshes the tree', async () => {
    api.post.mockResolvedValueOnce({ data: {} })
    api.get.mockResolvedValueOnce({ data: [{ id: 2, title: 'New', children: [] }] })

    const store = useProjectsStore()
    await store.createProject({ title: 'New' })

    expect(api.post).toHaveBeenCalledWith('/projects', { title: 'New', parent_id: null })
    expect(store.tree).toHaveLength(1)
  })

  it('clears selection when the selected project is deleted', async () => {
    api.delete.mockResolvedValueOnce({})
    api.get.mockResolvedValueOnce({ data: [] })

    const store = useProjectsStore()
    store.selectProject(5)
    await store.deleteProject(5)

    expect(store.selectedProjectId).toBe(null)
  })
})
