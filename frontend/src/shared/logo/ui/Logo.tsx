import Link from "next/link"
import { ROUTES } from "@/shared/config/routes"
import styles from "./Logo.module.scss"

export const Logo = () => {
  return (
    <Link href={ROUTES.HOME}>
      <h1 className="text-brand-main text-xl shrink-0">СППППП</h1>
    </Link>
  )
}
