import api from '@/api/client'

export async function fetchCalendarRange(from, to, projectId = null) {
  const params = { from, to }
  if (projectId) params.project_id = projectId
  const resp = await api.get('/calendar', { params })
  return resp.data
}
