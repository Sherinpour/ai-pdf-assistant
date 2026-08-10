import { useMutation } from '@tanstack/react-query'
import { uploadPdf } from '@/api/pdfApi'
import type { UploadPdfResponse } from '@/types/pdf'

interface UploadVariables {
  file: File
  onProgress?: (progress: number) => void
}

export function useUploadPdf() {
  return useMutation<UploadPdfResponse, Error, UploadVariables>({
    mutationFn: ({ file, onProgress }) => uploadPdf(file, onProgress),
  })
}
