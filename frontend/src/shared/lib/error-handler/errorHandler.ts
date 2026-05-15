import { FieldValues, Path, UseFormSetError } from "react-hook-form"

export interface BaseErrorResponse {
  detail?:
    | string
    | {
        message?: string
        seconds_left?: string
      }
}

const NON_FIELD_KEYS = ["detail", "non_field_errors"]

const isDetailObject = (
  value: unknown,
): value is { message?: string; seconds_left?: string } => {
  return !!value && typeof value === "object"
}

export const errorHandler = <T extends FieldValues, K extends object>(
  e: { data: K } | undefined,
  setError: UseFormSetError<T>,
  formValues?: T,
): undefined | number => {
  const defaultMessage =
    "Произошла непредвиденная ошибка. Мы уже занимаемся этим."

  try {
    if (!e) throw new Error("Не передана ошибка из стора.")

    const data = e?.data

    if (!data || typeof data !== "object") {
      throw new Error("Данные ошибки не переданы или не являются объектом.")
    }

    const keys = Object.keys(data) as (keyof K)[]
    const detail = "detail" in data ? data.detail : undefined
    const seconds_left = isDetailObject(detail) ? detail.seconds_left : undefined

    let isErrorSet = false

    keys.forEach((key) => {
      const value = data[key]
      const fieldName = String(key)
      let backendMessage: string | undefined

      if (Array.isArray(value)) {
        const first = value[0]
        backendMessage = typeof first === "string" ? first : undefined
      } else if (key === "detail") {
        backendMessage =
          typeof value === "string"
            ? value
            : isDetailObject(value)
              ? value.message
              : undefined
      } else if (typeof value === "string") {
        backendMessage = value
      }

      if (backendMessage) {
        isErrorSet = true

        if (
          NON_FIELD_KEYS.includes(fieldName) ||
          (formValues && !(fieldName in formValues))
        ) {
          setError("root", { type: "manual", message: backendMessage })
        } else {
          setError(fieldName as Path<T>, {
            type: "manual",
            message: backendMessage,
          })
        }
      }
    })

    if (!isErrorSet) {
      throw new Error("Ошибок нет. Лишний вызов errorHandler.")
    }

    return Number(seconds_left)

    // Отправка на API отчет об ошибке
  } catch (e) {
    console.error(e)
    setError("root" as Path<T>, { type: "manual", message: defaultMessage })

    // Отправка на API отчет об ошибке
  }
}
