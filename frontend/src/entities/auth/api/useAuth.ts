import { useMutation, useQueryClient } from "@tanstack/react-query"
import {
  ErrorResponseAuthData,
  RequestAuthData,
  useAuthStore,
  AuthApiAction,
} from "@/entities/auth"
import { useAuthWindowStore } from "@/entities/authWindow"
import { api } from "@/shared/api"
import { isAxiosError } from "axios"
import { ROUTES } from "@/shared/config"

export const useAuth = () => {
  const setIsAuth = useAuthStore((s) => s.setIsAuth)
  const queryClient = useQueryClient()
  const setAuthWindowOpen = useAuthWindowStore((s) => s.setIsOpen)

  return useMutation({
    mutationFn: async ({
      phone_number: phone,
      sms_code: smsCode,
    }: Record<
      keyof Omit<RequestAuthData, "code">,
      string
    >): Promise<AuthApiAction> => {
      try {
        await api.post<RequestAuthData>(ROUTES.AUTH.TOKEN, {
          phone_number: phone.startsWith("+7") ? phone : `+7${phone}`,
          sms_code: smsCode,
        })

        return {
          success: true,
        }
      } catch (error) {
        if (isAxiosError<ErrorResponseAuthData>(error)) {
          return {
            success: false,
            error: {
              data: error.response?.data as ErrorResponseAuthData,
            },
          }
        }

        // На случай сетевых ошибок или проблем с кодом
        return {
          success: false,
          error: {
            data: {
              detail: {
                message: "Произошла непредвиденная ошибка",
                seconds_left: "60",
              },
            },
          },
        }
      }
    },
    onSuccess: async (result) => {
      if (result.success) {
        setIsAuth(true)
        // Сразу перезапрашиваем данные профиля и избранного,
        // чтобы интерфейс мгновенно переключился на авторизованный режим
        await queryClient.refetchQueries({ queryKey: ["profile"], exact: true })
        await queryClient.refetchQueries({ queryKey: ["favorites"], exact: true })
        // Закрываем окно авторизации
        setAuthWindowOpen(false)
      }
    },
  })
}