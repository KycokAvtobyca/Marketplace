import { useMutation, useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"
import { isAxiosError } from "axios"

interface AddToCartPayload {
  product_variant_id: number
  quantity?: number
}

interface CartResponse {
  id: number
  cart_items: Array<{
    id: number
    product_variant: {
      id: number
      sku: string
      product_name: string
      product_slug: string
      brand: string | null
      price: number
      final_price: number
      stock: number
      image: string
    }
    quantity: number
    total_price: number
  }>
  total_items_price: number
  total_cost: number
  promocode: number | null
}

interface CartApiAction {
  success: boolean
  error?: {
    data: {
      detail?: string
      error?: string
    }
  }
  data?: CartResponse
}

export const useAddToCart = () => {
  return useMutation({
    mutationFn: async (payload: AddToCartPayload): Promise<CartApiAction> => {
      try {
        const response = await api.post<{
          message: string
          cart: CartResponse
        }>(ROUTES.CART.ADD_ITEM, payload)

        return {
          success: true,
          data: response.data.cart,
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
              detail: "Произошла ошибка при добавлении в корзину",
            },
          },
        }
      }
    },
  })
}

export const useGetCart = () => {
  return useQuery({
    queryKey: ["cart"],
    queryFn: async (): Promise<CartResponse> => {
      const response = await api.get<CartResponse>(ROUTES.CART.GET_CONTENTS)
      return response.data
    },
  })
}

export const useRemoveFromCart = () => {
  return useMutation({
    mutationFn: async (cartItemId: number): Promise<CartApiAction> => {
      try {
        const response = await api.delete<{
          message: string
          cart: CartResponse
        }>(ROUTES.CART.REMOVE_ITEM, {
          data: { cart_item_id: cartItemId },
        })

        return {
          success: true,
          data: response.data.cart,
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
              detail: "Произошла ошибка при удалении из корзины",
            },
          },
        }
      }
    },
  })
}

export const useClearCart = () => {
  return useMutation({
    mutationFn: async (): Promise<CartApiAction> => {
      try {
        const response = await api.delete<{
          message: string
        }>(ROUTES.CART.CLEAR)

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
              detail: "Произошла ошибка при очистке корзины",
            },
          },
        }
      }
    },
  })
}
