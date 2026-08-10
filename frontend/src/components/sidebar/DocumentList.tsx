import { useState } from 'react'
import { FileText, Loader2, Trash2 } from 'lucide-react'
import { useDocumentContext } from '@/context/DocumentContext'
import { useDeletePdf } from '@/hooks/useDeletePdf'
import { getErrorMessage } from '@/lib/errors'
import { cn, formatFileSize } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { DocumentRecord } from '@/types/pdf'

interface DocumentListProps {
  onSelect?: () => void
}

export function DocumentList({ onSelect }: DocumentListProps) {
  const { documents, selectedId, selectDocument, removeDocument } = useDocumentContext()
  const deleteMutation = useDeletePdf()
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleDelete = async (doc: DocumentRecord) => {
    const confirmed = window.confirm(`Delete "${doc.filename}"? This removes it from chat and the search index.`)
    if (!confirmed) return

    setError(null)
    setDeletingId(doc.id)

    try {
      await deleteMutation.mutateAsync(doc.filename)
      removeDocument(doc.id)
    } catch (err) {
      // If the file is only in local UI state, still allow removing it locally.
      const message = getErrorMessage(err, 'Failed to delete PDF.')
      if (message.toLowerCase().includes('not found')) {
        removeDocument(doc.id)
      } else {
        setError(message)
      }
    } finally {
      setDeletingId(null)
    }
  }

  if (documents.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-border bg-muted/40 px-3 py-6 text-center">
        <p className="text-sm font-medium text-foreground">No documents yet</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Upload a PDF to start chatting with your documents.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <ScrollArea className="max-h-[40vh] pr-1">
        <ul className="space-y-1.5">
          {documents.map((doc) => {
            const active = doc.id === selectedId
            const isDeleting = deletingId === doc.id

            return (
              <li key={doc.id}>
                <div
                  className={cn(
                    'flex w-full items-start gap-1 rounded-xl border px-2 py-2 transition-colors',
                    active
                      ? 'border-primary/30 bg-accent shadow-sm'
                      : 'border-transparent bg-transparent hover:bg-muted',
                  )}
                >
                  <button
                    type="button"
                    onClick={() => {
                      selectDocument(doc.id)
                      onSelect?.()
                    }}
                    className="flex min-w-0 flex-1 items-start gap-2.5 rounded-lg px-1 py-0.5 text-left"
                  >
                    <FileText
                      className={cn(
                        'mt-0.5 size-4 shrink-0',
                        active ? 'text-primary' : 'text-muted-foreground',
                      )}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-foreground">{doc.filename}</p>
                      <div className="mt-1 flex flex-wrap items-center gap-1.5">
                        <Badge variant={doc.status === 'uploaded' ? 'default' : 'secondary'}>
                          {doc.status}
                        </Badge>
                        <span className="text-[11px] text-muted-foreground">
                          {doc.pageCount} {doc.pageCount === 1 ? 'page' : 'pages'}
                        </span>
                        {typeof doc.fileSize === 'number' && (
                          <span className="text-[11px] text-muted-foreground">
                            · {formatFileSize(doc.fileSize)}
                          </span>
                        )}
                      </div>
                    </div>
                  </button>

                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-8 shrink-0 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                    aria-label={`Delete ${doc.filename}`}
                    disabled={isDeleting || deleteMutation.isPending}
                    onClick={(event) => {
                      event.stopPropagation()
                      void handleDelete(doc)
                    }}
                  >
                    {isDeleting ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Trash2 className="size-4" />
                    )}
                  </Button>
                </div>
              </li>
            )
          })}
        </ul>
      </ScrollArea>

      {error && (
        <p className="rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-xs text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
