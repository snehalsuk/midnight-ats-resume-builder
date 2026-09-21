import axios from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export const apiClient = axios.create({ baseURL: API_BASE_URL })

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// If the stored token is rejected (expired/invalid), clear it and send the
// user back to login instead of leaving the app in a silently-broken state
// where every request 401s with no explanation.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401 && window.location.pathname !== '/login') {
      localStorage.removeItem('accessToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export interface ApiErrorBody {
  success: false
  errorCode: string
  message: string
  details?: unknown
}

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined
    if (body?.message) return body.message
    return error.message
  }
  return 'An unexpected error occurred.'
}
