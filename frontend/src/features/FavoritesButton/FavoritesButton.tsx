"use client"

import Link from "next/link"
import { useGetFavorites } from "@/entities/favorites/api/useFavorites"
import { useAuthWindowStore } from "@/entities/authWindow"
import { useAuthStore } from "@/entities/auth"
import { Icon } from "@/shared/ui/Icons/Icon"
import { useProfile } from "@/entities/user/api/useProfile"
import { ROUTES } from "@/shared/config/routes"

export const FavoritesButton = ({ className }: { className?: string }) => {
  const { data, isError } = useGetFavorites()
  const { data: profile } = useProfile()
  const toggleAuthWindow = useAuthWindowStore((s) => s.toggle)
  const authStoreIsAuth = useAuthStore((s) => s.isAuth)

  // Проверяем авторизацию через профиль ИЛИ стор (для мгновенной реакции после входа)
  const isAuth = (!!profile && !isError) || authStoreIsAuth
  const count = data?.favorite_items?.length || 0

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (!isAuth) {
      e.preventDefault()
      toggleAuthWindow()
    }
  }

  return (
    <Link
      href={ROUTES.FAVORITES.ROOT || "/favorites"}
      onClick={handleClick}
      className="relative p-1 text-slate-700 hover:text-brand-main hover:bg-white/50 rounded-xl transition-all"
    >
      <Icon.HEARTBRAND className={`w-6 h-6 ${className}`} />

      {/* Бейджик со счетчиком */}
      {isAuth && count > 0 && (
        <span className="absolute top-0 right-0 inline-flex items-center justify-center w-4 h-4 text-[10px] font-bold text-white bg-red-500 rounded-full border-2 border-slate-50 animate-in zoom-in">
          {count}
        </span>
      )}
    </Link>
  )
}
