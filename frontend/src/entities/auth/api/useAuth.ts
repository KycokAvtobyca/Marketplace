import { useMutation, useQueryClient } from "@tanstack/react-query"
import {
  ErrorResponseAuthData,
  useAuthStore,
  AuthApiAction,
} from "@/entities/auth"
import { useAuthWindowStore } from "@/entities/authWindow"
import { api } from "@/shared/api"
import { isAxiosError } from "axios"
import { ROUTES } from "@/shared/config"
import { useRouter } from "next/navigation"

export const useAuth = () => {
  const setIsAuth = useAuthStore((s) => s.setIsAuth)
  const queryClient = useQueryClient()
  const setAuthWindowOpen = useAuthWindowStore((s) => s.setIsOpen)
  const router = useRouter()

  return useMutation({
    mutationFn: async ({
      phone_number: phone,
      sms_code: smsCode,
      password,
    }: {
      phone_number: string
      sms_code: string
      password?: string
    }): Promise<AuthApiAction> => {
      try {
        const { data } = await api.post<{
          requires_password?: boolean
          is_superuser?: boolean
          phone_number?: string
        }>(ROUTES.AUTH.TOKEN, {
          phone_number: phone.startsWith("+7") ? phone : `+7${phone}`,
          sms_code: smsCode,
          ...(password ? { password } : {}),
        })

        if (data.requires_password) {
          return {
            success: false,
            requiresPassword: true,
            error: {
              data: {
                detail: {
                  message: "Введите пароль администратора.",
                },
              },
            },
          }
        }

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
      if (result.error?.data?.detail?.code === "user_blocked") {
        setAuthWindowOpen(false)
        router.replace("/blocked")
        return
      }

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
