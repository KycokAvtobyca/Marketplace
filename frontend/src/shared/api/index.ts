import axios, { AxiosInstance } from "axios"

export const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const errorCode = error.response?.data?.detail?.code || error.response?.data?.code

    if (errorCode === "user_blocked") {
      if (typeof window !== "undefined") {
        window.location.href = "/blocked"
      }
      return Promise.reject(error)
    }

    // Ловим и 401 (Unauthorized) и 403 (Forbidden/CSRF Failed)
    if (
      (error.response?.status === 401 || error.response?.status === 403) &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true

      try {
        // Пробуем обновить токен
        await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/users/auth/token/refresh/`,
          {},
          { withCredentials: true },
        )

        // Повторяем запрос
        return api(originalRequest)
      } catch (refreshError) {
        // Если рефреш не удался, значит сессия реально протухла
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  },
)

export type { DefaultErrorResponse, DefaultApiAction } from "./interfaces"
