import { apiClient } from '@/api/client'
import type { UploadPdfResponse } from '@/types/pdf'

export async function uploadPdf(
  file: File,
  onUploadProgress?: (progress: number) => void,
): Promise<UploadPdfResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await apiClient.post<UploadPdfResponse>('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (event) => {
      if (!onUploadProgress || !event.total) return
      onUploadProgress(Math.round((event.loaded / event.total) * 100))
    },
  })

  return data
}
