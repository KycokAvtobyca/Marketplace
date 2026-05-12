import { useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export interface ShopData {
  name: string
  slug: string
  description: string
  is_active: boolean
  image: string | null
  data_time_create: string
}

export const useMyShop = () => {
  return useQuery<ShopData>({
    queryKey: ["my-shop"],
    queryFn: async () => {
      const { data } = await api.get(ROUTES.MY_SHOP)
      return data
    },
    retry: false,
    refetchOnWindowFocus: false,
  })
}
