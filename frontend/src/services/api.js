import axios from 'axios'
import toast from 'react-hot-toast'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('voyage_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const detail = error?.response?.data?.detail

    if (status === 401) {
      localStorage.removeItem('voyage_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else if (status === 403) {
      toast.error('You do not have permission to do this.')
    } else if (status === 422) {
      toast.error('Invalid input. Please check your data.')
    } else if (status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (detail) {
      toast.error(detail)
    }

    return Promise.reject(error)
  }
)

export default api
