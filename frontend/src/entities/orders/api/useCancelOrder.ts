import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export const useCancelOrder = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (orderId: number) => {
      const { data } = await api.post(ROUTES.ORDERS.CANCEL(orderId))
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] })
    },
  })
}
