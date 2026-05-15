"use client"

import React, { useState } from "react"
import clsx from "clsx"
import { Product } from "../model/types"
import { useAddToCart } from "@/entities/cart/api/useCart"
import { useProfile } from "@/entities/user/api/useProfile"
import {
  useAddToFavorites,
  useGetFavorites,
  useRemoveFromFavorites,
} from "@/entities/favorites/api/useFavorites"
import { useQueryClient } from "@tanstack/react-query"
import { useAuthWindowStore } from "@/entities/authWindow/"
import { Icon } from "@/shared/ui/Icons"
import Link from "next/link"

export const ProductCardSkeleton = () => {
  return (
    <div className="flex flex-col bg-white rounded-xl sm:rounded-2xl border border-slate-100 overflow-hidden h-full animate-pulse">
      <div className="aspect-[4/5] w-full bg-slate-100" />
      <div className="flex flex-col flex-1 p-3 sm:p-4">
        <div className="h-5 w-2/3 bg-slate-100 rounded mb-2" />
        <div className="h-3 w-full bg-slate-50 rounded mb-1" />
        <div className="h-3 w-1/2 bg-slate-50 rounded mb-4" />
        <div className="mt-auto flex justify-between items-center mb-3">
          <div className="h-3 w-8 bg-slate-50 rounded" />
          <div className="h-3 w-16 bg-slate-50 rounded" />
        </div>
        <div className="h-9 w-full bg-slate-100 rounded-lg" />
      </div>
    </div>
  )
}

