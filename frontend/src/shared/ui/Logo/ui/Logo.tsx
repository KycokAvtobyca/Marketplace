import Link from "next/link"
import { ROUTES } from "@/shared/config/routes"

export const Logo = () => {
  return (
    <Link href={ROUTES.HOME}>
      <h1 className="text-brand-main text-xl shrink-0">Флоппи</h1>
    </Link>
  )
}
