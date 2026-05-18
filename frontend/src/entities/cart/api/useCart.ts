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
      product_id: number
      product_slug: string
      brand: string | null
      price: number
      final_price: number
      stock: number
      image: string
    }
    quantity: number
    total_price: number
    has_promocode_discount: boolean
    promocode_discount: string
    promocode_final_price: string
    promocode_total_price: string
  }>
  total_items_price: number
  total_cost: number
  promocode: number | null
  promocode_code?: string | null
  promocode_discount?: string
}

interface CartApiAction {
  success: boolean
  error?: {
    data: {
      detail?: string | string[]
      error?: string | string[]
      promocode?: string | string[]
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
    retry: false,
  })
}

export const useRemoveFromCart = () => {
  return useMutation({
    // Изменяем аргумент на объект, чтобы он совпадал с handleRemove
    mutationFn: async ({
      cart_item_id,
    }: {
      cart_item_id: number
    }): Promise<CartApiAction> => {
      try {
        const response = await api.delete<{
          message: string
          cart: CartResponse
        }>(ROUTES.CART.REMOVE_ITEM, {
          // Axios требует, чтобы тело DELETE запроса передавалось в ключе data
          data: { cart_item_id },
        })

        return {
          success: true,
          data: response.data.cart,
        }
      } catch {
        // ... твой код обработки ошибок остается таким же ...
        return { success: false, error: { data: { detail: "Ошибка" } } }
      }
    },
  })
}

export const useUpdateCartItemQuantity = () => {
  return useMutation({
    mutationFn: async ({
      cart_item_id,
      quantity,
    }: {
      cart_item_id: number
      quantity: number
    }): Promise<CartApiAction> => {
      try {
        const response = await api.patch<{
          message: string
          cart: CartResponse
        }>(ROUTES.CART.UPDATE_ITEM, {
          cart_item_id,
          quantity,
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
              detail: "Не удалось обновить количество",
            },
          },
        }
      }
    },
  })
}

export const useApplyPromocode = () => {
  return useMutation({
    mutationFn: async (code: string): Promise<CartApiAction> => {
      try {
        const response = await api.post<{
          message: string
          cart: CartResponse
        }>(ROUTES.CART.APPLY_PROMOCODE, { code })

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
                promocode?: string
              },
            },
          }
        }

        return {
          success: false,
          error: {
            data: {
              detail: "Не удалось применить промокод",
            },
          },
        }
      }
    },
  })
}

export const useRemovePromocode = () => {
  return useMutation({
    mutationFn: async (): Promise<CartApiAction> => {
      try {
        const response = await api.delete<{
          message: string
          cart: CartResponse
        }>(ROUTES.CART.REMOVE_PROMOCODE)

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
              detail: "Не удалось удалить промокод",
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
        await api.delete<{
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
