import axios from 'axios'
import { config } from '@/lib/config'

export class ApiNotFoundError extends Error {
  constructor(message = 'Not found') {
    super(message)
    this.name = 'ApiNotFoundError'
  }
}

export class ApiServerError extends Error {
  constructor(message = 'Server error') {
    super(message)
    this.name = 'ApiServerError'
  }
}

export class ApiNetworkError extends Error {
  constructor(message = 'Network error') {
    super(message)
    this.name = 'ApiNetworkError'
  }
}

const apiClient = axios.create({
  baseURL: config.apiUrl,
  timeout: 10_000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      throw new ApiNetworkError()
    }
    const status: number = error.response.status
    if (status === 404) throw new ApiNotFoundError()
    if (status >= 500) throw new ApiServerError()
    throw error
  },
)

export default apiClient
