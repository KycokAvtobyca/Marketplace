"use client"

import React, { useState } from "react"
import { usePriceRange } from "@/entities/products/api/usePriceRange"

interface PriceRangeFilterProps {
  onChange: (minPrice: string, maxPrice: string) => void
}

export const PriceRangeFilter: React.FC<PriceRangeFilterProps> = ({
  onChange,
}) => {
  const { data: range, isLoading } = usePriceRange()
  const [minPrice, setMinPrice] = useState("")
  const [maxPrice, setMaxPrice] = useState("")

  const handleMinChange = (value: string) => {
    const digitsOnly = value.replace(/[^0-9]/g, "")
    setMinPrice(digitsOnly)
    onChange(digitsOnly, maxPrice)
  }

  const handleMaxChange = (value: string) => {
    const digitsOnly = value.replace(/[^0-9]/g, "")
    setMaxPrice(digitsOnly)
    onChange(minPrice, digitsOnly)
  }

  return (
    <div className="mb-4 p-4 rounded-2xl bg-slate-50 border border-slate-200">
      <div className="mb-3 text-sm font-semibold text-slate-700">
        Диапазон цены
      </div>
      <div className="grid grid-cols-2 gap-3">
        <label className="block text-[11px] text-slate-500">
          От
          <input
            value={minPrice}
            onChange={(e) => handleMinChange(e.target.value)}
            type="text"
            placeholder={isLoading ? "..." : String(range?.min ?? "")}
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-brand-main focus:ring-1 focus:ring-brand-main"
          />
        </label>
        <label className="block text-[11px] text-slate-500">
          До
          <input
            value={maxPrice}
            onChange={(e) => handleMaxChange(e.target.value)}
            type="text"
            placeholder={isLoading ? "..." : String(range?.max ?? "")}
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-brand-main focus:ring-1 focus:ring-brand-main"
          />
        </label>
      </div>
    </div>
  )
}
