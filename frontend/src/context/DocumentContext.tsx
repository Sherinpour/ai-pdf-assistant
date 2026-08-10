import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from 'react'
import { useDocuments } from '@/hooks/useDocuments'
import type { DocumentRecord } from '@/types/pdf'
import type { UiChatMessage } from '@/types/chat'

interface DocumentContextValue {
  documents: DocumentRecord[]
  selectedDocument: DocumentRecord | null
  selectedId: string | null
  addDocument: ReturnType<typeof useDocuments>['addDocument']
  selectDocument: (id: string) => void
  removeDocument: (id: string) => void
  messages: UiChatMessage[]
  setMessages: Dispatch<SetStateAction<UiChatMessage[]>>
  clearChat: () => void
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
}

const DocumentContext = createContext<DocumentContextValue | null>(null)

export function DocumentProvider({ children }: { children: ReactNode }) {
  const docs = useDocuments()
  const [messagesByDoc, setMessagesByDoc] = useState<Record<string, UiChatMessage[]>>({})
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const chatKey = docs.selectedId ?? '__none__'
  const messages = useMemo(
    () => messagesByDoc[chatKey] ?? [],
    [messagesByDoc, chatKey],
  )

  const setMessages = useCallback<Dispatch<SetStateAction<UiChatMessage[]>>>(
    (updater) => {
      setMessagesByDoc((prev) => {
        const current = prev[chatKey] ?? []
        const next = typeof updater === 'function' ? updater(current) : updater
        return { ...prev, [chatKey]: next }
      })
    },
    [chatKey],
  )

  const clearChat = useCallback(() => {
    setMessagesByDoc((prev) => ({ ...prev, [chatKey]: [] }))
  }, [chatKey])

  const removeDocument = useCallback(
    (id: string) => {
      setMessagesByDoc((prev) => {
        const next = { ...prev }
        delete next[id]
        return next
      })
      docs.removeDocument(id)
    },
    [docs],
  )

  const value = useMemo(
    () => ({
      documents: docs.documents,
      selectedDocument: docs.selectedDocument,
      selectedId: docs.selectedId,
      addDocument: docs.addDocument,
      selectDocument: docs.selectDocument,
      removeDocument,
      messages,
      setMessages,
      clearChat,
      sidebarOpen,
      setSidebarOpen,
    }),
    [
      docs.documents,
      docs.selectedDocument,
      docs.selectedId,
      docs.addDocument,
      docs.selectDocument,
      removeDocument,
      messages,
      setMessages,
      clearChat,
      sidebarOpen,
    ],
  )

  return <DocumentContext.Provider value={value}>{children}</DocumentContext.Provider>
}

export function useDocumentContext() {
  const ctx = useContext(DocumentContext)
  if (!ctx) {
    throw new Error('useDocumentContext must be used within DocumentProvider')
  }
  return ctx
}
