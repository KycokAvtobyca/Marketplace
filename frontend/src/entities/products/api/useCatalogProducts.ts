import { useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ProductCatalogResponse } from "../model/types"
import { ROUTES } from "@/shared/config"

// @/entities/products/api/index.ts
export const useCatalogProducts = (queryString: string) => {
  return useQuery({
    queryKey: ["products", queryString],
    queryFn: async () => {
      // Используем ROUTES.PRODUCTSCATALOG вместо хардкода, чтобы не ошибиться в URL
      const response = await api.get<ProductCatalogResponse>(
        `${ROUTES.PRODUCTSCATALOG}?${queryString}`,
      )
      // Возвращаем сразу response.data, чтобы в компоненте было data.results
      return response.data
    },
  })
}
