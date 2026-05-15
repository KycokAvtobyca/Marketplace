import type { Metadata } from "next"
import "@/app/styles/globals.scss"
import { QueryProvider } from "@/app/providers/QueryProvider"
import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query"
import { cookies } from "next/headers"
import { api } from "@/shared/api"
import { Footer } from "@/widgets/Footer"
import { CompactHeader } from "@/widgets/CompactHeader"
import { Header } from "@/widgets/Header"
import { AuthWindow } from "@/widgets/AuthWindow/ui/AuthWindow"

export const revalidate = 7200

export const metadata: Metadata = {
  title: "Маркетплейс Флоппи",
  description: "Маркетплейс на Next.js + Django",
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const queryClient = new QueryClient()
  const cookieStore = await cookies()
  const accessToken = cookieStore.get("access_token")?.value

  // Если в куках есть токен, пробуем "прогреть" кэш на сервере
  if (accessToken) {
    await queryClient.prefetchQuery({
      queryKey: ["profile"],
      queryFn: async () => {
        // На сервере axios не видит куки сам, передаем их вручную
        const { data } = await api.get("/users/profile/", {
          headers: { Cookie: `access_token=${accessToken}` },
        })
        return data
      },
    })
  }
  return (
    <QueryProvider>
      <html lang="ru">
        <body className="flex min-h-screen flex-col items-center overflow-x-hidden bg-default text-brand-main">
          <HydrationBoundary state={dehydrate(queryClient)}>
            <div className="relative flex min-h-screen w-full max-w-5xl flex-col px-2 py-3 sm:px-3">
              <div className="sticky top-0 z-[35] hidden sm:block">
                <Header />
              </div>
              <div className="sticky top-0 z-[35] block sm:hidden">
                <CompactHeader />
              </div>
              <div className="h-4 sm:h-6" />
              <main className="grow space-y-5 pb-10">
                {children}
              </main>
              <AuthWindow />
              <Footer />
            </div>

            {/* Элементы сюда добавляются через portal */}
            <div id="dropdowns" className="z-30"></div>
            <div id="modals" className="z-40"></div>
          </HydrationBoundary>
        </body>
      </html>
    </QueryProvider>
  )
}
