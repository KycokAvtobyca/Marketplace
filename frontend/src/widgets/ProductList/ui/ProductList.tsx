"use client"

import { useMemo } from "react"
import { useSearchParams } from "next/navigation"
import { ProductCard, ProductCardSkeleton } from "@/entities/products"
import { ProductCatalogResponse } from "@/entities/products/model/types"
import { useCatalogProducts } from "@/entities/products"
import { useFilterModalMenuStore } from "@/entities/filters"
import clsx from "clsx"

export const ProductList = () => {
  // Достаем примененную строку фильтров
  const appliedQueryString = useFilterModalMenuStore(
    (s) => s.appliedQueryString,
  )
  const searchParams = useSearchParams()
  const search = searchParams?.get("search")?.trim() || ""
  const category =
    searchParams?.get("categories")?.trim() ||
    searchParams?.get("category")?.trim() ||
    ""

  const queryString = useMemo(() => {
    const params = new URLSearchParams(appliedQueryString)
    if (search) {
      params.set("search", search)
    } else {
      params.delete("search")
    }

    // Добавляем категорию из URL
    if (category) {
      params.set("categories", category)
    } else {
      params.delete("categories")
    }

    return params.toString()
  }, [appliedQueryString, search, category])

  // Используем ваш хук.
  // Как только appliedQueryString или search изменятся, React Query сделает новый запрос.
  const { data, isLoading, isError } = useCatalogProducts(queryString)

  // const { data, isLoading, isError } = useQuery({
  //   queryKey: ["products"],
  //   queryFn: async () => {
  //     const response = await api.get<ProductCatalogResponse>(
  //       ROUTES.PRODUCTSCATALOG,
  //     )
  //     return response.data
  //   },
  // })

  // Сетка (Grid) общая для всех состояний, чтобы верстка не "прыгала"
  const gridClassName = clsx(
    "grid",
    "grid-cols-2", // На маленьких экранах 2 колонки
    "sm:grid-cols-3", // От 640px - 3 колонки
    "md:grid-cols-3", // Учитываем сайдбар: на средних экранах лучше оставить 3
    "lg:grid-cols-4", // На десктопе в контейнере max-w-5xl с сайдбаром 4 колонки - оптимально
    "gap-3 sm:gap-4 md:gap-5",
  )

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

  const products = data?.results || []

  console.log("Полученные товары:", data, products)

  if (products.length === 0) {
    return (
      <div className="py-20 text-center text-slate-500">
        Товары не найдены. Попробуйте сбросить фильтры.
      </div>
    )
  }

  // 3. Успешный результат
  return (
    <div className={gridClassName}>
      {products.map((product) => (
        // Проверь, что в объекте точно есть name, price и image!
        // Если в консоли они называются api_price, передавай их так:
        // <ProductCard key={product.id} product={{...product, price: product.api_price}} />
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}
