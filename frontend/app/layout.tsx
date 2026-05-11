import type { Metadata } from "next"
import "@/app/styles/globals.scss"
import { QueryProvider } from "@/app/providers/QueryProvider"

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
  return (
    <QueryProvider>
      <html lang="ru">
        <body className="items-center min-h-screen flex flex-col bg-default text-brand-main">
          <div className="max-w-5xl p-3 w-full relative">
            <main className="grow space-y-5">
              <div className="flex min-[450px]:hidden">{/* Header 2 */}</div>
              {children}
            </main>
          </div>

          {/* Элементы сюда добавляются через portal */}
          <div id="dropdowns" className="z-30"></div>
          <div id="modals" className="z-40"></div>
        </body>
      </html>
    </QueryProvider>
  )
}
