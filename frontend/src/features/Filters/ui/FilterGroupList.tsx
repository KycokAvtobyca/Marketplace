"use client"

import React, { ReactNode, useState } from "react"
import { useFilterProperties } from "@/entities/filters"
import {
  FilterPropertiesResponse,
  MetaResponse,
} from "@/entities/filters/model/types"
import { FilterItem } from "@/entities/filters"
import { FilterPropertiesData } from "@/shared/config/routesInterfaces"
import { FilterList } from "./FilterList"

interface FilterGroupListProps {
  isSidebar?: boolean
}

type FilterGroup = {
  name: string
  prefix?: string
  next?: string | number | null
  children?: unknown[]
}

const mergeGroup = (
  previousGroup: FilterGroup | undefined,
  nextGroup: FilterGroup | undefined,
) => {
  if (!nextGroup) return previousGroup
  return {
    ...nextGroup,
    children: [...(previousGroup?.children || []), ...(nextGroup.children || [])],
  }
}

const mergeResponseByPrefix = (
  previousData: FilterPropertiesResponse,
  nextData: FilterPropertiesResponse,
  prefix: string,
): FilterPropertiesResponse => {
  if (prefix === nextData.product_types?.prefix) {
    return {
      ...nextData,
      product_types: mergeGroup(
        previousData.product_types,
        nextData.product_types,
      ) as typeof nextData.product_types,
      categories: previousData.categories || nextData.categories,
      meta: previousData.meta || nextData.meta,
    }
  }

  if (prefix === nextData.categories?.prefix) {
    return {
      ...nextData,
      categories: mergeGroup(
        previousData.categories,
        nextData.categories,
      ) as typeof nextData.categories,
      product_types: previousData.product_types || nextData.product_types,
      meta: previousData.meta || nextData.meta,
    }
  }

  const metaKey = Object.entries(nextData.meta || {}).find(
    ([, value]) => value?.prefix === prefix,
  )?.[0] as keyof MetaResponse | undefined

  if (metaKey) {
    return {
      ...nextData,
      product_types: previousData.product_types || nextData.product_types,
      categories: previousData.categories || nextData.categories,
      meta: {
        ...nextData.meta,
        ...previousData.meta,
        [metaKey]: mergeGroup(
          previousData.meta?.[metaKey],
          nextData.meta?.[metaKey],
        ) as NonNullable<MetaResponse[typeof metaKey]>,
      },
    }
  }

  return nextData
}

export const FilterGroupList: React.FC<FilterGroupListProps> = ({
  isSidebar = false,
}) => {
  const [startPages, setStartPages] = useState<FilterPropertiesData[]>([])
  const [loadingPrefix, setLoadingPrefix] = useState<string | null>(null)
  const [mergedResponse, setMergedResponse] =
    useState<FilterPropertiesResponse | null>(null)
  const pendingLoadRef = React.useRef<FilterPropertiesData | null>(null)
  const lastAppliedAtRef = React.useRef(0)

  const {
    data: response,
    isLoading,
    isError,
    dataUpdatedAt,
  } = useFilterProperties({ startPages })

  React.useEffect(() => {
    const nextData = response?.data
    if (!nextData || dataUpdatedAt === lastAppliedAtRef.current) return

    lastAppliedAtRef.current = dataUpdatedAt
    const pendingLoad = pendingLoadRef.current

    setMergedResponse((prev) => {
      if (!prev || !pendingLoad) {
        return nextData
      }

      return mergeResponseByPrefix(prev, nextData, pendingLoad.prefix)
    })
    pendingLoadRef.current = null
    setLoadingPrefix(null)
  }, [response, dataUpdatedAt])

  if (isLoading && !mergedResponse) return <div>Загрузка фильтров...</div>
  if (isError || !mergedResponse) {
    return <div>Ошибка при загрузке фильтров.</div>
  }

  const { meta, ...lists } = mergedResponse

  const handleLoadMore = (prefix?: string, next?: string | number | null) => {
    if (!prefix || next === undefined || next === null) return
    const pageNumber = String(next)
    pendingLoadRef.current = { prefix, pageNumber }
    setLoadingPrefix(prefix)
    setStartPages((prev) => [
      ...prev.filter((item) => item.prefix !== prefix),
      { prefix, pageNumber },
    ])
  }

  const groupingComponents = (
    lists: Omit<FilterPropertiesResponse, "meta"> | MetaResponse,
  ): ReactNode => {
    return Object.entries(lists).map(([objectKey, value]) => {
      if (!value?.children || value.children.length === 0) return null

      const groupWrapper: FilterItem = {
        name: value.name,
        slug: objectKey,
        children: value.children as FilterItem["children"],
      }
      const hasNextPage =
        Boolean(value.prefix) && value.next !== undefined && value.next !== null

      return (
        <div key={objectKey}>
          <FilterList
            object={groupWrapper}
            title={value.name}
            hasParent={false}
            nestingLevel={0}
            isSidebar={isSidebar}
            loadMore={
              hasNextPage
                ? {
                    isLoading: isLoading && loadingPrefix === value.prefix,
                    onClick: () => handleLoadMore(value.prefix, value.next),
                  }
                : undefined
            }
          />
        </div>
      )
    })
  }

  return (
    <>
      {lists && groupingComponents(lists)}
      {meta && groupingComponents(meta)}
    </>
  )
}
