"use client"

import { useFilterProperties } from "@/entities/filters"
import {
  FilterPropertiesResponse,
  MetaResponse,
} from "@/entities/filters/model/types"

import { ReactNode, useEffect, useState } from "react"
import React from "react"
import { FilterList } from "./FilterList"
import { FilterItem } from "@/entities/filters"

interface FilterGroupListProps {
  isSidebar?: boolean
}

export const FilterGroupList: React.FC<FilterGroupListProps> = ({
  isSidebar = false,
}) => {
  const [filterVars, setFilterVars] = useState({ startPages: [] })

  const {
    data: response,
    isLoading,
    isError,
    error,
  } = useFilterProperties(filterVars)

  useEffect(() => {
    if (response?.data) {
      console.log("Данные получены:", response?.data)
    }
  }, [response])

  if (isLoading) return <div>Загрузка фильтров...</div>
  if (isError || !response) return <div>Ошибка при загрузке фильтров.</div>

  const { meta, ...lists } = response.data || {}

  // console.log(lists, meta)

  const groupingComponents = (
    lists: Omit<FilterPropertiesResponse, "meta"> | MetaResponse,
  ): ReactNode => {
    return Object.entries(lists).map(([objectKey, value], index) => {
      if (!value?.children || value.children.length === 0) return

      // Создаем групповой объект
      const groupWrapper: FilterItem = {
        name: value.name,
        slug: objectKey, // Используем ключ как slug для стилей
        children: value.children, // Передаем результаты как детей
      }

      return (
        <FilterList
          key={objectKey}
          object={groupWrapper}
          title={value.name}
          hasParent={false}
          nestingLevel={0}
          isSidebar={isSidebar}
        />
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
