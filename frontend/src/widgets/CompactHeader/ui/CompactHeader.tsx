"use client"

import { SearchForm } from "@/features/SearchProducts"
import { UserButton } from "@/features/Auth"
import { FavoritesButton } from "@/features/FavoritesButton/FavoritesButton"
import { CartButton } from "@/features/CartButton/CartButton"
import { CatalogMenu } from "@/widgets/Header/ui/CatalogMenu"

export const CompactHeader = () => {
  return (
    <header className="sticky top-0 z-[35] flex w-full flex-col gap-2 rounded-xl border border-brand-main/10 bg-brand-main/5 p-2 shadow-sm backdrop-blur-md">
      <div className="flex h-10 w-full items-center gap-2">
        <div className="h-full min-w-0 flex-1">
          <SearchForm />
        </div>

        <nav className="flex shrink-0 items-center gap-1">
          <FavoritesButton className="h-6 w-6" />
          <CartButton className="h-6 w-6" />
          <UserButton />
        </nav>
      </div>

      <CatalogMenu compact buttonClassName="w-full justify-center" />
    </header>
  )
}
