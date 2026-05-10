export interface BaseProperties {
  name?: string
  slug?: string
}

/**
 * Интерфейс отдельной категории.
 * Используется рекурсивно для поля children.
 */
export interface Category extends BaseProperties {
  children: Category[]
}

/**
 * Интерфейс ответа от API с пагинацией.
 */
export interface CategoriesResponse {
  name?: string
  prefix?: string
  next?: string
  previous?: string
  results: Category[]
}

/**
 * Интерфейс отдельной категории.
 * Используется рекурсивно для поля children.
 */
export interface ProductType extends BaseProperties {
  name: string
  slug: string
}

export interface ProductTypesResponse {
  name?: string
  prefix?: string
  next?: string
  previous?: string
  results: ProductType[]
}

// Вложенные свойства meta ответа
interface MetaProperiesNested<T> {
  name?: string
  prefix: string
  next?: number
  previous?: number
  results?: T[]
}

// Интерфейс для Brand
interface BrandResult extends BaseProperties {
  description: string
  image: string | null
}

// Интерфейс для Shop
interface ShopResult extends BaseProperties {
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
interface AttributesResult extends BaseProperties {
  is_active: boolean
  values: MetaProperiesNested<AttributeValuesResult>
}

export interface MetaResponse {
  brands?: MetaProperiesNested<BrandResult>
  shops?: MetaProperiesNested<ShopResult>
  attributes?: MetaProperiesNested<AttributesResult>
}

export interface FilterPropertiesResponse {
  categories: CategoriesResponse
  product_types: ProductTypesResponse
  meta: MetaResponse
}

// export type FilterProperty =
//   FilterPropertiesResponse[keyof FilterPropertiesResponse]

// Определяем тип одной записи (кортежа)
export type FilterEntry = [
  keyof FilterPropertiesResponse,
  FilterPropertiesResponse[keyof FilterPropertiesResponse],
]
