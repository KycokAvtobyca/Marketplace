import Link from "next/link"
import styles from "./Header.module.scss"
import { SearchForm } from "@/features/search-products"
import { Logo } from "@/shared/logo/ui/Logo"
import { LoginButton } from "@/features/auth"

export const Header = () => {
  return (
    // Семантичный тег header
    <header className="flex items-center flex-row justify-between gap-6 gap backdrop-blur rounded-xl sticky p-2 bg-[#edede295]">
      <Logo />
      <SearchForm />
      <LoginButton />
    </header>
  )
}
