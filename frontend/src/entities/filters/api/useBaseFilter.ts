import { useMutation } from "@tanstack/react-query"
import { isAxiosError } from "axios"
import { DefaultApiAction, DefaultErrorResponse } from "@/shared/api"

// Описываем переменные, которые приходят в mutate()
export interface FilterVariables {
  cursor?: string
  categories?: string[]
  types?: string[]
  metaParams?: Record<string, number>
}

// Делаем интерфейс хука универсальным через дженерики
interface IBaseFilterHook<TResponse> {
  // Указываем функцию запроса снаружи, чтобы хук был гибким
  fetcher: (vars: FilterVariables) => Promise<{ data: TResponse }>
}

// Базовый хук для создания других хуков на его основе
export const useBaseFilter = <TResponse, TError extends DefaultErrorResponse>({
  fetcher,
}: IBaseFilterHook<TResponse>) => {
  return useMutation({
    mutationFn: async (
      variables: FilterVariables = {},
    ): Promise<DefaultApiAction> => {
      try {
        const response = await fetcher(variables)
        const rawData = response.data as Record<string, any>

        const data = {
          ...rawData,
          // Декодируем только если значение существует, иначе оставляем null
          next: rawData.next ? decodeURIComponent(rawData.next) : rawData.next,
          previous: rawData.previous
            ? decodeURIComponent(rawData.previous)
            : rawData.previous,
        }

        return {
          success: true,
          data,
        }
      } catch (error) {
        if (isAxiosError<TError>(error)) {
          const data = error.response?.data

          return {
            success: false,
            error: {
              data:
                data && typeof data === "object"
                  ? data
                  : { detail: "Произошла непредвиденная ошибка" },
            },
          }
        }

        return {
          success: false,
          error: {
            data: {
              detail: {
                message: "Произошла непредвиденная ошибка",
              },
            },
          },
        }
      }
    },
  })
}
