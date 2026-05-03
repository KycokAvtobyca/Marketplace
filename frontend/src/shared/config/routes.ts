type Prefixed<T> = {
  [K in keyof T]: T[K] extends string
    ? string
    : T[K] extends (...args: any[]) => string
      ? (...args: Parameters<T[K]>) => string
      : T[K] extends object
        ? Prefixed<T[K]>
        : T[K]
}

const BASE_URL = "/"

// Вспомогательная функция для автоматического добавления префикса
function withPrefix<T extends Record<string, any>>(
  prefix: string,
  routes: T,
): Prefixed<T> {
  const result = {} as any

  for (const key in routes) {
    const value = routes[key]

    if (typeof value === "string") {
      result[key] = prefix + value
    } else if (typeof value === "function") {
      result[key] = (...args: any[]) => prefix + value(...args)
    } else if (typeof value === "object" && value !== null) {
      result[key] = withPrefix(prefix, value)
    } else {
      result[key] = value
    }
  }

  return result
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
  SKU: {
    ROOT: "sku/",
    RETRIEVE: (id: number) => `sku/${id}/`,
  },
}

const USER_BASE_URL = BASE_URL + "users/"

const USER_APP_ROUTES = {
  AUTH: {
    SEND_SMS: "auth/send-sms/",
    TOKEN: "auth/token/",
    TOKEN_REFRESH: "auth/token/refresh/",
    TOKEN_VERIFY: "auth/token/verify/",
  },

  SHOP: {
    ROOT: "shop/",
    RETRIEVE: (slug: string) => "shop/" + `${slug}/`,
  },

  PROFILE: {
    ROOT: "profile/",
    EXIT: "profile/exit/",
  },
}

export const ROUTES = {
  HOME: BASE_URL,
  ...withPrefix(CATALOG_BASE_URL, CATALOG_APP_ROUTES),
  ...withPrefix(USER_BASE_URL, USER_APP_ROUTES),
} as const
