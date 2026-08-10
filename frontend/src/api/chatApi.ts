import { apiClient } from '@/api/client'
import type { ChatRequest, ChatResponse } from '@/types/chat'

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/chat/', payload)
  return data
}
