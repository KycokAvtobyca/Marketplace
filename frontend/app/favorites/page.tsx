"use client"

import React from "react"
import { useGetFavorites } from "@/entities/favorites/api/useFavorites"
import {
  ProductCard,
  ProductCardSkeleton,
} from "@/entities/products/ui/ProductCard"
import { Icon } from "@/shared/ui/Icons/Icon"
import Link from "next/link"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"

export const FavoritesPage = () => {
  const { data, isLoading } = useGetFavorites()

  if (isLoading) {
    return (
      <main className="max-w-5xl mx-auto p-4 sm:p-6">
        <Breadcrumbs crumbs={[{ label: "Избранное" }]} />
        <h1 className="text-2xl font-bold mb-6">Избранное</h1>
        <div className="grid grid-cols-1 gap-4 min-[380px]:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <ProductCardSkeleton key={i} />
          ))}
        </div>
      </main>
    )
  }

  const favoriteItems = data?.favorite_items || []

  if (favoriteItems.length === 0) {
    return (
      <main className="mx-auto flex max-w-5xl flex-col items-center gap-4 px-4 py-12 text-center sm:p-12">
        <div className="w-full text-left">
          <Breadcrumbs crumbs={[{ label: "Избранное" }]} />
        </div>
        <div className="p-6 bg-slate-50 rounded-full text-slate-300">
          <Icon.HEARTBRAND className="w-16 h-16" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">
          В избранном пока пусто
        </h2>
        <p className="text-slate-500 max-w-xs">
          Добавляйте товары, которые вам понравились, чтобы не потерять их.
        </p>
        <Link
          href="/"
          className="mt-4 px-6 py-3 bg-brand-main text-white rounded-xl font-bold uppercase text-xs tracking-widest hover:brightness-110 transition-all"
        >
          Перейти в каталог
        </Link>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-5xl p-4 animate-in fade-in duration-500 sm:p-6">
      <Breadcrumbs crumbs={[{ label: "Избранное" }]} />
      <div className="mb-8 flex flex-col gap-2 min-[420px]:flex-row min-[420px]:items-center min-[420px]:justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Избранное</h1>
        <span className="text-sm text-slate-500">
          {favoriteItems.length} товаров
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 min-[380px]:grid-cols-2 sm:gap-6 md:grid-cols-3 lg:grid-cols-4">
        {favoriteItems.map((item) => (
          <ProductCard
            key={item.id}
            // Маппим данные из product_variant в формат, который ждет карточка
            product={
              {
                id: item.product_variant.product_id,
                name: item.product_variant.product_name,
                price: String(item.product_variant.final_price),
                old_price: String(item.product_variant.price),
                image: item.product_variant.image,
                stock: item.product_variant.stock,
                rating: 5, // Или другое поле из твоей модели
                variant_id: item.product_variant.id,
              }
            }
          />
        ))}
      </div>
    </main>
  )
}

export default function Page() {
  return <FavoritesPage />
}
