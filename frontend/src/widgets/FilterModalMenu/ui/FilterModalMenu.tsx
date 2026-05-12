"use client"

import { useFilterModalMenuStore } from "@/entities/filters"
import { HamburgerButton } from "@/shared/ui/HamburgerButton"
import { ModalMenu } from "@/shared/ui/ModalMenu"
import { FilterGroupList } from "@/features/Filters/"
import clsx from "clsx"
import { api } from "@/shared/api"
import { getApiParams } from "@/shared/lib/getApiParams/getApiParams"
import { ROUTES } from "@/shared/config"

interface FilterModalMenuProps {
  classNameHamburgerButton?: string
  classNameModalMenu?: string
}

export const FilterModalMenu: React.FC<FilterModalMenuProps> = ({
  classNameHamburgerButton,
  classNameModalMenu,
}) => {
  const {
    isFilterModalMenu,
    toggleFilterModalMenu,
    resetFilters,
    selectedFilters,
    setAppliedQueryString,
  } = useFilterModalMenuStore()

  const hasFilters = selectedFilters.length > 0

  const handleApply = () => {
    const params = getApiParams(selectedFilters)
    const searchParams = new URLSearchParams()

    Object.entries(params).forEach(([key, values]) => {
      if (Array.isArray(values)) {
        values.forEach((val) => searchParams.append(key, val))
      }
    })

    setAppliedQueryString(searchParams.toString())
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
        {/* ВЕСЬ КОНТЕНТ ДОЛЖЕН БЫТЬ ВНУТРИ ЭТОГО DIV */}
        <div className="flex flex-col h-full max-h-[90vh]">
          {/* 1. Шапка (Фиксированная) */}
          <div className="flex items-center justify-between mb-6 px-1 shrink-0">
            <h2 className="text-2xl font-bold text-slate-800">Фильтры</h2>
            <button
              onClick={resetFilters}
              className={clsx(
                "text-sm font-bold text-brand-main transition-all uppercase tracking-tight",
                hasFilters ? "opacity-100" : "opacity-0 pointer-events-none",
              )}
            >
              Сбросить все
            </button>
          </div>

          {/* 2. Список (С прокруткой) */}
          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
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
      </ModalMenu>
    </>
  )
}
