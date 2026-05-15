"use client"

import React, { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import clsx from "clsx"
import { FilterGroupList } from "@/features/Filters"
import { useFilterModalMenuStore } from "@/entities/filters"
import { getApiParams } from "@/shared/lib/getApiParams/getApiParams"
import { PriceRangeFilter } from "@/features/Filters/ui/PriceRangeFilter"

interface FilterSidebarProps {
  className?: string
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({ className }) => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { selectedFilters, setAppliedQueryString } = useFilterModalMenuStore()
  const resetFilters = useFilterModalMenuStore((s) => s.resetFilters)
  const [priceMin, setPriceMin] = useState("")
  const [priceMax, setPriceMax] = useState("")
  const hasFilters = selectedFilters.length > 0 || !!priceMin || !!priceMax

  const handleResetFilters = () => {
    resetFilters()
    setPriceMin("")
    setPriceMax("")
    setAppliedQueryString("")

    const preservedSearch = searchParams?.get("search")?.trim()
    const params = new URLSearchParams()
    if (preservedSearch) params.set("search", preservedSearch)

    const searchUrl = params.toString()
    router.replace(
      searchUrl
        ? `${window.location.pathname}?${searchUrl}`
        : window.location.pathname,
    )
  }

  const handleApply = () => {
    const params = getApiParams(selectedFilters)
    const searchParamsForUrl = new URLSearchParams()

    const preservedSearch = searchParams?.get("search")?.trim()
    if (preservedSearch) {
      searchParamsForUrl.set("search", preservedSearch)
    }

    Object.entries(params).forEach(([key, values]) => {
      if (Array.isArray(values)) {
        values.forEach((val) => searchParamsForUrl.append(key, val))
      }
    })

    if (priceMin) {
      searchParamsForUrl.set("price_min", priceMin)
    }
    if (priceMax) {
      searchParamsForUrl.set("price_max", priceMax)
    }

    const queryString = searchParamsForUrl.toString()

    setAppliedQueryString(queryString)
    router.push(
      queryString
        ? `${window.location.pathname}?${queryString}`
        : window.location.pathname,
    )
  }

  return (
    <aside
      className={clsx(
        "sticky top-20 hidden max-h-[calc(100vh-6rem)] w-60 shrink-0 flex-col self-start overflow-hidden min-[800px]:flex xl:w-64",
        "bg-white border border-slate-100 rounded-2xl p-4 shadow-sm",
        className,
      )}
    >
      <div className="flex items-center justify-between mb-5 px-1 shrink-0">
        <h2 className="text-xl font-bold tracking-tight text-slate-800">
          Фильтры
        </h2>
        <button
          onClick={handleResetFilters}
          disabled={!hasFilters}
          className={clsx(
            "text-xs font-semibold text-brand-main transition-all uppercase tracking-wider",
            hasFilters
              ? "hover:opacity-70 cursor-pointer"
              : "opacity-30 cursor-default",
          )}
        >
          Сбросить
        </button>
      </div>

      <div className="min-w-0 overflow-y-auto pr-1">
        {/* Удаляем лишние gap, чтобы аккордеоны стояли плотно */}
        <div className="flex flex-col">
          <PriceRangeFilter
            onChange={(min, max) => {
              setPriceMin(min)
              setPriceMax(max)
            }}
          />
          <FilterGroupList isSidebar={true} />
        </div>
      </div>

      {/* Кнопка "Показать" — современный стиль без бордеров */}
      <div className="mt-4 pt-2 shrink-0">
        <button
          onClick={handleApply}
          className="w-full bg-brand-main text-white py-3 rounded-xl font-bold text-sm shadow-lg shadow-brand-main/20 hover:brightness-110 active:scale-[0.97] transition-all"
        >
          Показать результаты
        </button>
      </div>
    </aside>
  )
}
