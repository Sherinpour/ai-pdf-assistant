import { useMutation } from '@tanstack/react-query'
import { deletePdf } from '@/api/pdfApi'
import type { DeletePdfResponse } from '@/types/pdf'

export function useDeletePdf() {
  return useMutation<DeletePdfResponse, Error, string>({
    mutationFn: deletePdf,
  })
}
