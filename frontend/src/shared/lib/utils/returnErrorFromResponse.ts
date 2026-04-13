import { AxiosError } from "axios"

interface ErrorParams {
  error: AxiosError<Record<string, any>>
  dataAttr?: string
  defaultDataAttr?: string
}

export const returnErrorMessageFromResponse = ({
  error,
  dataAttr,
  defaultDataAttr = "detail",
}: ErrorParams): string | undefined => {
  const data = error.response?.data

  if (typeof data !== "object" || data === null) {
    return "Непредвиденная ошибка сервера. Мы уже занимаемся этим."
  }

  const message = dataAttr
    ? data?.[dataAttr] || data?.[defaultDataAttr]
    : data?.[defaultDataAttr]

  if (Array.isArray(message)) return message[0]
  if (typeof message === "string") return message

  return undefined
}
