import Link from "next/link"
import styles from "./Header.module.scss"
import { SearchForm } from "@/features/searchProducts"
import { Logo } from "@/shared/logo/ui/Logo"
import { LoginButton } from "@/features/auth"

export const Header = () => {
  return (
    // Семантичный тег header
    <header
      className="
      flex h-[8vw] min-h-12 w-full max-w-5xl max-h-12 items-center flex-row justify-between
      gap-[3vw] backdrop-blur rounded-xl sticky p-2 py-1.5 bg-[#edede295]"
    >
      <div className="hidden min-[450px]:block">
        <Logo />
      </div>
      <SearchForm />
      <LoginButton />
    </header>
  )
}
