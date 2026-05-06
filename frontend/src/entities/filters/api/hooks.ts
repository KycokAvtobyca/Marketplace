import { api, DefaultErrorResponse } from "@/shared/api"
import { useBaseFilter } from "./useBaseFilter"
import {
  CategoriesResponse,
  ProductTypesResponse,
  MetaResponse,
} from "./interfaces"
import { ROUTES } from "@/shared/config"

export const useCategories = () => {
  return useBaseFilter<CategoriesResponse, DefaultErrorResponse>({
    fetcher: (vars) => api.get(ROUTES.FILTERS.CATEGORIES(vars.cursor)),
  })
}

export const useProductTypes = () => {
  return useBaseFilter<ProductTypesResponse, DefaultErrorResponse>({
    fetcher: (vars) =>
      api.get(ROUTES.FILTERS.TYPES(vars.categories, vars.cursor)),
  })
}

export const useMetaAttrs = () => {
  return useBaseFilter<MetaResponse, DefaultErrorResponse>({
    fetcher: (vars) =>
      api.get(
        ROUTES.FILTERS.META(vars.categories, vars.types, vars.metaParams),
      ),
  })
}
