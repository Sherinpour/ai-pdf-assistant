import { FileText } from 'lucide-react'
import { useDocumentContext } from '@/context/DocumentContext'
import { cn, formatFileSize } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

interface DocumentListProps {
  onSelect?: () => void
}

export function DocumentList({ onSelect }: DocumentListProps) {
  const { documents, selectedId, selectDocument } = useDocumentContext()

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
    <ScrollArea className="max-h-[40vh] pr-1">
      <ul className="space-y-1.5">
        {documents.map((doc) => {
          const active = doc.id === selectedId
          return (
            <li key={doc.id}>
              <button
                type="button"
                onClick={() => {
                  selectDocument(doc.id)
                  onSelect?.()
                }}
                className={cn(
                  'flex w-full items-start gap-2.5 rounded-xl border px-3 py-2.5 text-left transition-colors',
                  active
                    ? 'border-primary/30 bg-accent shadow-sm'
                    : 'border-transparent bg-transparent hover:bg-muted',
                )}
              >
                <FileText
                  className={cn('mt-0.5 size-4 shrink-0', active ? 'text-primary' : 'text-muted-foreground')}
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
            </li>
          )
        })}
      </ul>
    </ScrollArea>
  )
}
