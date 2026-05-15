import { useMutation, useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"
import { isAxiosError } from "axios"

interface AddToFavoritesPayload {
  product_variant_id: number
}

interface FavoritesResponse {
  id: number
  favorite_items: Array<{
    id: number
    product_variant: {
      id: number
      sku: string
      product_name: string
      product_id: number
      product_slug: string
      brand: string | null
      price: number
      final_price: number
      stock: number
      image: string
    }
  }>
  items_count: number
}

interface FavoritesApiAction {
  success: boolean
  error?: {
    data: {
      detail?: string
      error?: string
    }
  }
  data?: FavoritesResponse
}

export const useAddToFavorites = () => {
  return useMutation({
    mutationFn: async (
      payload: AddToFavoritesPayload,
    ): Promise<FavoritesApiAction> => {
      try {
        const response = await api.post<{
          message: string
          favorite: FavoritesResponse
        }>(ROUTES.FAVORITES.ADD_ITEM, payload)

        return {
          success: true,
          data: response.data.favorite,
        }
      } catch (error) {
        if (isAxiosError(error)) {
          return {
            success: false,
            error: {
              data: error.response?.data as {
                detail?: string
                error?: string
              },
            },
          }
        }

        return {
          success: false,
          error: {
            data: {
              detail: "Произошла ошибка при добавлении в избранное",
            },
          },
        }
      }
    },
  })
}

export const useGetFavorites = () => {
  return useQuery({
    queryKey: ["favorites"],
    queryFn: async (): Promise<FavoritesResponse> => {
      const response = await api.get<FavoritesResponse>(
        ROUTES.FAVORITES.GET_FAVORITES,
      )
      return response.data
    },
    retry: 1,
    retryDelay: 500,
    staleTime: 1000 * 60 * 5, // 5 минут
    refetchOnWindowFocus: true,
  })
}

export const useRemoveFromFavorites = () => {
  return useMutation({
    mutationFn: async (
      productVariantId: number,
    ): Promise<FavoritesApiAction> => {
      try {
        const response = await api.delete<{
          message: string
          favorite: FavoritesResponse
        }>(ROUTES.FAVORITES.REMOVE_ITEM, {
          data: { product_variant_id: productVariantId },
        })

        return {
          success: true,
          data: response.data.favorite,
        }
      } catch (error) {
        if (isAxiosError(error)) {
          return {
            success: false,
            error: {
              data: error.response?.data as {
                detail?: string
                error?: string
              },
            },
          }
        }

        return {
          success: false,
          error: {
            data: {
              detail: "Произошла ошибка при удалении из избранного",
            },
          },
        }
      }
    },
  })
}

export const useClearFavorites = () => {
  return useMutation({
    mutationFn: async (): Promise<FavoritesApiAction> => {
      try {
        await api.delete<{
          message: string
        }>(ROUTES.FAVORITES.CLEAR)

        return {
          success: true,
        }
      } catch (error) {
        if (isAxiosError(error)) {
          return {
            success: false,
            error: {
              data: error.response?.data as {
                detail?: string
                error?: string
              },
            },
          }
        }

        return {
          success: false,
          error: {
            data: {
              detail: "Произошла ошибка при очистке избранного",
            },
          },
        }
      }
    },
  })
}
