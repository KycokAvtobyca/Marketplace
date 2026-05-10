import { useQuery } from "@tanstack/react-query"
import { isAxiosError } from "axios"
import { DefaultApiAction, DefaultErrorResponse } from "@/shared/api"
import { FilterPropertiesData } from "@/shared/config/routesInterfaces"

interface PaginatedData {
  next?: string | null
  previous?: string | null
}

export interface FilterVariables {
  cursor?: string
  categories?: string[]
  types?: string[]
  metaParams?: Record<string, number>
  startPages?: FilterPropertiesData[]
}

// Тип для фильтра (категории + типы)
// export interface FilterPropertiesData {
//   categories: CategoriesResponse;
//   product_types: ProductTypesResponse;
// }

// Тип для пагинированных списков (категории или типы продуктов отдельно)
export interface PaginatedFilterData<T> extends PaginatedData {
  results: T[]
}

// Делаем интерфейс хука универсальным через дженерики
interface IBaseFilterHook<TData> {
  key: string
  // Указываем функцию запроса снаружи, чтобы хук был гибким
  fetcher: (vars: FilterVariables) => Promise<{ data: TData }>
  variables: FilterVariables
}

function hasPagination(obj: any): obj is PaginatedData {
  return (
    obj && (typeof obj.next === "string" || typeof obj.previous === "string")
  )
}

// Базовый хук для создания других хуков на его основе
export const useBaseFilter = <
  TData,
  TError extends DefaultErrorResponse = DefaultErrorResponse,
>({
  key,
  fetcher,
  variables,
}: IBaseFilterHook<TData>) => {
  return useQuery({
    queryKey: [key, variables],
    enabled: !!variables,
    staleTime: 10 * 60 * 1000, // 10 минут
    queryFn: async (): Promise<DefaultApiAction<TData>> => {
      try {
        const response = await fetcher(variables)
        const rawData = response.data

        let data = { ...rawData }

        // Если это не свойства фильтра, пробуем декодировать пагинацию
        if (key !== "filterProperties" && hasPagination(data)) {
          // Используем Type Guard, чтобы убедить TS
          if (hasPagination(rawData)) {
            data = {
              ...data,
              // Декодируем только если значение существует, иначе оставляем null
              next: rawData.next
                ? decodeURIComponent(rawData.next)
                : rawData.next,
              previous: rawData.previous
                ? decodeURIComponent(rawData.previous)
                : rawData?.previous,
            }
          }
        }

        return {
          success: true,
          data: data as TData,
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
