"use client"

import { useMemo, useRef, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { ProductCard, ProductCardSkeleton } from "@/entities/products"
import { useCatalogProducts } from "@/entities/products"
import { useFilterModalMenuStore } from "@/entities/filters"
import { Popover } from "@/shared/ui/Popover"
import clsx from "clsx"

const SORT_OPTIONS = [
  { value: "new", label: "Сначала новые" },
  { value: "price_asc", label: "Сначала дешевле" },
  { value: "price_desc", label: "Сначала дороже" },
  { value: "popular", label: "Популярные" },
  { value: "views_desc", label: "По просмотрам" },
  { value: "rating_desc", label: "По рейтингу" },
] as const

type SortValue = (typeof SORT_OPTIONS)[number]["value"]

const isSortValue = (value: string | null): value is SortValue =>
  SORT_OPTIONS.some((option) => option.value === value)

export const ProductList = () => {
  const appliedQueryString = useFilterModalMenuStore(
    (s) => s.appliedQueryString,
  )
  const router = useRouter()
  const searchParams = useSearchParams()
  const search = searchParams?.get("search")?.trim() || ""
  const sortFromUrl = searchParams?.get("sort") || null
  const sort: SortValue = isSortValue(sortFromUrl) ? sortFromUrl : "new"
  const [isSortOpen, setIsSortOpen] = useState(false)
  const sortButtonRef = useRef<HTMLButtonElement>(null)
  const sortLabel =
    SORT_OPTIONS.find((option) => option.value === sort)?.label ||
    SORT_OPTIONS[0].label

  const queryString = useMemo(() => {
    const params = new URLSearchParams(appliedQueryString)
    const urlCategories = searchParams?.getAll("categories") || []
    const urlCategoryAlias = searchParams?.get("category")?.trim()
    const categoriesFromUrl = [
      ...urlCategories.map((value) => value?.trim()).filter(Boolean),
      ...(urlCategoryAlias ? [urlCategoryAlias] : []),
    ]

    if (search) {
      params.set("search", search)
    } else {
      params.delete("search")
    }

    if (categoriesFromUrl.length > 0) {
      params.delete("categories")
      categoriesFromUrl.forEach((cat) => params.append("categories", cat))
    } else {
      params.delete("categories")
    }

    params.set("sort", sort)
    return params.toString()
  }, [appliedQueryString, search, searchParams, sort])

  const handleSortChange = (value: SortValue) => {
    const params = new URLSearchParams(searchParams?.toString())
    if (value === "new") {
      params.delete("sort")
    } else {
      params.set("sort", value)
    }

    const nextQuery = params.toString()
    router.replace(
      nextQuery
        ? `${window.location.pathname}?${nextQuery}`
        : window.location.pathname,
      { scroll: false },
    )
    setIsSortOpen(false)
  }

  const { data, isLoading, isError } = useCatalogProducts(queryString)

  const gridClassName = clsx(
    "grid",
    "grid-cols-1",
    "min-[380px]:grid-cols-2",
    "sm:grid-cols-3",
    "lg:grid-cols-4",
    "gap-3 sm:gap-4 md:gap-5",
  )

  const sortControl = (
    <div className="mb-4 flex flex-col gap-2 min-[480px]:items-end">
      <button
        ref={sortButtonRef}
        type="button"
        onClick={() => setIsSortOpen((current) => !current)}
        className="inline-flex min-h-10 w-full flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-brand-main hover:text-brand-main min-[480px]:w-auto min-[480px]:justify-start"
        aria-haspopup="menu"
        aria-expanded={isSortOpen}
      >
        <span>Сортировка</span>
        <span className="text-brand-main">{sortLabel}</span>
        <span aria-hidden="true">▾</span>
      </button>

      <Popover
        anchorRef={sortButtonRef}
        isOpen={isSortOpen}
        onClose={() => setIsSortOpen(false)}
        needTriangle={false}
        padding={12}
      >
        <div
          className="flex w-[calc(100vw-2rem)] min-[360px]:w-64 flex-col gap-1"
          role="menu"
        >
          {SORT_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              role="menuitemradio"
              aria-checked={option.value === sort}
              onClick={() => handleSortChange(option.value)}
              className={clsx(
                "w-full rounded-lg px-3 py-2 text-left text-sm transition",
                option.value === sort
                  ? "bg-brand-main text-white"
                  : "text-slate-700 hover:bg-slate-100",
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      </Popover>
    </div>
  )

  if (isLoading) {
    return (
      <>
        {sortControl}
        <div className={gridClassName}>
          {[...Array(6)].map((_, index) => (
            <ProductCardSkeleton key={index} />
          ))}
        </div>
      </>
    )
  }

  if (isError) {
    return (
      <>
        {sortControl}
        <div className="py-10 text-center text-red-500">
          Не удалось загрузить товары. Попробуйте обновить страницу.
        </div>
      </>
    )
  }

  const products = data?.results || []

  if (products.length === 0) {
    return (
      <>
        {sortControl}
        <div className="py-20 text-center text-slate-500">
          Товары не найдены. Попробуйте сбросить фильтры.
        </div>
      </>
    )
  }

  return (
    <>
      {sortControl}
      <div className={gridClassName}>
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </>
  )
}
