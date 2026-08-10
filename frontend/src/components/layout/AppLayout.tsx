import { Outlet } from 'react-router-dom'
import { AppHeader } from '@/components/layout/AppHeader'
import { AppSidebar } from '@/components/sidebar/AppSidebar'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { useDocumentContext } from '@/context/DocumentContext'

export function AppLayout() {
  const { sidebarOpen, setSidebarOpen } = useDocumentContext()

  return (
    <div className="flex h-full min-h-0 overflow-hidden">
      <div className="hidden w-72 shrink-0 border-r border-sidebar-border lg:block">
        <AppSidebar />
      </div>

      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 lg:hidden">
          <SheetHeader className="sr-only">
            <SheetTitle>Navigation</SheetTitle>
          </SheetHeader>
          <AppSidebar onNavigate={() => setSidebarOpen(false)} />
        </SheetContent>
      </Sheet>

      <div className="flex min-w-0 flex-1 flex-col">
        <AppHeader onOpenSidebar={() => setSidebarOpen(true)} />
        <main className="min-h-0 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
