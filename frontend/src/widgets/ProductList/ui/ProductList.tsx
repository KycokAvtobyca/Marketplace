"use client"

import { ProductCard, ProductCardSkeleton } from "@/entities/products"
import { ProductCatalogResponse } from "@/entities/products/model/types"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"
import { useQuery } from "@tanstack/react-query"

export const ProductList = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const response = await api.get<ProductCatalogResponse>(
        ROUTES.PRODUCTSCATALOG,
      )
      return response.data
    },
  })

  // Сетка (Grid) общая для всех состояний, чтобы верстка не "прыгала"
  const gridClassName =
    "grid grid-cols-2 sm:grid-cols-3 min-[800px]:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6"

  // 1. Состояние загрузки (показываем 6 скелетонов)
  if (isLoading) {
    return (
      <div className={gridClassName}>
        {[...Array(6)].map((_, index) => (
          <ProductCardSkeleton key={index} />
        ))}
      </div>
    )
  }

  // 2. Состояние ошибки
  if (isError) {
    return (
      <div className="py-10 text-center text-red-500">
        Не удалось загрузить товары. Попробуйте обновить страницу.
      </div>
    )
  }

  // 3. Успешный результат
  return (
    <div className={gridClassName}>
      {/* Используем ?. чтобы быть уверенными, что results существует */}
      {data?.results.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}
