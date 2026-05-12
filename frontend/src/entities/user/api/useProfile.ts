import { useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"

export const useProfile = () => {
  return useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const { data } = await api.get("/users/profile/")
      return data
    },
    // Разрешаем 1 retry, чтобы интерцептор успел обновить токен и повторить запрос
    retry: 1,
    retryDelay: 500,
    staleTime: 1000 * 60 * 5, // 5 минут — соответствуем жизни access-токена
    refetchOnWindowFocus: true,
  })
}
