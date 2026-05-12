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

  const { data } = useCategories({ cursor: "" })
  const categories = data?.data?.categories?.children || []

  const category = useMemo(
    () => findCategoryBySlug(categories, slug),
    [categories, slug],
  )

  if (!slug) {
    return null
  }

  return (
    <Breadcrumbs
      crumbs={[
        {
          label: category?.name || decodeURIComponent(slug),
        },
      ]}
    />
  )
}
