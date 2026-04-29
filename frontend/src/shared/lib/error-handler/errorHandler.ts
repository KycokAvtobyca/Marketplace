import { FieldValues, Path, UseFormSetError } from "react-hook-form"

export interface BaseErrorResponse {
  detail?: {
    message?: string
    seconds_left?: string
  }
  [key: string]: any
}

const NON_FIELD_KEYS = ["detail", "non_field_errors"]

export const errorHandler = <
  T extends FieldValues,
  K extends BaseErrorResponse,
>(
  e: { data: K } | undefined,
  setError: UseFormSetError<T>,
  formValues?: T,
): undefined | number => {
  const defaultMessage =
    "Произошла непредвиденная ошибка. Мы уже занимаемся этим."

  try {
    if (!e) throw new Error("Не передана ошибка из стора.")

    const data = e?.data
    const seconds_left = e?.data?.detail?.seconds_left

    if (!data || typeof data !== "object") {
      throw new Error("Данные ошибки не переданы или не являются объектом.")
    }

    const keys = Object.keys(data) as (keyof K)[]

    let isErrorSet = false

    keys.forEach((key) => {
      const backendMessage: string | undefined = Array.isArray(data[key])
        ? data[key][0]
        : key === "detail"
          ? data[key]?.message
          : data[key]

      if (backendMessage) {
        isErrorSet = true

        if (
          NON_FIELD_KEYS.includes(String(key)) ||
          (formValues && !(key in formValues))
        ) {
          setError("root", { type: "manual", message: backendMessage })
        } else {
          setError(key as Path<T>, { type: "manual", message: backendMessage })
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
