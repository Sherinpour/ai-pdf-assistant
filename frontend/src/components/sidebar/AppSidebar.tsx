import { Link, useLocation } from 'react-router-dom'
import { FileStack, MessageSquarePlus, Settings, Sparkles } from 'lucide-react'
import { DocumentList } from '@/components/sidebar/DocumentList'
import { PdfUpload } from '@/components/pdf/PdfUpload'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useDocumentContext } from '@/context/DocumentContext'
import { cn } from '@/lib/utils'

interface AppSidebarProps {
  className?: string
  onNavigate?: () => void
}

export function AppSidebar({ className, onNavigate }: AppSidebarProps) {
  const location = useLocation()
  const { clearChat, selectedDocument } = useDocumentContext()

  return (
    <aside
      className={cn(
        'flex h-full w-full flex-col bg-sidebar text-sidebar-foreground',
        className,
      )}
    >
      <div className="flex items-center gap-2.5 px-4 py-4">
        <div className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
          <Sparkles className="size-4" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold tracking-tight">AI PDF Assistant</p>
          <p className="truncate text-xs text-muted-foreground">Chat with your documents</p>
        </div>
      </div>

      <div className="px-3">
        <Button
          className="w-full justify-start"
          onClick={() => {
            clearChat()
            onNavigate?.()
          }}
          disabled={!selectedDocument}
        >
          <MessageSquarePlus />
          New Chat
        </Button>
      </div>

      <div className="mt-4 flex-1 space-y-4 overflow-hidden px-3 pb-3">
        <div className="space-y-2">
          <div className="flex items-center gap-2 px-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            <FileStack className="size-3.5" />
            Documents
          </div>
          <PdfUpload compact />
          <DocumentList onSelect={onNavigate} />
        </div>
      </div>

      <Separator />
      <div className="p-3">
        <Link
          to="/settings"
          onClick={onNavigate}
          className={cn(
            'flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-muted',
            location.pathname === '/settings' && 'bg-muted font-medium',
          )}
        >
          <Settings className="size-4 text-muted-foreground" />
          Settings
        </Link>
      </div>
    </aside>
  )
}
