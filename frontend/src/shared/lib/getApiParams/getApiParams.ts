export const getApiParams = (selectedFilters: (string | number)[]) => {
  const params: Record<string, string[]> = {}

  selectedFilters.forEach((item) => {
    // Разбиваем строку 'category__obuv' на ['category', 'obuv']
    const [group, value] = String(item).split("__")

    if (group && value) {
      if (!params[group]) {
        params[group] = []
      }
      params[group].push(value)
    }
  })

  return params
}
