import type { Metadata } from "next"
import { Inter } from "next/font/google"
// import "@/shared/styles/_tailwind.css"
import "@/app/styles/globals.scss"
import { Header } from "@/widgets/header"

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
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <Header />
        <main className="grow">{children}</main>
      </body>
    </html>
  )
}