interface ProductCardProps {
  product: Product
  className?: string
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  className,
}) => {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState<{
    text: string
    type: "cart" | "fav" | "error"
  } | null>(null)

  const toggleAuthWindow = useAuthWindowStore((s) => s.toggle)

  const { data: profile, isLoading: isProfileLoading } = useProfile()
  const userIsAuthenticated = !!profile

  const { mutate: addToCart, isPending: isAddingToCart } = useAddToCart()
  const { mutate: addToFavorites, isPending: isAddingToFavorites } =
    useAddToFavorites()
  const { mutate: removeFromFavorites, isPending: isRemovingFromFavorites } =
    useRemoveFromFavorites()

  const { data: favoritesData } = useGetFavorites()
  const isFavorite = favoritesData?.favorite_items?.some(
    (item) => item.product_variant.id === product.variant_id,
  )

  const currentPrice = Number(product.price)
  const oldPrice = product.old_price ? Number(product.old_price) : null
  const discountPercent =
    oldPrice && oldPrice > currentPrice
      ? Math.round(((oldPrice - currentPrice) / oldPrice) * 100)
      : 0

  const formatPrice = (value: number) =>
    value.toLocaleString("ru-RU", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })

  const firstError = (value?: string | string[]) =>
    Array.isArray(value) ? value[0] : value

  const handleActionWithAuth = (action: () => void) => {
    if (isProfileLoading) return
    if (!userIsAuthenticated) {
      return toggleAuthWindow()
    }
    action()
  }

  const handleAddToCart = () => {
    handleActionWithAuth(() => {
      if (!product.variant_id) return

      addToCart(
        { product_variant_id: product.variant_id, quantity: 1 },
        {
          onSuccess: (result) => {
            if (!result.success) {
              setMessage({
                text:
                  firstError(result.error?.data.error) ||
                  firstError(result.error?.data.detail) ||
                  "Не удалось добавить товар в корзину",
                type: "error",
              })
              setTimeout(() => setMessage(null), 3000)
              return
            }

            setMessage({ text: "Добавлено в корзину", type: "cart" })
            queryClient.invalidateQueries({ queryKey: ["cart"] })
            setTimeout(() => setMessage(null), 2000)
          },
        },
      )
    })
  }

  const handleToggleFavorite = () => {
    handleActionWithAuth(() => {
      if (isFavorite) {
        removeFromFavorites(product.variant_id || product.id, {
          onSuccess: () => {
            setMessage({ text: "Удалено", type: "fav" })
            queryClient.invalidateQueries({ queryKey: ["favorites"] })
            setTimeout(() => setMessage(null), 2000)
          },
        })
      } else {
        addToFavorites(
          { product_variant_id: product.variant_id || product.id },
          {
            onSuccess: () => {
              setMessage({ text: "В избранном", type: "fav" })
              queryClient.invalidateQueries({ queryKey: ["favorites"] })
              setTimeout(() => setMessage(null), 2000)
            },
          },
        )
      }
    })
  }

  return (
    <article
      className={clsx(
        "group relative flex min-w-0 flex-col w-full h-full bg-white rounded-xl sm:rounded-2xl border border-slate-100",
        "hover:shadow-xl hover:shadow-slate-200/50 transition-all duration-300 overflow-hidden",
        className,
      )}
    >
      {/* Изображение */}
      <Link
        href={`/products/${product.id}`}
        className="relative aspect-[4/5] w-full overflow-hidden bg-slate-50 shrink-0 block"
      >
        <img
          src={product.image}
          alt={product.name}
          className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-110"
        />

        {discountPercent > 0 && (
          <div className="absolute top-2 left-2 z-10 bg-red-500 text-white text-[10px] sm:text-xs font-bold px-1.5 py-0.5 rounded-md shadow-sm">
            -{discountPercent}%
          </div>
        )}
      </Link>

      {/* Кнопка избранного */}
      <button
        onClick={handleToggleFavorite}
        disabled={isAddingToFavorites || isRemovingFromFavorites}
        className={clsx(
          "absolute top-2 right-2 p-1 backdrop-blur-sm rounded-full transition-all shadow-sm z-10",
          isFavorite
            ? "bg-red-500 text-white"
            : "bg-white/80 text-slate-400 hover:text-red-500 hover:bg-white",
          (isAddingToFavorites || isRemovingFromFavorites) &&
            "opacity-50 cursor-not-allowed",
        )}
      >
        <Icon.HEARTGRAY className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
      </button>

      {/* Контент */}
      <div className="flex min-w-0 flex-1 flex-col p-2.5 sm:p-4">
        <div className="mb-1 flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5">
          <span className="text-sm font-bold text-slate-900 min-[380px]:text-base sm:text-lg">
            {formatPrice(currentPrice)} ₽
          </span>
          {oldPrice && oldPrice > currentPrice && (
            <span className="text-[10px] text-slate-400 line-through sm:text-xs">
              {formatPrice(oldPrice)} ₽
            </span>
          )}
        </div>

        <Link href={`/products/${product.id}`}>
          <h3 className="text-[11px] sm:text-sm text-slate-700 line-clamp-2 leading-tight mb-1 min-h-[2.5em] group-hover:text-brand-main transition-colors cursor-pointer">
            {product.name}
          </h3>
        </Link>

        {product.sku && (
          <p className="text-[10px] sm:text-xs text-slate-500 mb-1">
            Артикул: {product.sku}
          </p>
        )}

        <div className="mt-auto mb-3 flex flex-col items-start gap-2 pt-2 min-[380px]:flex-row min-[380px]:items-center min-[380px]:justify-between">
          <div className="flex items-center gap-0.5 text-yellow-400 shrink-0">
            <svg className="w-3 h-3 fill-current" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="text-[10px] sm:text-xs font-semibold text-slate-500">
              {product.rating ? Number(product.rating).toFixed(1) : "—"}
            </span>
          </div>
          <span className="w-full text-left text-[9px] font-medium uppercase tracking-tighter text-slate-400 min-[380px]:w-auto min-[380px]:truncate min-[380px]:text-right sm:text-[11px]">
            {product.stock && product.stock > 0
              ? `Остаток: ${product.stock}`
              : "Нет в наличии"}
          </span>
        </div>

        <button
          onClick={handleAddToCart}
          disabled={isAddingToCart || !product.stock || product.stock <= 0}
          className={clsx(
            "w-full py-2 sm:py-2.5 rounded-lg sm:rounded-xl text-[10px] sm:text-xs font-bold uppercase tracking-[0.08em] sm:tracking-widest transition-all active:scale-[0.97]",
            !product.stock || product.stock <= 0
              ? "bg-slate-100 text-slate-400 cursor-not-allowed"
              : isAddingToCart
                ? "bg-slate-200 text-slate-500 cursor-wait"
                : "bg-brand-main text-white shadow-md shadow-brand-main/20 hover:brightness-110",
          )}
        >
          {isAddingToCart
            ? "..."
            : !product.stock || product.stock <= 0
              ? "Пусто"
              : "В корзину"}
        </button>
      </div>

      {/* Уведомление */}
      {message && (
        <div
          className={clsx(
            "absolute inset-x-2 bottom-16 text-white text-[10px] py-1.5 px-2 rounded-lg text-center backdrop-blur-sm animate-in fade-in slide-in-from-bottom-2 z-20",
            message.type === "error" ? "bg-red-600/95" : "bg-slate-900/90",
          )}
        >
          {message.text}
        </div>
      )}
    </article>
  )
}
