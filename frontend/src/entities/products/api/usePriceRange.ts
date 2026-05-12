import { useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export interface PriceRangeResponse {
  min: number
  max: number
}

export const usePriceRange = () => {
  return useQuery<PriceRangeResponse>({
    queryKey: ["priceRange"],
    queryFn: async () => {
      const { data } = await api.get<PriceRangeResponse>(ROUTES.FILTER_PRICE)
      return data
    },
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })
}
