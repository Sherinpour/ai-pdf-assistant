import { useState } from 'react'
import { ChatInput } from '@/components/chat/ChatInput'
import { ChatMessages } from '@/components/chat/ChatMessages'
import { useDocumentContext } from '@/context/DocumentContext'
import { toChatErrorMessage, useChat } from '@/hooks/useChat'
import type { ChatMessagePayload, UiChatMessage } from '@/types/chat'

function createId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function ChatPage() {
  const { selectedDocument, messages, setMessages } = useDocumentContext()
  const chatMutation = useChat()
  const [error, setError] = useState<string | null>(null)

  const handleSend = async (content: string) => {
    if (!selectedDocument) {
      setError('Select a document before asking a question.')
      return
    }

    if (!content.trim()) {
      setError('Please enter a question.')
      return
    }

    setError(null)

    const userMessage: UiChatMessage = {
      id: createId(),
      role: 'user',
      content: content.trim(),
      createdAt: new Date().toISOString(),
    }

    const history: ChatMessagePayload[] = messages.map((message) => ({
      role: message.role,
      content: message.content,
    }))

    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await chatMutation.mutateAsync({
        question: userMessage.content,
        top_k: 5,
        history,
      })

      const assistantMessage: UiChatMessage = {
        id: createId(),
        role: 'assistant',
        content: response.answer,
        sources: response.found === false ? [] : response.sources,
        found: response.found,
        createdAt: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError(toChatErrorMessage(err))
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="min-h-0 flex-1">
        <ChatMessages
          messages={messages}
          hasDocument={Boolean(selectedDocument)}
          isThinking={chatMutation.isPending}
        />
      </div>

      {error && (
        <div className="border-t border-destructive/20 bg-destructive/5 px-4 py-2 text-sm text-destructive sm:px-6" role="alert">
          <div className="mx-auto max-w-3xl">{error}</div>
        </div>
      )}

      <ChatInput
        disabled={!selectedDocument}
        isSending={chatMutation.isPending}
        placeholder={
          selectedDocument
            ? `Ask something about ${selectedDocument.filename}…`
            : 'Upload and select a PDF to start chatting…'
        }
        onSend={(message) => {
          void handleSend(message)
        }}
      />
    </div>
  )
}
