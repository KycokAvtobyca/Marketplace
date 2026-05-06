import { DefaultErrorResponse } from "@/shared/api"

/**
 * Интерфейс отдельной категории.
 * Используется рекурсивно для поля children.
 */
interface Category {
  name: string
  slug: string
  children: Category[]
}

/**
 * Интерфейс ответа от API с пагинацией.
 */
export interface CategoriesResponse {
  next?: string
  previous?: string
  results: Category[]
}

/**
 * Интерфейс отдельной категории.
 * Используется рекурсивно для поля children.
 */
interface ProductType {
  name: string
  slug: string
}

export interface ProductTypesResponse {
  next?: string
  previous?: string
  results: ProductType[]
}

// Вложенные свойства meta ответа
interface MetaProperiesNested<T> {
  prefix: string
  next?: number
  previous?: number
  results?: T[]
}

// Базовые поля, которые есть и у брендов, и у магазинов
interface BaseFilterResult {
  slug: string
  name: string
}

// Интерфейс для Brand
interface BrandResult extends BaseFilterResult {
  description: string
  image: string | null
}

// Интерфейс для Shop
interface ShopResult extends BaseFilterResult {
  created_at: string
  owner: number
  description: string
  image: string | null
}

// Интерфейс для AttributeValues
interface AttributeValuesResult {
  id: number
  value: string
}

// Интерфейс для Attributes со вложенными AttributeValues
interface AttributesResult extends BaseFilterResult {
  is_active: boolean
  values: MetaProperiesNested<AttributeValuesResult>
}

export interface MetaResponse {
  brands?: MetaProperiesNested<BrandResult>
  shops?: MetaProperiesNested<ShopResult>
  attributes?: MetaProperiesNested<AttributesResult>
}
