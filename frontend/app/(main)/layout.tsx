import { AuthWindow } from "@/widgets/AuthWindow/ui/AuthWindow"
import { Header } from "@/widgets/Header"

export const revalidate = 3600

export default function HomeLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <Header />
      {children}

      {/* Модальные окна */}
      <AuthWindow />
    </>
  )
}
