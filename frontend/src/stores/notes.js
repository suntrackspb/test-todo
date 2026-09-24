import { defineStore } from 'pinia'
import api from '@/api/client'

export const useNotesStore = defineStore('notes', {
  state: () => ({
    notesByProject: {},
    activeNote: null,
  }),
  actions: {
    async fetchNotes(projectId) {
      const resp = await api.get(`/projects/${projectId}/notes`)
      this.notesByProject = { ...this.notesByProject, [projectId]: resp.data }
    },
    async createNote(projectId, payload = {}) {
      const resp = await api.post(`/projects/${projectId}/notes`, payload)
      await this.fetchNotes(projectId)
      return resp.data
    },
    async openNote(noteId) {
      const resp = await api.get(`/notes/${noteId}`)
      this.activeNote = resp.data
      return resp.data
    },
    async updateNote(noteId, payload) {
      const resp = await api.patch(`/notes/${noteId}`, payload)
      this.activeNote = resp.data
      const projectId = resp.data.project_id
      const list = this.notesByProject[projectId]
      if (list) {
        const idx = list.findIndex((n) => n.id === noteId)
        if (idx !== -1) list[idx] = resp.data
      }
      return resp.data
    },
    async deleteNote(noteId, projectId) {
      await api.delete(`/notes/${noteId}`)
      if (this.activeNote?.id === noteId) this.activeNote = null
      await this.fetchNotes(projectId)
    },
    async uploadAttachment(noteId, file, kind = 'image') {
      const formData = new FormData()
      formData.append('file', file)
      const resp = await api.post(`/notes/${noteId}/attachments?kind=${kind}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return resp.data
    },
  },
})
