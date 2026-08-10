import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { SendHorizonal } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface ChatInputProps {
  disabled?: boolean
  isSending?: boolean
  placeholder?: string
  onSend: (message: string) => void
}

export function ChatInput({
  disabled = false,
  isSending = false,
  placeholder = 'Ask something about this PDF…',
  onSend,
}: ChatInputProps) {
  const [value, setValue] = useState('')

  const trimmed = value.trim()
  const canSend = !disabled && !isSending && trimmed.length > 0

  const submit = () => {
    if (!canSend) return
    onSend(trimmed)
    setValue('')
  }

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    submit()
  }

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      className="border-t border-border bg-card/90 px-4 py-3 backdrop-blur-sm sm:px-6"
    >
      <div className="mx-auto flex max-w-3xl items-end gap-2">
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          disabled={disabled || isSending}
          rows={1}
          className="min-h-[48px] max-h-40 flex-1"
          aria-label="Message"
        />
        <Button type="submit" size="icon" disabled={!canSend} aria-label="Send message">
          <SendHorizonal className="size-4" />
        </Button>
      </div>
      <p className="mx-auto mt-2 max-w-3xl text-[11px] text-muted-foreground">
        Enter to send · Shift + Enter for a new line
      </p>
    </form>
  )
}
