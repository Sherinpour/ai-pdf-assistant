import { FileUp, MessagesSquare } from 'lucide-react'

interface ChatEmptyStateProps {
  hasDocument: boolean
}

export function ChatEmptyState({ hasDocument }: ChatEmptyStateProps) {
  if (!hasDocument) {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center px-6 py-16 text-center">
        <div className="mb-4 flex size-14 items-center justify-center rounded-2xl bg-accent text-accent-foreground shadow-sm">
          <FileUp className="size-6" />
        </div>
        <h2 className="text-xl font-semibold tracking-tight">Upload a PDF to get started</h2>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
          Upload a document from the sidebar and start asking questions about it.
        </p>
      </div>
    )
  }

  return (
    <div className="mx-auto flex max-w-md flex-col items-center px-6 py-16 text-center">
      <div className="mb-4 flex size-14 items-center justify-center rounded-2xl bg-accent text-accent-foreground shadow-sm">
        <MessagesSquare className="size-6" />
      </div>
      <h2 className="text-xl font-semibold tracking-tight">Ask anything about your document</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        I can help you summarize, explain, or find information inside your PDF.
      </p>
    </div>
  )
}
