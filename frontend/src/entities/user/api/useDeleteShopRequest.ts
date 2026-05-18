import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export const useDeleteShopRequest = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post(ROUTES.SHOP_DELETE_REQUEST)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-shop"] })
      queryClient.invalidateQueries({ queryKey: ["profile"] })
    },
  })
}
