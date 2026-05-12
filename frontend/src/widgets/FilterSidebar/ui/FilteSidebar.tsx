"use client"

import React from "react"
import clsx from "clsx"
import { FilterGroupList } from "@/features/Filters"
import { useFilterModalMenuStore } from "@/entities/filters"
import { api } from "@/shared/api"
import { getApiParams } from "@/shared/lib/getApiParams/getApiParams"
import { ROUTES } from "@/shared/config"

interface FilterSidebarProps {
  className?: string
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({ className }) => {
  const { selectedFilters, setAppliedQueryString } = useFilterModalMenuStore()
  const resetFilters = useFilterModalMenuStore((s) => s.resetFilters)
  const hasFilters = useFilterModalMenuStore(
    (s) => s.selectedFilters.length > 0,
  )

  const handleApply = () => {
    const params = getApiParams(selectedFilters)

    // Превращаем объект { categories: ['obuv'], brands: ['nike'] }
    // в строку "categories=obuv&brands=nike"
    const searchParams = new URLSearchParams()

    Object.entries(params).forEach(([key, values]) => {
      if (Array.isArray(values)) {
        values.forEach((val) => searchParams.append(key, val))
      }
    })

    const queryString = searchParams.toString()

    // Сохраняем в стор -> это триггернет обновление ProductList
    setAppliedQueryString(queryString)
  }

  return (
    <aside
      className={clsx(
        "flex flex-col w-64 shrink-0 hidden min-[800px]:flex",
        "bg-white border border-slate-100 rounded-2xl p-4 shadow-sm", // Небольшая тень вместо бордера
        "sticky top-4 max-h-[calc(100vh-32px)]",
        className,
      )}
    >
      <div className="flex items-center justify-between mb-5 px-1 shrink-0">
        <h2 className="text-xl font-bold tracking-tight text-slate-800">
          Фильтры
        </h2>
        <button
          onClick={resetFilters}
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

      <div className="flex-1 overflow-y-auto custom-scrollbar pr-1 min-w-0">
        {/* Удаляем лишние gap, чтобы аккордеоны стояли плотно */}
        <div className="flex flex-col">
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
