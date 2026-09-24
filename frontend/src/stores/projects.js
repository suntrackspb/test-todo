import { defineStore } from 'pinia'
import api from '@/api/client'

export const useProjectsStore = defineStore('projects', {
  state: () => ({
    tree: [],
    selectedProjectId: null,
  }),
  actions: {
    async fetchTree() {
      const resp = await api.get('/projects/tree')
      this.tree = resp.data
    },
    async createProject({ title, parentId = null }) {
      await api.post('/projects', { title, parent_id: parentId })
      await this.fetchTree()
    },
    async renameProject(projectId, title) {
      await api.patch(`/projects/${projectId}`, { title })
      await this.fetchTree()
    },
    async deleteProject(projectId) {
      await api.delete(`/projects/${projectId}`)
      if (this.selectedProjectId === projectId) {
        this.selectedProjectId = null
      }
      await this.fetchTree()
    },
    selectProject(projectId) {
      this.selectedProjectId = projectId
    },
  },
})
