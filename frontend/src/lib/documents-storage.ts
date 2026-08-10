import type { DocumentRecord } from '@/types/pdf'

const STORAGE_KEY = 'ai-pdf-assistant.documents'

export function loadDocuments(): DocumentRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed: unknown = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.filter(isDocumentRecord)
  } catch {
    return []
  }
}

export function saveDocuments(documents: DocumentRecord[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(documents))
}

function isDocumentRecord(value: unknown): value is DocumentRecord {
  if (!value || typeof value !== 'object') return false
  const doc = value as Record<string, unknown>
  return (
    typeof doc.id === 'string' &&
    typeof doc.filename === 'string' &&
    typeof doc.status === 'string' &&
    typeof doc.pageCount === 'number' &&
    typeof doc.chunkCount === 'number' &&
    typeof doc.uploadedAt === 'string'
  )
}
