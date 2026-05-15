import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export interface OrderItem {
  id: number
  product_variant: number
  product_variant_name: string
  product_variant_sku: string
  product_variant_image: string | null
  quantity: number
  price_per_item: string
  discounted_price_per_item: string
  total_price: number
}

export interface Order {
  id: number
  status: string
  status_display: string
  delivery_type: string
  delivery_type_display: string
  branch: string | null
  branch_display: string | null
  address: string | null
  address_data: Record<string, unknown> | null
  name: string
  phone_number: string
  description: string
  date_time_deliver: string
  total_cost_without_sales: string
  total_cost: string
  order_items: OrderItem[]
  date_time_create: string
}

export const useOrders = () => {
  return useQuery<Order[]>({
    queryKey: ["orders"],
    queryFn: async () => {
      const { data } = await api.get(ROUTES.ORDERS.ROOT)
      return data.results || data
    },
    staleTime: 1000 * 60 * 5, // 5 минут
    refetchOnWindowFocus: true,
    retry: 1,
  })
}

export const useCancelOrder = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number): Promise<Order> => {
      const { data } = await api.post(ROUTES.ORDERS.CANCEL(id))
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] })
    },
  })
}
