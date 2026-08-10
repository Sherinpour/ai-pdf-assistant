import { Menu } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useDocumentContext } from '@/context/DocumentContext'

interface AppHeaderProps {
  onOpenSidebar: () => void
}

export function AppHeader({ onOpenSidebar }: AppHeaderProps) {
  const { selectedDocument } = useDocumentContext()

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-3 border-b border-border bg-card/80 px-4 backdrop-blur-sm">
      <div className="flex min-w-0 items-center gap-2">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onOpenSidebar}
          aria-label="Open sidebar"
        >
          <Menu className="size-5" />
        </Button>
        <div className="min-w-0">
          <h1 className="truncate text-sm font-semibold tracking-tight sm:text-base">
            AI PDF Assistant
          </h1>
          <p className="hidden text-xs text-muted-foreground sm:block">
            Ask questions grounded in your uploaded PDFs
          </p>
        </div>
      </div>

      <div className="flex min-w-0 items-center gap-2">
        {selectedDocument ? (
          <Badge variant="outline" className="max-w-[14rem] truncate sm:max-w-xs">
            {selectedDocument.filename}
          </Badge>
        ) : (
          <span className="text-xs text-muted-foreground">No PDF selected</span>
        )}
      </div>
    </header>
  )
}
