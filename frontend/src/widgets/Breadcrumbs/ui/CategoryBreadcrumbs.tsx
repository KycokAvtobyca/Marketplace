"use client"

import { useMemo } from "react"
import { useSearchParams } from "next/navigation"
import { useCategories } from "@/entities/filters/api/hooks"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"
import { Category } from "@/entities/filters/model/types"

const findCategoryBySlug = (
  categories: Category[] = [],
  slug?: string,
): Category | null => {
  if (!slug) return null

  for (const category of categories) {
    if (category.slug === slug) {
      return category
    }

    const childMatch = findCategoryBySlug(category.children, slug)
    if (childMatch) {
      return childMatch
    }
  }

  return null
}

export const CategoryBreadcrumbs = () => {
  const searchParams = useSearchParams()
  const slug =
    searchParams?.get("categories")?.trim() ||
    searchParams?.get("category")?.trim() ||
    ""
  const search = searchParams?.get("search")?.trim() || ""
  const hasFilters = Array.from(searchParams?.keys() || []).some((key) =>
    [
      "brands",
      "shops",
      "product_types",
      "price_min",
      "price_max",
      "material",
      "razmer",
    ].includes(key),
  )

  const { data } = useCategories({ cursor: "" })

  const category = useMemo(
    () => findCategoryBySlug(data?.data?.categories?.children || [], slug),
    [data, slug],
  )

  if (!slug && !search && !hasFilters) {
    return null
  }

  const crumbs = []

  if (slug) {
    crumbs.push({
      label: category?.name || decodeURIComponent(slug),
      href: search || hasFilters ? `/catalog?categories=${slug}` : undefined,
    })
  }

  if (search) {
    crumbs.push({
      label: `Поиск: ${search}`,
      href: hasFilters ? `/catalog?search=${encodeURIComponent(search)}` : undefined,
    })
  }

  if (hasFilters) {
    crumbs.push({ label: "Фильтры" })
  }

  return (
    <Breadcrumbs crumbs={crumbs} />
  )
}
