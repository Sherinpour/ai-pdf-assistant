import { useMutation } from '@tanstack/react-query'
import { sendChatMessage } from '@/api/chatApi'
import { getErrorMessage } from '@/lib/errors'
import type { ChatRequest, ChatResponse } from '@/types/chat'

export function useChat() {
  return useMutation<ChatResponse, Error, ChatRequest>({
    mutationFn: sendChatMessage,
    meta: {
      errorMessage: 'Failed to get a response.',
    },
  })
}

export function toChatErrorMessage(error: unknown): string {
  return getErrorMessage(error, 'Failed to get a response from the assistant.')
}
