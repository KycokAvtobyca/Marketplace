"use client"

import Link from "next/link"
import { useGetCart } from "@/entities/cart/api/useCart"
import { useAuthWindowStore } from "@/entities/authWindow"
import { Icon } from "@/shared/ui/Icons/Icon"
import { useProfile } from "@/entities/user/api/useProfile"

// Импортируем интерфейс, если он лежит в другом файле
// import { CartResponse } from "../model/types";

export const CartButton = ({ className }: { className?: string }) => {
  const { data: profile } = useProfile()
  // Явно указываем тип данных из хука, чтобы TS помогал с автокомплитом
  const { data, isError } = useGetCart()
  const toggleAuthWindow = useAuthWindowStore((s) => s.toggle)

  const isAuth = !!profile && !isError

  // 1. Используем cart_items вместо items
  // 2. Считаем сумму всех quantity, чтобы получить реальное кол-во товаров
  const count =
    data?.cart_items?.reduce((acc, item) => acc + item.quantity, 0) || 0

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (!isAuth) {
      e.preventDefault()
      toggleAuthWindow()
    }
  }

  return (
    <Link
      href="/cart"
      onClick={handleClick}
      className="relative p-1 text-slate-700 hover:text-brand-main hover:bg-white/50 rounded-xl transition-all"
    >
      <Icon.CART className={`w-6 h-6 ${className}`} />

      {isAuth && count > 0 && (
        <span className="absolute top-0 right-0 inline-flex items-center justify-center min-w-[16px] h-4 px-1 text-[10px] font-bold text-white bg-brand-main rounded-full border-2 border-white animate-in zoom-in">
          {count > 99 ? "99+" : count}
        </span>
      )}
    </Link>
  )
}
