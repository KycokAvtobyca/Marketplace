"use client"

import React from "react"
import clsx from "clsx"
import { FilterGroupList } from "@/features/Filters"

interface FilterSidebarProps {
  className?: string
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({ className }) => {
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
        <button className="text-xs font-semibold text-brand-main hover:opacity-70 transition-all uppercase tracking-wider">
          Сбросить
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar pr-1">
        {/* Удаляем лишние gap, чтобы аккордеоны стояли плотно */}
        <div className="flex flex-col">
          <FilterGroupList isSidebar={true} />
        </div>
      </div>

      {/* Кнопка "Показать" — современный стиль без бордеров */}
      <div className="mt-4 pt-2 shrink-0">
        <button className="w-full bg-brand-main text-white py-3 rounded-xl font-bold text-sm shadow-lg shadow-brand-main/20 hover:brightness-110 active:scale-[0.97] transition-all">
          Показать результаты
        </button>
      </div>
    </aside>
  )
}
