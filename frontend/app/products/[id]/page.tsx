"use client"

import React, { useState, useCallback, useEffect } from "react"
import { useProduct } from "@/entities/products/api/useProduct"
import { useAddToCart } from "@/entities/cart/api/useCart"
import { useQueryClient } from "@tanstack/react-query"
import { useParams, useRouter } from "next/navigation"
import Head from "next/head"
import { useProfile } from "@/entities/user/api/useProfile"
import { useAuthWindowStore } from "@/entities/authWindow"

export default function ProductPage() {
  const params = useParams()
  const router = useRouter()
  const id = Number(params?.id)
  const { data: product, isLoading } = useProduct(id)
  const { mutate: addToCart, isPending: isAdding } = useAddToCart()
  const queryClient = useQueryClient()
  const { data: profile } = useProfile()
  const toggleAuthWindow = useAuthWindowStore((s) => s.toggle)

  const [selectedVariant, setSelectedVariant] = useState<number | null>(null)
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [touchStart, setTouchStart] = useState<number | null>(null)
  const [quantity, setQuantity] = useState(1)

  // Находим основной вариант по умолчанию
  const mainVariant = product?.variants.find((v) => v.is_main) || product?.variants[0]
  const activeVariant =
    product?.variants.find((v) => v.id === selectedVariant) || mainVariant

  // Сбрасываем индекс изображения при смене варианта
  useEffect(() => {
    setCurrentImageIndex(0)
  }, [selectedVariant])

  const allImages = activeVariant?.images || []
  const currentImage = allImages[currentImageIndex]

  const handlePrevImage = useCallback(() => {
    setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : allImages.length - 1))
  }, [allImages.length])

  const handleNextImage = useCallback(() => {
    setCurrentImageIndex((prev) => (prev < allImages.length - 1 ? prev + 1 : 0))
  }, [allImages.length])

  // Свайп
  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStart(e.touches[0].clientX)
  }

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStart === null) return
    const diff = touchStart - e.changedTouches[0].clientX
    if (Math.abs(diff) > 50) {
      if (diff > 0) handleNextImage()
      else handlePrevImage()
    }
    setTouchStart(null)
  }

  // Свайп мышью для ПК
  const handleMouseDown = (e: React.MouseEvent) => {
    setTouchStart(e.clientX)
  }

  const handleMouseUp = (e: React.MouseEvent) => {
    if (touchStart === null) return
    const diff = touchStart - e.clientX
    if (Math.abs(diff) > 50) {
      if (diff > 0) handleNextImage()
      else handlePrevImage()
    }
    setTouchStart(null)
  }

  const handleAddToCart = () => {
    if (!activeVariant) return
    if (!profile) {
      toggleAuthWindow()
      return
    }
    addToCart(
      { product_variant_id: activeVariant.id, quantity },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ["cart"] })
        },
      }
    )
  }

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto p-12 text-center animate-pulse">
        Загрузка товара...
      </div>
    )
  }

  if (!product) {
    return (
      <div className="max-w-5xl mx-auto p-12 text-center">
        <h2 className="text-xl font-bold">Товар не найден</h2>
        <button
          onClick={() => router.push("/")}
          className="mt-4 px-6 py-2 bg-brand-main text-white rounded-xl"
        >
          На главную
        </button>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>{product.name} — Floppi</title>
        <meta name="description" content={product.description?.slice(0, 160) || `${product.name} в маркетплейсе Floppi`} />
      </Head>
      <main className="max-w-5xl mx-auto p-4 sm:p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Галерея */}
        <div className="space-y-4">
          <div
            className="relative aspect-[3/4] bg-slate-100 rounded-2xl overflow-hidden select-none"
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
          >
            {currentImage ? (
              <img
                src={currentImage.image}
                alt={product.name}
                className="w-full h-full object-contain"
                draggable={false}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-400">
                Нет изображения
              </div>
            )}

            {/* Кнопки навигации */}
            {allImages.length > 1 && (
              <>
                <button
                  onClick={handlePrevImage}
                  className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 backdrop-blur rounded-full flex items-center justify-center shadow-lg hover:bg-white transition-colors"
                >
                  ◀
                </button>
                <button
                  onClick={handleNextImage}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 backdrop-blur rounded-full flex items-center justify-center shadow-lg hover:bg-white transition-colors"
                >
                  ▶
                </button>
                <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
                  {allImages.map((_, idx) => (
                    <button
                      key={idx}
                      onClick={() => setCurrentImageIndex(idx)}
                      className={`w-2 h-2 rounded-full transition-colors ${
                        idx === currentImageIndex
                          ? "bg-brand-main"
                          : "bg-white/60"
                      }`}
                    />
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Миниатюры */}
          {allImages.length > 1 && (
            <div className="flex gap-2 overflow-auto pb-1">
              {allImages.map((img, idx) => (
                <button
                  key={img.id}
                  onClick={() => setCurrentImageIndex(idx)}
                  className={`shrink-0 w-16 h-16 rounded-xl overflow-hidden border-2 transition-colors ${
                    idx === currentImageIndex
                      ? "border-brand-main"
                      : "border-transparent"
                  }`}
                >
                <img
                  src={img.image}
                  alt=""
                  className="w-full h-full object-contain"
                />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Информация о товаре */}
        <div className="space-y-6">
          <div>
            {product.brand && (
              <p className="text-sm text-slate-500 mb-1">{product.brand.name}</p>
            )}
            <h1 className="text-2xl sm:text-3xl font-bold">{product.name}</h1>
            {product.category && (
              <p className="text-sm text-slate-400 mt-1">
                {product.category.name}
              </p>
            )}
          </div>

          {/* Цена */}
          {activeVariant && (
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-black text-brand-main">
                {Number(activeVariant.final_price).toLocaleString("ru-RU")} ₽
              </span>
              {activeVariant.has_discount && (
                <span className="text-lg text-slate-400 line-through">
                  {Number(
                    activeVariant.final_price /
                      (1 - (activeVariant.discount_pct || 0) / 100)
                  ).toLocaleString("ru-RU")}{" "}
                  ₽
                </span>
              )}
            </div>
          )}

          {/* Варианты */}
          {product.variants.length > 1 && (
            <div>
              <p className="text-sm font-medium text-slate-600 mb-2">Варианты:</p>
              <div className="flex flex-wrap gap-2">
                {product.variants.map((variant) => (
                  <button
                    key={variant.id}
                    onClick={() => setSelectedVariant(variant.id)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all ${
                      variant.id === activeVariant?.id
                        ? "bg-brand-main text-white border-brand-main"
                        : "bg-white text-slate-700 border-slate-200 hover:border-brand-main"
                    }`}
                  >
                    {variant.attribute_values.map((av) => av.name).join(", ") ||
                      variant.sku}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Характеристики варианта */}
          {activeVariant && activeVariant.attribute_values.length > 0 && (
            <div className="space-y-1">
              <p className="text-sm font-medium text-slate-600">Характеристики:</p>
              {activeVariant.attribute_values.map((av) => (
                <div
                  key={av.id}
                  className="flex justify-between text-sm py-1 border-b border-slate-50"
                >
                  <span className="text-slate-500">{av.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* Наличие */}
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                activeVariant && activeVariant.stock > 0
                  ? "bg-green-500"
                  : "bg-red-500"
              }`}
            />
            <span className="text-sm">
              {activeVariant && activeVariant.stock > 0
                ? `В наличии: ${activeVariant.stock} шт.`
                : "Нет в наличии"}
            </span>
          </div>

          {/* Количество и кнопка */}
          <div className="flex gap-3">
            <div className="flex items-center border border-slate-200 rounded-xl">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="px-3 py-2 text-lg font-medium hover:bg-slate-50"
              >
                −
              </button>
              <span className="px-3 py-2 text-sm font-bold min-w-[40px] text-center">
                {quantity}
              </span>
              <button
                onClick={() =>
                  setQuantity(
                    Math.min(activeVariant ? activeVariant.stock : 1, quantity + 1)
                  )
                }
                className="px-3 py-2 text-lg font-medium hover:bg-slate-50"
              >
                +
              </button>
            </div>
            <button
              onClick={handleAddToCart}
              disabled={isAdding || !activeVariant || activeVariant.stock <= 0}
              className="flex-1 py-3 bg-brand-main text-white rounded-xl font-bold hover:brightness-110 shadow-lg shadow-brand-main/20 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {isAdding ? "Добавление..." : "В корзину"}
            </button>
          </div>

          {/* Описание */}
          {product.description && (
            <div>
              <p className="text-sm font-medium text-slate-600 mb-1">Описание:</p>
              <p className="text-sm text-slate-500 whitespace-pre-line">
                {product.description}
              </p>
            </div>
          )}

          {/* Магазин */}
          {product.shop && (
            <div className="p-3 bg-slate-50 rounded-xl">
              <p className="text-xs text-slate-400">Продавец</p>
              <p className="font-medium">{product.shop.name}</p>
            </div>
          )}
        </div>
      </div>
    </main>
    </>
  )
}
