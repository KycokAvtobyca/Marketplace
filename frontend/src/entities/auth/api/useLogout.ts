import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { useAuthStore } from "@/entities/auth"
import { ROUTES } from "@/shared/config"

export const useLogout = () => {
  const queryClient = useQueryClient()
  const setIsAuth = useAuthStore((s) => s.setIsAuth)

  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post(ROUTES.AUTH.LOGOUT)
      return data
    },
    onSuccess: () => {
      // 1. Очищаем глобальный кэш React Query
      queryClient.clear()
      // 2. Сбрасываем локальное состояние авторизации
      setIsAuth(false)
      // 3. Перезагружаем страницу для полного сброса состояния
      window.location.reload()
    },
    onError: () => {
      // Даже если сервер вернул ошибку, принудительно выходим локально
      queryClient.clear()
      setIsAuth(false)
      window.location.reload()
    },
  })
}
