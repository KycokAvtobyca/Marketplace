import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export interface CreateShopPayload {
  name: string
  description?: string
}

export const useCreateShop = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: CreateShopPayload) => {
      const { data } = await api.post(ROUTES.SHOP_CREATE, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-shop"] })
      queryClient.invalidateQueries({ queryKey: ["profile"] })
      // Автологин в Django admin через корневой endpoint бэкенда
      const apiBase = process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") || "http://127.0.0.1:8001"
      window.location.href = `${apiBase}/admin-login/`
    },
  })
}