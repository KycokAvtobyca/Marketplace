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
  final_price: number | string
  old_price: number | string
  has_discount: boolean
  discount_pct: number | string
  stock: number
  is_active: boolean
  is_main: boolean
  attribute_values: Array<{
    id: number
    name: string
    attribute?: string
    attribute_id?: number
  }>
  images: ProductImage[]
}

interface ProductTreeNode {
  name: string
  slug: string
  children: ProductTreeNode[]
}

interface ProductAttributeValue {
  id: number
  name: string
  slug?: string
}

interface ProductAttribute {
  id: number
  name: string
  slug?: string
  values?: ProductAttributeValue[]
  attribute_values?: ProductAttributeValue[]
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
    children: ProductTreeNode[]
  } | null
  brand: { name: string; slug: string } | null
  shop: { name: string; slug: string; owner: number } | null
  product_type: { name: string; slug: string } | null
  tags: Array<{ name: string; slug: string }>
  attributes: ProductAttribute[]
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
