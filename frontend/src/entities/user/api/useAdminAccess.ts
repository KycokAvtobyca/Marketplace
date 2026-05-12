import { useQuery, useMutation } from "@tanstack/react-query"
import { api } from "@/shared/api"

function getBackendBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") || "http://127.0.0.1:8001"
}

/**
 * Хук для проверки, есть ли у пользователя доступ к Django админке.
 * Проверяет поле is_staff в профиле пользователя.
 */
export const useCheckAdminAccess = () => {
  return useQuery({
    queryKey: ["admin_access"],
    queryFn: async () => {
      const { data } = await api.get("/users/profile/")
      return data.is_staff === true
    },
    retry: 1,
    staleTime: 1000 * 60 * 5,
    refetchOnWindowFocus: true,
  })
}

/**
 * Хук для перенаправления пользователя в Django админку.
 * Переходит на корневой endpoint бэкенда (/admin-login/), который автоматически
 * логинит через JWT cookie и редиректит в /admin/.
 */
export const useRedirectToAdmin = () => {
  return useMutation({
    mutationFn: async () => {
      const base = getBackendBaseUrl()
      window.location.href = `${base}/admin-login/`
    },
  })
}
