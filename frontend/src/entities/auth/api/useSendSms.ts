import { useMutation } from "@tanstack/react-query"
import {
  AuthApiAction,
  ErrorResponseAuthData,
  RequestAuthData,
  useAuthStore,
} from "@/entities/auth"
import { api } from "@/shared/api"
import { isAxiosError } from "axios"
import { ROUTES } from "@/shared/config"

export const useSendSms = () => {
  const setIsCodeSent = useAuthStore((s) => s.setIsCodeSent)

  return useMutation({
    mutationFn: async (phone: string): Promise<AuthApiAction> => {
      try {
        await api.post<RequestAuthData>(ROUTES.AUTH.SEND_SMS, {
          phone_number: phone.startsWith("+7") ? phone : `+7${phone}`,
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
    onSuccess: (result) => {
      if (result.success) {
        setIsCodeSent(true)
      }
    },
  })
}
