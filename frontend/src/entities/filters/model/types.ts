export interface BaseProperties {
  name: string
  slug: string
}

export interface FilterItem<T = any> extends BaseProperties {
  children: T[]
}

/**
 * Интерфейс отдельной категории.
 * Используется рекурсивно для поля children.
 */
export interface Category extends FilterItem<Category> {}

/**
 * Интерфейс ответа от API с пагинацией.
 */
export interface CategoriesResponse extends Omit<Category, "slug"> {
  prefix?: string
  next?: string
  previous?: string
}

export interface ProductType extends FilterItem<ProductType> {}

export interface ProductTypesResponse extends Omit<ProductType, "slug"> {
  prefix?: string
  next?: string
  previous?: string
}

// Вложенные свойства meta ответа
interface MetaProperiesNested<T> extends Omit<FilterItem<T>, "slug"> {
  prefix: string
  next?: number
  previous?: number
}

// Интерфейс для Brand
interface Brand extends BaseProperties {
  description: string
  image: string | null
}

// Интерфейс для Shop
interface Shop extends BaseProperties {
  created_at: string
  owner: number
  description: string
  image: string | null
}

// Интерфейс для AttributeValues
interface AttributeValues extends Omit<BaseProperties, "slug"> {
  id: number
}

// Интерфейс для Attributes со вложенными AttributeValues
interface Attributes extends FilterItem<MetaProperiesNested<AttributeValues>> {
  is_active: boolean
}

export interface MetaResponse {
  brands?: MetaProperiesNested<Brand>
  shops?: MetaProperiesNested<Shop>
  attributes?: MetaProperiesNested<Attributes>
}

export interface FilterPropertiesResponse {
  categories?: CategoriesResponse
  product_types?: ProductTypesResponse
  meta?: MetaResponse
}

// export type FilterProperty =
//   FilterPropertiesResponse[keyof FilterPropertiesResponse]

// Определяем тип одной записи (кортежа)
// export type FilterEntry = [
//   keyof FilterPropertiesResponse,
//   FilterPropertiesResponse[keyof FilterPropertiesResponse],
// ]
