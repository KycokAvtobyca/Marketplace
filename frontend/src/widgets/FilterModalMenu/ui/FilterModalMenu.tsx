"use client"

import React, { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useFilterModalMenuStore } from "@/entities/filters"
import { HamburgerButton } from "@/shared/ui/HamburgerButton"
import { ModalMenu } from "@/shared/ui/ModalMenu"
import { FilterGroupList } from "@/features/Filters/"
import { PriceRangeFilter } from "@/features/Filters/ui/PriceRangeFilter"
import clsx from "clsx"
import { getApiParams } from "@/shared/lib/getApiParams/getApiParams"

interface FilterModalMenuProps {
  classNameHamburgerButton?: string
  classNameModalMenu?: string
}

export const FilterModalMenu: React.FC<FilterModalMenuProps> = ({
  classNameHamburgerButton,
  classNameModalMenu,
}) => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const {
    isFilterModalMenu,
    toggleFilterModalMenu,
    resetFilters,
    selectedFilters,
    setAppliedQueryString,
  } = useFilterModalMenuStore()

  const [priceMin, setPriceMin] = useState("")
  const [priceMax, setPriceMax] = useState("")

  const handleResetFilters = () => {
    resetFilters()
    setPriceMin("")
    setPriceMax("")
    setAppliedQueryString("")

    const preservedSearch = searchParams.get("search")?.trim()
    const params = new URLSearchParams()
    if (preservedSearch) params.set("search", preservedSearch)

    const searchUrl = params.toString()
    router.replace(
      searchUrl
        ? `${window.location.pathname}?${searchUrl}`
        : window.location.pathname,
    )
  }

  const hasFilters = selectedFilters.length > 0 || priceMin || priceMax

  const handleApply = () => {
    const params = getApiParams(selectedFilters)
    const searchParamsForUrl = new URLSearchParams()

    const preservedSearch = searchParams.get("search")?.trim()
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
    toggleFilterModalMenu()
  }

  return (
    <>
      <HamburgerButton
        className={classNameHamburgerButton}
        onClick={toggleFilterModalMenu}
      />
      <ModalMenu
        className={classNameModalMenu}
        isOpen={isFilterModalMenu}
        toggleModalMenu={toggleFilterModalMenu}
      >
        <div className="mx-auto w-full max-w-5xl px-2">
          {/* ВЕСЬ КОНТЕНТ ДОЛЖЕН БЫТЬ ВНУТРИ ЭТОГО DIV */}
          <div className="flex flex-col">
            {/* 1. Шапка (Фиксированная) */}
            <div className="flex items-center justify-between mb-6 px-1 shrink-0">
              <h2 className="text-2xl font-bold text-slate-800">Фильтры</h2>
              <button
                onClick={handleResetFilters}
                className={clsx(
                  "text-sm font-bold text-brand-main transition-all uppercase tracking-tight",
                  hasFilters ? "opacity-100" : "opacity-0 pointer-events-none",
                )}
              >
                Сбросить все
              </button>
            </div>

            {/* 2. Список (С прокруткой) */}
            <div className="overflow-y-auto pr-2 custom-scrollbar">
              <PriceRangeFilter
                onChange={(min, max) => {
                  setPriceMin(min)
                  setPriceMax(max)
                }}
              />
              <FilterGroupList />
            </div>

            {/* 3. Футер с кнопкой (Фиксированный снизу) */}
            <div className="mt-6 shrink-0">
              <button
                onClick={handleApply}
                className="w-full bg-brand-main text-white py-4 rounded-2xl font-bold shadow-lg active:scale-[0.98] transition-transform"
              >
                Показать результаты
              </button>
            </div>
          </div>
        </div>
      </ModalMenu>
    </>
  )
}
