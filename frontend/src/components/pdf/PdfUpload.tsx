import { useCallback, useRef, useState, type DragEvent, type ChangeEvent } from 'react'
import { FileText, Loader2, UploadCloud } from 'lucide-react'
import { useUploadPdf } from '@/hooks/useUploadPdf'
import { useDocumentContext } from '@/context/DocumentContext'
import { getErrorMessage } from '@/lib/errors'
import { cn, formatFileSize } from '@/lib/utils'
import { Button } from '@/components/ui/button'

interface PdfUploadProps {
  compact?: boolean
  className?: string
}

export function PdfUpload({ compact = false, className }: PdfUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const { addDocument } = useDocumentContext()
  const uploadMutation = useUploadPdf()

  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [progress, setProgress] = useState(0)
  const [phase, setPhase] = useState<'idle' | 'uploading' | 'processing' | 'success'>('idle')
  const [error, setError] = useState<string | null>(null)

  const resetInput = () => {
    if (inputRef.current) inputRef.current.value = ''
  }

  const validateFile = (file: File): string | null => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return 'Only PDF files are allowed.'
    }
    if (file.size === 0) {
      return 'Uploaded file is empty.'
    }
    return null
  }

  const handleFile = useCallback(
    async (file: File) => {
      const validationError = validateFile(file)
      if (validationError) {
        setError(validationError)
        setSelectedFile(null)
        setPhase('idle')
        return
      }

      setSelectedFile(file)
      setError(null)
      setProgress(0)
      setPhase('uploading')

      try {
        const response = await uploadMutation.mutateAsync({
          file,
          onProgress: (value) => {
            setProgress(value)
            if (value >= 100) setPhase('processing')
          },
        })

        addDocument(response, file.size)
        setPhase('success')
        setProgress(100)
        resetInput()
      } catch (err) {
        setPhase('idle')
        setError(getErrorMessage(err, 'Failed to upload PDF.'))
        resetInput()
      }
    },
    [addDocument, uploadMutation],
  )

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    const file = event.dataTransfer.files?.[0]
    if (file) void handleFile(file)
  }

  const onChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) void handleFile(file)
  }

  const isBusy = phase === 'uploading' || phase === 'processing'

  return (
    <div className={cn('space-y-3', className)}>
      <div
        role="button"
        tabIndex={0}
        aria-label="Upload PDF"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            inputRef.current?.click()
          }
        }}
        onClick={() => !isBusy && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={cn(
          'rounded-xl border border-dashed bg-card p-4 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring',
          isDragging ? 'border-primary bg-accent' : 'border-border hover:border-primary/40',
          isBusy && 'pointer-events-none opacity-80',
          compact ? 'p-3' : 'p-5',
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={onChange}
          disabled={isBusy}
        />

        <div className={cn('flex gap-3', compact ? 'items-center' : 'flex-col items-center text-center')}>
          <div className="flex size-10 items-center justify-center rounded-lg bg-accent text-accent-foreground">
            {isBusy ? <Loader2 className="size-5 animate-spin" /> : <UploadCloud className="size-5" />}
          </div>
          <div className={cn(compact ? 'min-w-0 flex-1 text-left' : 'space-y-1')}>
            <p className="text-sm font-medium text-foreground">
              {phase === 'uploading' && 'Uploading PDF…'}
              {phase === 'processing' && 'Processing document…'}
              {phase === 'success' && 'Upload complete'}
              {phase === 'idle' && 'Drop a PDF here or click to browse'}
            </p>
            <p className="text-xs text-muted-foreground">
              {isBusy
                ? phase === 'processing'
                  ? 'Extracting text, chunking, and indexing…'
                  : `${progress}% uploaded`
                : 'PDF files only'}
            </p>
          </div>
        </div>

        {isBusy && (
          <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all duration-300"
              style={{ width: `${phase === 'processing' ? 100 : progress}%` }}
            />
          </div>
        )}
      </div>

      {selectedFile && (
        <div className="flex items-start gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm">
          <FileText className="mt-0.5 size-4 shrink-0 text-primary" />
          <div className="min-w-0 flex-1">
            <p className="truncate font-medium">{selectedFile.name}</p>
            <p className="text-xs text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
          </div>
          {phase === 'success' && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => {
                setPhase('idle')
                setSelectedFile(null)
                setProgress(0)
              }}
            >
              Clear
            </Button>
          )}
        </div>
      )}

      {error && (
        <p className="rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
