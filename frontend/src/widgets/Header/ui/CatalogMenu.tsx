"use client"

import { useEffect, useState } from "react"
import { createPortal } from "react-dom"
import { useCategories } from "@/entities/filters/api/hooks"
import { Category } from "@/entities/filters/model/types"
import { useMountTransition } from "@/shared/lib/hooks"
import { Icon } from "@/shared/ui/Icons"
import clsx from "clsx"
import Link from "next/link"

interface CatalogMenuProps {
  buttonClassName?: string
  compact?: boolean
}

const CategoryTreeItem = ({
  category,
  depth = 0,
  onSelect,
}: {
  category: Category
  depth?: number
  onSelect: (slug: string) => void
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const hasChildren =
    Array.isArray(category.children) && category.children.length > 0

  return (
    <div>
      <div className="flex items-center gap-0">
        {hasChildren && (
          <button
            type="button"
            onClick={() => setIsOpen(!isOpen)}
            className="p-2 rounded-lg hover:bg-brand-main/5 transition flex-shrink-0"
          >
            <div
              className={clsx(
                "w-4 h-4 text-brand-main transition-transform",
                isOpen && "rotate-90",
              )}
            >
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          </button>
        )}
        {!hasChildren && <div className="p-2 flex-shrink-0" />}

        <Link
          href={`/catalog?categories=${encodeURIComponent(category.slug)}`}
          onClick={() => onSelect(category.slug)}
          className={clsx(
            "flex-1 px-4 py-3 rounded-lg text-sm font-medium transition-colors",
            depth === 0
              ? "text-slate-900 hover:bg-brand-main/10"
              : "text-slate-700 hover:bg-brand-main/5",
          )}
        >
          <div className="flex items-center justify-between gap-3">
            <span>{category.name}</span>
            {hasChildren && (
              <span className="text-xs text-slate-400 bg-slate-100 rounded-full px-2 py-1">
                {category.children.length}
              </span>
            )}
          </div>
        </Link>
      </div>

      {hasChildren && isOpen && (
        <div className="ml-2 border-l-2 border-brand-main/10 pl-0 space-y-1">
          {category.children.map((child) => (
            <CategoryTreeItem
              key={child.slug}
              category={child}
              depth={depth + 1}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export const CatalogMenu: React.FC<CatalogMenuProps> = ({
  buttonClassName,
  compact = false,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const { shouldRender, isVisible } = useMountTransition({
    isOpen,
    transitionDuration: 220,
  })

  useEffect(() => {
    setMounted(true)
  }, [])

  const toggle = () => setIsOpen((current) => !current)
  const close = () => setIsOpen(false)
  const result = useCategories({ cursor: "" })
  const categories = result.data?.data?.categories?.children || []

  if (!mounted) {
    return (
      <button
        type="button"
        onClick={toggle}
        className={clsx(
          "rounded-2xl px-4 py-2 text-sm font-semibold transition",
          "bg-brand-main/10 text-brand-main border border-brand-main/20 hover:bg-brand-main/15",
          buttonClassName,
        )}
      >
        Каталог
      </button>
    )
  }

  const portalRoot = document.getElementById("modals")
  return (
    <>
      <button
        type="button"
        onClick={toggle}
        className={clsx(
          "rounded-2xl px-4 py-2 text-sm font-semibold transition",
          "bg-brand-main/10 text-brand-main border border-brand-main/20 hover:bg-brand-main/15",
          compact && "px-3 text-[11px]",
          buttonClassName,
        )}
      >
        Каталог
      </button>

      {shouldRender &&
        portalRoot &&
        createPortal(
          <div
            className={clsx(
              "fixed inset-x-0 top-[5rem] z-50 flex justify-center px-4 sm:px-6 transition-opacity duration-220",
              isVisible ? "opacity-100" : "opacity-0 pointer-events-none",
            )}
            onClick={close}
          >
            <div
              className="relative mx-auto w-full max-w-[1000px] overflow-hidden rounded-[1rem]"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="w-full bg-white shadow-2xl shadow-brand-main/10 rounded-[1rem] border border-brand-main/10">
                {/* Заголовок */}
                <div className="flex items-center justify-between border-b border-brand-main/10 px-6 py-5">
                  <h3 className="text-lg font-bold text-slate-900">
                    Категории товаров
                  </h3>
                  <button
                    type="button"
                    onClick={close}
                    className="rounded-full border border-slate-200 bg-slate-50 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
                    aria-label="Закрыть каталог"
                  >
                    <Icon.CLOSE />
                  </button>
                </div>

                {/* Контент */}
                <div className="max-h-[calc(100vh-8rem)] overflow-y-auto px-2 py-4">
                  {result.isLoading && (
                    <div className="px-4 py-8 text-center text-slate-500">
                      Загрузка категорий...
                    </div>
                  )}
                  {result.isError && (
                    <div className="px-4 py-8 text-center text-rose-600">
                      Не удалось загрузить категории.
                    </div>
                  )}
                  {!result.isLoading &&
                    !result.isError &&
                    categories.length === 0 && (
                      <div className="px-4 py-8 text-center text-slate-500">
                        Категории пока недоступны.
                      </div>
                    )}
                  {!result.isLoading && categories.length > 0 && (
                    <div className="space-y-1">
                      {categories.map((category) => (
                        <CategoryTreeItem
                          key={category.slug}
                          category={category}
                          depth={0}
                          onSelect={close}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>,
          portalRoot,
        )}
    </>
  )
}
