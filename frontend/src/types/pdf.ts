export interface UploadPdfResponse {
  filename: string
  status: string
  page_count: number
  chunk_count: number
  replaced_chunks?: number
  timings?: {
    extract_s: number
    chunk_s: number
    embed_s: number
    store_s: number
    total_s: number
  }
}

export interface DeletePdfResponse {
  filename: string
  status: string
  deleted_chunks: number
  file_removed: boolean
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
