export interface UploadPdfResponse {
  filename: string
  status: string
  page_count: number
  chunk_count: number
}

export interface DocumentRecord {
  id: string
  filename: string
  status: string
  pageCount: number
  chunkCount: number
  uploadedAt: string
  fileSize?: number
}
