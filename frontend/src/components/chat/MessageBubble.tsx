import { cn } from '@/lib/utils'
import type { UiChatMessage } from '@/types/chat'

interface MessageBubbleProps {
  message: UiChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const showSources =
    !isUser &&
    message.found !== false &&
    Boolean(message.sources && message.sources.length > 0)

  return (
    <div className={cn('flex w-full', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[min(42rem,92%)] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm',
          isUser
            ? 'rounded-br-md bg-primary text-primary-foreground'
            : 'rounded-bl-md border border-border bg-card text-card-foreground',
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>

        {showSources && (
          <div className="mt-3 border-t border-border/70 pt-2">
            <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
              Sources
            </p>
            <ul className="space-y-1">
              {message.sources!.map((source, index) => (
                <li
                  key={`${source.source}-${source.page}-${index}`}
                  className="text-xs text-muted-foreground"
                >
                  {source.source} · page {source.page}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
