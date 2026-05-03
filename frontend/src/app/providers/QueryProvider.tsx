"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"

export const QueryProvider = ({ children }: { children: React.ReactNode }) => {
  // Инициализируем QueryClient внутри useState, чтобы он создался один раз
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Настройка для SSR: данные считаются свежими некоторое время,
            // чтобы избежать двойных запросов при гидратации
            staleTime: parseInt(String(process.env.NEXT_REVALIDATE)) || 7200,
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}
