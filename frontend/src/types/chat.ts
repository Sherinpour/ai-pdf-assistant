export interface ChatMessagePayload {
  role: 'user' | 'assistant' | string
  content: string
}

export interface ChatRequest {
  question: string
  top_k?: number
  history?: ChatMessagePayload[]
}

export interface ChatSource {
  page: number
  source: string
  distance: number
}

export interface ChatResponse {
  answer: string
  sources: ChatSource[]
}

export interface UiChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: ChatSource[]
  createdAt: string
}
