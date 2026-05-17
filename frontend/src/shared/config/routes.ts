import { FilterPropertiesData } from "./routesInterfaces"

type Prefixed<T> = {
  [K in keyof T]: T[K] extends string
    ? string
    : T[K] extends (...args: infer Args) => string
      ? (...args: Args) => string
      : T[K] extends Record<string, unknown>
        ? Prefixed<T[K]>
        : T[K]
}

const BASE_URL = "/"

// Вспомогательная функция для автоматического добавления префикса
function withPrefix<T extends Record<string, unknown>>(
  prefix: string,
  routes: T,
): Prefixed<T> {
  const result: Record<string, unknown> = {}

  for (const key in routes) {
    const value = routes[key]

    if (typeof value === "string") {
      result[key] = prefix + value
    } else if (typeof value === "function") {
      const routeFactory = value as (...args: unknown[]) => string
      result[key] = (...args: unknown[]) => prefix + routeFactory(...args)
    } else if (typeof value === "object" && value !== null) {
      result[key] = withPrefix(prefix, value as Record<string, unknown>)
    } else {
      result[key] = value
    }
  }

  return result as Prefixed<T>
}

const CATALOG_BASE_URL = BASE_URL + "catalog/"

const CATALOG_APP_ROUTES = {
  ATTRIBUTE_VALUES: {
    ROOT: "attribute-values/",
    RETRIEVE: (id: number) => `attribute-values/${id}/`,
  },
  ATTRIBUTES: {
    ROOT: "attributes/",
    RETRIEVE: (slug: string) => `attributes/${slug}/`,
  },
  BRANDS: {
    ROOT: "brands/",
    RETRIEVE: {
      ROOT: (slug: string) => `brands/${slug}/`,
      PRODUCTS: {
        ROOT: (slug: string) => `brands/${slug}/products/`,
        RETRIEVE: (slug: string, id: number) =>
          `brands/${slug}/products/${id}/`,
      },
    },
  },
  CATEGORIES: {
    ROOT: "categories/",
    RETRIEVE: (slug: string) => `categories/${slug}/`,
  },
  FILTER_PRICE: "filter-price/",
  PRODUCT_TAGS: {
    ROOT: "product-tags/",
    RETRIEVE: (slug: string) => `product-tags/${slug}/`,
  },
  PRODUCT_TYPES: {
    ROOT: "product-types/",
    RETRIEVE: (slug: string) => `product-types/${slug}/`,
  },
  PRODUCTS: {
    ROOT: "products/",
    RETRIEVE: (id: number) => `products/${id}/`,
  },
  PRODUCTSCATALOG: "product-catalog/",
  SKU: {
    ROOT: "sku/",
    RETRIEVE: (id: number) => `sku/${id}/`,
  },
}

const FILTERS_BASE_URL = CATALOG_BASE_URL + "filters/"

const FILTERS_APP_ROUTES = {
  FILTER_PROPERTIES: (startPages: FilterPropertiesData[] = []) => {
    const params = new URLSearchParams({ filter_properties: "true" })

    startPages.forEach((data) => {
      if (data) params.append(data.prefix, data.pageNumber)
    })

    const queryString = params.toString()
    return queryString ? `?${queryString}` : ""
  },
  CATEGORIES: (cursor: string = "") => {
    const params = new URLSearchParams()

    if (cursor) params.append("cursor", cursor)

    const queryString = params.toString()
    return queryString ? `?${queryString}` : ""
  },
  TYPES: (categories: string[] = [], cursor: string = "") => {
    const params = new URLSearchParams()

    if (cursor) params.append("cursor", cursor)

    categories.forEach((cat) => {
      if (cat) params.append("categories", cat)
    })

    const queryString = params.toString()
    return queryString ? `?${queryString}` : "/"
  },
  META: (
    categories: string[] = [],
    types: string[] = [],
    metaAttrsStart?: Record<string, number>,
  ) => {
    const params = new URLSearchParams()

    categories.forEach((cat) => {
      if (cat) params.append("categories", cat)
    })

    types.forEach((type) => {
      if (type) params.append("types", type)
    })

    if (metaAttrsStart)
      for (const [key, value] of Object.entries(metaAttrsStart)) {
        if (value !== undefined && value !== null) {
          params.append(`${key}_start`, value.toString())
        }
      }

    const queryString = params.toString()
    return queryString ? `?${queryString}` : ""
  },
}

const USER_BASE_URL = BASE_URL + "users/"

const USER_APP_ROUTES = {
  AUTH: {
    SEND_SMS: "auth/send-sms/",
    TOKEN: "auth/token/",
    TOKEN_REFRESH: "auth/token/refresh/",
    TOKEN_VERIFY: "auth/token/verify/",
    LOGOUT: "auth/logout/",
  },

  SHOP: {
    ROOT: "shop/",
    RETRIEVE: (slug: string) => "shop/" + `${slug}/`,
  },

  PROFILE: {
    ROOT: "profile/",
    EXIT: "profile/exit/",
  },

  PHONE_CHANGE: "profile/phone-change/",
  SHOP_CREATE: "shop/create/",
  MY_SHOP: "shop/my/",
}

const CART_BASE_URL = BASE_URL + "cart/"

const CART_APP_ROUTES = {
  ROOT: "",
  GET_CONTENTS: "get_contents/",
  ADD_ITEM: "add_item/",
  UPDATE_ITEM: "update_item/",
  REMOVE_ITEM: "remove_item/",
  APPLY_PROMOCODE: "apply_promocode/",
  REMOVE_PROMOCODE: "remove_promocode/",
  CLEAR: "clear/",
}

const FAVORITES_BASE_URL = BASE_URL + "favorites/"

const FAVORITES_APP_ROUTES = {
  ROOT: "",
  GET_FAVORITES: "get_favorites/",
  ADD_ITEM: "add_item/",
  REMOVE_ITEM: "remove_item/",
  CLEAR: "clear/",
}

export const ROUTES = {
  HOME: BASE_URL,
  ...withPrefix(CATALOG_BASE_URL, CATALOG_APP_ROUTES),
  FILTERS: { ...withPrefix(FILTERS_BASE_URL, FILTERS_APP_ROUTES) },
  ...withPrefix(USER_BASE_URL, USER_APP_ROUTES),
  CART: { ...withPrefix(CART_BASE_URL, CART_APP_ROUTES) },
  FAVORITES: { ...withPrefix(FAVORITES_BASE_URL, FAVORITES_APP_ROUTES) },

  ORDERS: {
    ROOT: BASE_URL + "orders/",
    CREATE: BASE_URL + "orders/create/",
    CANCEL: (id: number) => BASE_URL + `orders/${id}/cancel/`,
  },

  REVIEWS: {
    ROOT: BASE_URL + "reviews/",
    RETRIEVE: (id: number) => BASE_URL + `reviews/${id}/`,
    VOTE: (id: number) => BASE_URL + `reviews/${id}/vote/`,
    REVIEW_COMPLAINTS: BASE_URL + "reviews/review-complaints/",
    PRODUCT_COMPLAINTS: BASE_URL + "reviews/product-complaints/",
    QUESTIONS: BASE_URL + "reviews/questions/",
    QUESTION_RETRIEVE: (id: number) => BASE_URL + `reviews/questions/${id}/`,
    QUESTION_ANSWER: (id: number) => BASE_URL + `reviews/questions/${id}/answer/`,
  },
} as const
