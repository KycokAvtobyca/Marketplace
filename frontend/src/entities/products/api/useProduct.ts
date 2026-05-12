import { useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export interface ProductImage {
  id: number
  image: string
  is_main: boolean
}

export interface ProductVariant {
  id: number
  sku: string
  final_price: number
  has_discount: boolean
  discount_pct: number
  stock: number
  is_active: boolean
  is_main: boolean
  attribute_values: Array<{ id: number; name: string }>
  images: ProductImage[]
}

export interface ProductDetail {
  id: number
  name: string
  slug: string
  description: string
  views: number
  category: {
    name: string
    slug: string
    children: any[]
  } | null
  brand: { name: string; slug: string } | null
  shop: { name: string; slug: string; owner: number } | null
  product_type: { name: string; slug: string } | null
  tags: Array<{ name: string; slug: string }>
  attributes: Array<any>
  variants: ProductVariant[]
}

export const useProduct = (id: number) => {
  return useQuery<ProductDetail>({
    queryKey: ["product", id],
    queryFn: async () => {
      const { data } = await api.get(
        `${ROUTES.PRODUCTS.RETRIEVE(id)}?variants_flag=true`
      )
      return data
    },
    enabled: !!id,
    retry: false,
  })
}
