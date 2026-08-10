import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function SettingsPage() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

  return (
    <div className="h-full overflow-auto px-4 py-8 sm:px-8">
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost" size="sm">
            <Link to="/">
              <ArrowLeft />
              Back to chat
            </Link>
          </Button>
        </div>

        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Settings</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Connection details for this local AI PDF Assistant.
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
          <h3 className="text-sm font-semibold">API</h3>
          <dl className="mt-4 space-y-3 text-sm">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
              <dt className="text-muted-foreground">Base URL</dt>
              <dd className="font-mono text-xs sm:text-sm">{apiBaseUrl}</dd>
            </div>
            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
              <dt className="text-muted-foreground">Chat endpoint</dt>
              <dd className="font-mono text-xs sm:text-sm">POST /chat/</dd>
            </div>
            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
              <dt className="text-muted-foreground">Upload endpoint</dt>
              <dd className="font-mono text-xs sm:text-sm">POST /upload/</dd>
            </div>
          </dl>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
          <h3 className="text-sm font-semibold">Documents</h3>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            The backend does not currently expose a document list API. Uploaded documents are
            tracked in this browser so you can select them for chat. Restarting the backend keeps
            vectors in ChromaDB, but the sidebar list is local until a documents endpoint is added.
          </p>
        </div>
      </div>
    </div>
  )
}
