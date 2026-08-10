import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { DocumentProvider } from '@/context/DocumentContext'
import { AppRouter } from '@/routes'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <DocumentProvider>
        <AppRouter />
      </DocumentProvider>
    </QueryClientProvider>
  )
}
