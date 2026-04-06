import Link from "next/link"
import styles from "./Header.module.scss"
import { SearchForm } from "@/features/searchProducts"
import { Logo } from "@/shared/logo/ui/Logo"
import { LoginButton } from "@/features/auth"

export const Header = () => {
  return (
    // Семантичный тег header
    <header className="flex h-12 items-center flex-row justify-between gap-6 backdrop-blur rounded-xl sticky p-2 bg-[#edede295]">
      <Logo />
      <SearchForm />
      <LoginButton />
    </header>
  )
}
