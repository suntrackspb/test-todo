import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

let accessToken = null
let refreshToken = null
let onAuthFailure = () => {}
let onTokensRefreshed = () => {}

export function setTokens(tokens) {
  accessToken = tokens?.access_token ?? null
  refreshToken = tokens?.refresh_token ?? null
}

export function setAuthFailureHandler(handler) {
  onAuthFailure = handler
}

export function setTokensRefreshedHandler(handler) {
  onTokensRefreshed = handler
}

export function getAccessToken() {
  return accessToken
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

let refreshPromise = null

async function performRefresh() {
  const resp = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
  setTokens(resp.data)
  return resp.data
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && refreshToken && !original._retry) {
      original._retry = true
      try {
        refreshPromise = refreshPromise || performRefresh()
        const tokens = await refreshPromise
        refreshPromise = null
        onTokensRefreshed(tokens)
        original.headers.Authorization = `Bearer ${tokens.access_token}`
        return api(original)
      } catch (refreshError) {
        refreshPromise = null
        setTokens(null)
        onAuthFailure()
        return Promise.reject(refreshError)
      }
    }
    if (error.response?.status === 401) {
      onAuthFailure()
    }
    return Promise.reject(error)
  },
)

export default api
