"use client"

import { SearchForm } from "@/features/SearchProducts"
import { UserButton } from "@/features/Auth"
import { FavoritesButton } from "@/features/FavoritesButton/FavoritesButton"
import { CartButton } from "@/features/CartButton/CartButton"

export const CompactHeader = () => {
  return (
    <header className="flex h-12 w-full items-center gap-2 backdrop-blur-md rounded-xl sticky top-4 z-[35] p-2 bg-brand-main/5 border border-brand-main/10 shadow-sm">
      {/* Поиск (занимает основную часть) */}
      <div className="flex-1 h-full">
        <SearchForm />
      </div>

      {/* Иконки */}
      <nav className="flex items-center gap-1 shrink-0">
        <FavoritesButton className="w-6 h-6" />
        <CartButton className="w-6 h-6" />
        <UserButton />
      </nav>
    </header>
  )
}
