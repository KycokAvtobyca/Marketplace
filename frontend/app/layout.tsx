import type { Metadata } from "next"
import "@/app/styles/globals.scss"
import { AuthWindow } from "@/widgets/auth-window/ui/AuthWindow"

export const metadata: Metadata = {
  title: "Маркетплейс Флоппи",
  description: "Курсовая работа Лыскова Ивана: Маркетплейс на Next.js + Django",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body className="items-center min-h-screen flex flex-col bg-default text-brand-main">
        <div className="max-w-5xl p-3 w-full relative">
          <main className="grow">{children}</main>
        </div>

        <div id="modals" className="z-40">
          <AuthWindow />
        </div>
      </body>
    </html>
  )
}
