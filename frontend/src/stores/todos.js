import { defineStore } from 'pinia'
import api from '@/api/client'

export const useTodosStore = defineStore('todos', {
  state: () => ({
    todosByProject: {},
  }),
  actions: {
    async fetchTodos(projectId, status = null) {
      const params = status ? { status } : {}
      const resp = await api.get(`/projects/${projectId}/todos`, { params })
      this.todosByProject = { ...this.todosByProject, [projectId]: resp.data }
    },
    async createTodo(projectId, payload) {
      await api.post(`/projects/${projectId}/todos`, payload)
      await this.fetchTodos(projectId)
    },
    async updateTodo(todoId, projectId, payload) {
      await api.patch(`/todos/${todoId}`, payload)
      await this.fetchTodos(projectId)
    },
    async deleteTodo(todoId, projectId) {
      await api.delete(`/todos/${todoId}`)
      await this.fetchTodos(projectId)
    },
  },
})
