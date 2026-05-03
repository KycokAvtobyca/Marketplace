import { useMutation } from "@tanstack/react-query"
import {
  ErrorResponseAuthData,
  RequestAuthData,
  useAuthStore,
  ApiAction,
} from "@/entities/auth"
import { api } from "@/shared/api"
import { isAxiosError } from "axios"
import { ROUTES } from "@/shared/config"

export const useAuth = () => {
  const setIsAuth = useAuthStore((s) => s.setIsAuth)

  return useMutation({
    mutationFn: async ({
      phone_number: phone,
      sms_code: smsCode,
    }: Record<
      keyof Omit<RequestAuthData, "code">,
      string
    >): Promise<ApiAction> => {
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
    onSuccess: (result) => {
      if (result.success) {
        setIsAuth(true)
      }
    },
  })
}
