import axios from 'axios'

export function getErrorMessage(error: unknown, fallback = 'Something went wrong.'): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        return 'The request timed out. Please try again.'
      }
      return 'Unable to reach the server. Make sure the backend is running.'
    }

    const detail = error.response.data?.detail
    if (typeof detail === 'string' && detail.trim()) {
      return detail
    }
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0]
      if (typeof first === 'string') return first
      if (first && typeof first === 'object' && 'msg' in first) {
        return String(first.msg)
      }
    }

    if (error.response.status >= 500) {
      return 'The server encountered an error. Please try again.'
    }
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}
