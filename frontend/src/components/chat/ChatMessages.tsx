import { useEffect, useRef } from 'react'
import { Loader2 } from 'lucide-react'
import { ChatEmptyState } from '@/components/chat/ChatEmptyState'
import { MessageBubble } from '@/components/chat/MessageBubble'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { UiChatMessage } from '@/types/chat'

interface ChatMessagesProps {
  messages: UiChatMessage[]
  hasDocument: boolean
  isThinking: boolean
}

export function ChatMessages({ messages, hasDocument, isThinking }: ChatMessagesProps) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, isThinking])

  if (messages.length === 0 && !isThinking) {
    return (
      <div className="flex h-full items-center justify-center">
        <ChatEmptyState hasDocument={hasDocument} />
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="mx-auto flex max-w-3xl flex-col gap-4 px-4 py-6 sm:px-6">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isThinking && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-2xl rounded-bl-md border border-border bg-card px-4 py-3 text-sm text-muted-foreground shadow-sm">
              <Loader2 className="size-4 animate-spin text-primary" />
              Thinking…
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>
    </ScrollArea>
  )
}
