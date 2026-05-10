"use client"

import { useFilterProperties } from "@/entities/filters"
import {
  FilterEntry,
  FilterPropertiesResponse,
} from "@/entities/filters/api/interfaces"

import { CheckBox } from "@/shared/ui/CheckBox"
import { useEffect, useState } from "react"
import React from "react"
import { FilterItem, FilterList } from "./FilterList"

export const FilterGroupList: React.FC = () => {
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

  return (
    <>
      {Object.entries(lists).map(([objectKey, value], index) => {
        if (!value?.results || value.results.length === 0) return
        // console.log("value", value, "\n", "value results", value.results)

        // Создаем групповой объект
        const groupWrapper: FilterItem = {
          name: value.name,
          slug: objectKey, // Используем ключ как slug для стилей
          children: value.results, // Передаем результаты как детей
        }

        return (
          <FilterList
            key={objectKey}
            object={groupWrapper}
            title={value.name}
            hasParent={false}
            nestingLevel={0}
          />
        )

        // return (
        //   <React.Fragment key={objectKey}>
        //     {value.results.map((obj) => (
        //       <FilterList key={obj?.slug} object={obj} isLast={isLast} />
        //     ))}
        //   </React.Fragment>
        // )
      })}
    </>
  )
}
