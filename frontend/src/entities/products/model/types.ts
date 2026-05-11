export interface Product {
  id: number
  name: string
  price: string // Приходит строкой (Decimal)
  old_price: string
  image: string
  rating: number | null
  stock: number
}

export interface ProductCatalogResponse {
  next: string | null
  previous: string | null
  results: Product[]
}
