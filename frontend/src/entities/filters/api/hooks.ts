import { api, DefaultErrorResponse } from "@/shared/api"
import { FilterVariables, useBaseFilter } from "./useBaseFilter"
import {
  CategoriesResponse,
  ProductTypesResponse,
  MetaResponse,
  FilterPropertiesResponse,
} from "../model/types"
import { ROUTES } from "@/shared/config"

export const useFilterProperties = (vars: FilterVariables) => {
  return useBaseFilter<FilterPropertiesResponse>({
    fetcher: (vars) =>
      api.get(ROUTES.FILTERS.FILTER_PROPERTIES(vars.startPages)),
    key: "filterProperties",
    variables: vars,
  })
}

export const useCategories = (vars: FilterVariables) => {
  return useBaseFilter<{ categories: CategoriesResponse }>({
    fetcher: (vars) => api.get(ROUTES.FILTERS.CATEGORIES(vars.cursor)),
    key: "categories",
    variables: vars,
  })
}

export const useProductTypes = (vars: FilterVariables) => {
  return useBaseFilter<ProductTypesResponse>({
    fetcher: (vars) =>
      api.get(ROUTES.FILTERS.TYPES(vars.categories, vars.cursor)),
    variables: vars,
    key: "productTypes",
  })
}

export const useMetaObjects = (vars: FilterVariables) => {
  return useBaseFilter<MetaResponse>({
    fetcher: (vars) =>
      api.get(
        ROUTES.FILTERS.META(vars.categories, vars.types, vars.metaParams),
      ),
    variables: vars,
    key: "meta",
  })
}
