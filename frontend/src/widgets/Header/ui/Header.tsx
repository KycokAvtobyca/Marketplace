import { SearchForm } from "@/features/SearchProducts"
import { Logo } from "@/shared/ui/Logo/ui/Logo"
import { UserButton } from "@/features/Auth"
import { FavoritesButton } from "@/features/FavoritesButton/FavoritesButton"
import { CartButton } from "@/features/CartButton/CartButton"

export const Header = () => {
  return (
    <header
      className="
      flex h-[8vw] min-h-12 w-full max-w-5xl max-h-12 items-center flex-row justify-between
      gap-[3vw] backdrop-blur-md rounded-xl sticky top-4 z-[35] p-2 py-1.5 bg-brand-main/5 border border-brand-main/10 shadow-sm"
    >
      {/* Логотип */}
      <div className="hidden min-[450px]:block">
        <Logo />
      </div>

      {/* Поиск (занимает центральную часть) */}
      <div className="flex-1 h-full max-w-xl">
        <SearchForm />
      </div>

      {/* Правый блок с навигацией (Избранное, Корзина, Профиль) */}
      <nav className="flex items-center gap-1 sm:gap-2 shrink-0">
        <FavoritesButton className="w-7 h-7" />
        <CartButton className="w-7 h-7" />

        {/* Вертикальная линия-разделитель для красоты */}
        <div className="w-px h-6 bg-slate-200 mx-1 hidden sm:block"></div>

        <UserButton />
      </nav>
    </header>
  )
}
