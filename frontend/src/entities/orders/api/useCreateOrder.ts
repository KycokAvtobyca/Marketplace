import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"
import { Order } from "./useOrders"

export interface CreateOrderPayload {
  delivery_type: "PICKUP" | "COURIER"
  branch?: string | null
  address?: string | null
  address_data?: Record<string, unknown>
  name: string
  phone_number: string
  date_time_deliver?: string | null
  description?: string
}

export const useCreateOrder = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: CreateOrderPayload): Promise<Order> => {
      const { data } = await api.post(ROUTES.ORDERS.CREATE, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] })
      queryClient.invalidateQueries({ queryKey: ["cart"] })
    },
  })
}
