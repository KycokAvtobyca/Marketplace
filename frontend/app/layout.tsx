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

export const revalidate = parseInt(String(process.env.NEXT_REVALIDATE)) || 7200

export const metadata: Metadata = {
  title: "Маркетплейс Флоппи",
  description: "Курсовая работа Лыскова Ивана: Маркетплейс на Next.js + Django",
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
        <body className="items-center min-h-screen flex flex-col bg-default text-brand-main">
          <HydrationBoundary state={dehydrate(queryClient)}>
            <div className="max-w-5xl p-3 w-full relative flex flex-col min-h-screen">
              <Header />
              <div className="h-4 sm:h-6" />
              <main className="grow space-y-5 pb-10">
                <div className="flex min-[450px]:hidden">
                  <CompactHeader />
                </div>
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
