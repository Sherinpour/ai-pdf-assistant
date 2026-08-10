import { useCallback, useEffect, useState } from 'react'
import { loadDocuments, saveDocuments } from '@/lib/documents-storage'
import type { DocumentRecord, UploadPdfResponse } from '@/types/pdf'

/**
 * Documents are persisted locally because the backend has no list endpoint.
 * When a GET /documents/ API is added, swap the storage layer for a React Query fetch.
 */
export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentRecord[]>(() => loadDocuments())
  const [selectedId, setSelectedId] = useState<string | null>(() => {
    const docs = loadDocuments()
    return docs[0]?.id ?? null
  })

  useEffect(() => {
    saveDocuments(documents)
  }, [documents])

  const addDocument = useCallback((response: UploadPdfResponse, fileSize?: number) => {
    const record: DocumentRecord = {
      id: `${response.filename}-${Date.now()}`,
      filename: response.filename,
      status: response.status,
      pageCount: response.page_count,
      chunkCount: response.chunk_count,
      uploadedAt: new Date().toISOString(),
      fileSize,
    }

    setDocuments((prev) => {
      const withoutDup = prev.filter((doc) => doc.filename !== record.filename)
      return [record, ...withoutDup]
    })
    setSelectedId(record.id)
    return record
  }, [])

  const selectDocument = useCallback((id: string) => {
    setSelectedId(id)
  }, [])

  const removeDocument = useCallback((id: string) => {
    setDocuments((prev) => {
      const remaining = prev.filter((doc) => doc.id !== id)
      setSelectedId((current) => {
        if (current !== id) return current
        return remaining[0]?.id ?? null
      })
      return remaining
    })
  }, [])

  const selectedDocument = documents.find((doc) => doc.id === selectedId) ?? null

  return {
    documents,
    selectedDocument,
    selectedId,
    addDocument,
    selectDocument,
    removeDocument,
    setSelectedId,
  }
}
