import React, { useState } from "react"
import clsx from "clsx"
import { Product } from "../model/types"
import { useAddToCart } from "@/entities/cart/api/useCart"
import { useAddToFavorites } from "@/entities/favorites/api/useFavorites"

interface ProductCardProps {
  product: Product
  className?: string
}

export const ProductCardSkeleton = () => {
  return (
    // Заменяем h-[420px] на h-full и min-h
    <div className="flex flex-col bg-white rounded-2xl border border-slate-100 overflow-hidden min-h-[400px] h-full animate-pulse">
      {/* Используем aspect-ratio вместо жесткой высоты h-[240px] */}
      <div className="aspect-[4/5] w-full bg-slate-200" />
      <div className="flex flex-col grow p-3 sm:p-4 gap-3">
        <div className="h-6 w-20 bg-slate-200 rounded-md" />
        <div className="space-y-2">
          <div className="h-4 w-full bg-slate-200 rounded-md" />
          <div className="h-4 w-2/3 bg-slate-200 rounded-md" />
        </div>
        <div className="mt-auto flex justify-between mb-3">
          <div className="h-4 w-12 bg-slate-200 rounded-md" />
          <div className="h-4 w-16 bg-slate-200 rounded-md" />
        </div>
        <div className="h-10 w-full bg-slate-200 rounded-xl" />
      </div>
    </div>
  )
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  className,
}) => {
  const { mutate: addToCart, isPending: isAddingToCart } = useAddToCart()
  const { mutate: addToFavorites, isPending: isAddingToFavorites } =
    useAddToFavorites()
  const [cartMessage, setCartMessage] = useState<string | null>(null)
  const [favoritesMessage, setFavoritesMessage] = useState<string | null>(null)

  const currentPrice = Number(product.price)
  const oldPrice = product.old_price ? Number(product.old_price) : null

  const discountPercent =
    oldPrice && oldPrice > currentPrice
      ? Math.round(((oldPrice - currentPrice) / oldPrice) * 100)
      : 0

  const handleAddToCart = () => {
    if (!product.id) return

    addToCart(
      { product_variant_id: product.id, quantity: 1 },
      {
        onSuccess: (result) => {
          if (result.success) {
            setCartMessage("Добавлено в корзину")
            setTimeout(() => setCartMessage(null), 2000)
          } else {
            setCartMessage(
              result.error?.data?.detail || "Ошибка при добавлении",
            )
            setTimeout(() => setCartMessage(null), 3000)
          }
        },
        onError: () => {
          setCartMessage("Ошибка подключения")
          setTimeout(() => setCartMessage(null), 3000)
        },
      },
    )
  }

  const handleAddToFavorites = () => {
    if (!product.id) return

    addToFavorites(
      { product_variant_id: product.id },
      {
        onSuccess: (result) => {
          if (result.success) {
            setFavoritesMessage("Добавлено в избранное")
            setTimeout(() => setFavoritesMessage(null), 2000)
          } else {
            setFavoritesMessage(
              result.error?.data?.detail || "Ошибка при добавлении",
            )
            setTimeout(() => setFavoritesMessage(null), 3000)
          }
        },
        onError: () => {
          setFavoritesMessage("Ошибка подключения")
          setTimeout(() => setFavoritesMessage(null), 3000)
        },
      },
    )
  }

  return (
    <article
      className={clsx(
        "flex flex-col bg-white rounded-2xl border border-slate-100 overflow-hidden hover:shadow-xl transition-all duration-300 h-full min-h-[400px] relative group",
        className,
      )}
    >
      {/* 1. Изображение с сохранением пропорций */}
      <div className="relative aspect-[4/5] w-full bg-slate-50 shrink-0 overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
        />
        {discountPercent > 0 && (
          <div className="absolute top-2 left-2 sm:top-3 sm:left-3 bg-red-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded-md z-10">
            -{discountPercent}%
          </div>
        )}
        <button
          onClick={handleAddToFavorites}
          disabled={isAddingToFavorites}
          className="absolute top-2 right-2 sm:top-3 sm:right-3 p-2 bg-white rounded-full shadow-md hover:bg-slate-50 transition-colors z-10 disabled:opacity-50"
          title="Добавить в избранное"
        >
          <svg
            className="w-5 h-5 text-red-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            />
          </svg>
        </button>
      </div>

      {/* Контентная часть */}
      <div className="flex flex-col grow p-3 sm:p-4">
        {/* 2. Цены - чуть уменьшил шрифт для мобилок */}
        <div className="flex flex-wrap items-baseline gap-x-2 mb-1 sm:mb-2">
          <span className="text-lg sm:text-xl font-bold text-slate-900 whitespace-nowrap">
            {currentPrice.toLocaleString("ru-RU")} ₽
          </span>
          {oldPrice && oldPrice > currentPrice && (
            <span className="text-xs sm:text-sm text-slate-400 line-through whitespace-nowrap">
              {oldPrice.toLocaleString("ru-RU")} ₽
            </span>
          )}
        </div>

        {/* Название товара - line-clamp-2 важен, чтобы не раздувать карточку */}
        <h3 className="text-xs sm:text-sm text-slate-700 line-clamp-2 leading-snug mb-3 hover:text-brand-main transition-colors cursor-pointer italic sm:not-italic">
          {product.name}
        </h3>

        {/* 3. Инфо-блок (Рейтинг и остаток) */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 mt-auto mb-4">
          <div className="flex items-center gap-1 text-yellow-400">
            <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="text-[11px] sm:text-xs font-medium text-slate-600">
              {product.rating ?? "0.0"}
            </span>
          </div>
          <span className="text-[10px] sm:text-xs text-slate-500">
            Остаток:{" "}
            <span className="font-medium text-slate-700">{product.stock}</span>
          </span>
        </div>

        {/* Сообщение об ошибке/успехе */}
        {cartMessage && (
          <div className="mb-2 text-xs text-center py-1 px-2 bg-slate-100 rounded-lg text-slate-700">
            {cartMessage}
          </div>
        )}

        {/* 4. Кнопка корзины */}
        <button
          onClick={handleAddToCart}
          disabled={isAddingToCart || product.stock === 0}
          className={clsx(
            "w-full py-2 sm:py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 active:scale-95 shrink-0",
            isAddingToCart
              ? "bg-slate-200 text-slate-600 cursor-wait"
              : product.stock === 0
                ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                : "bg-brand-main/10 text-brand-main hover:bg-brand-main hover:text-white",
          )}
        >
          {isAddingToCart
            ? "Добавляю..."
            : product.stock === 0
              ? "Нет в наличии"
              : "В корзину"}
        </button>
      </div>
    </article>
  )
}
