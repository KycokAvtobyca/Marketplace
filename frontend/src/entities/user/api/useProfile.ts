import { useQuery } from "@tanstack/react-query"
import { usePathname } from "next/navigation"
import { api } from "@/shared/api"

export const useProfile = () => {
  const pathname = usePathname()
  const isBlockedPage = pathname === "/blocked"

  return useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const { data } = await api.get("/users/profile/")
      return data
    },
    enabled: !isBlockedPage,
    // Разрешаем 1 retry, чтобы интерцептор успел обновить токен и повторить запрос
    retry: isBlockedPage ? false : 1,
    retryDelay: 500,
    staleTime: 1000 * 60 * 5, // 5 минут — соответствуем жизни access-токена
    refetchOnWindowFocus: !isBlockedPage,
  })
}
