import { SearchForm } from "@/features/SearchProducts"
import { Logo } from "@/shared/ui/Logo/ui/Logo"
import { UserButton } from "@/features/Auth"
import { FavoritesButton } from "@/features/FavoritesButton/FavoritesButton"
import { CartButton } from "@/features/CartButton/CartButton"
import { CatalogMenu } from "./CatalogMenu"

export const Header = () => {
  return (
    <header
      className="
      sticky top-0 z-[35] flex min-h-12 w-full max-w-5xl flex-row items-center justify-between
      gap-3 rounded-xl border border-brand-main/10 bg-brand-main/5 p-2 py-1.5 shadow-sm backdrop-blur-md"
    >
      <div className="flex min-w-0 items-center gap-3">
        <div className="hidden min-[450px]:block">
          <Logo />
        </div>
        <CatalogMenu />
      </div>

      {/* Поиск (занимает центральную часть) */}
      <div className="h-10 min-w-0 flex-1">
        <SearchForm />
      </div>

      {/* Правый блок с навигацией (Избранное, Корзина, Профиль) */}
      <nav className="flex shrink-0 items-center gap-1 sm:gap-2">
        <FavoritesButton className="w-7 h-7" />
        <CartButton className="w-7 h-7" />

        {/* Вертикальная линия-разделитель для красоты */}
        <div className="w-px h-6 bg-slate-200 mx-1 hidden sm:block"></div>

        <UserButton />
      </nav>
    </header>
  )
}
