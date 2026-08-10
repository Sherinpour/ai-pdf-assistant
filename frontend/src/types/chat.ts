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

export interface ChatTimings {
  retrieve_s: number
  prompt_s: number
  llm_s: number
  total_s: number
}

export interface ChatResponse {
  answer: string
  sources: ChatSource[]
  found?: boolean
  timings?: ChatTimings
}

export interface UiChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: ChatSource[]
  found?: boolean
  createdAt: string
}
