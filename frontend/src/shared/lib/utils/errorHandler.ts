import axios from "axios"
import { FieldValues, Path, UseFormSetError } from "react-hook-form"
import { keyof } from "zod"

export interface ResponseData {
  detail?: {
    message?: string
    seconds_left?: number
  }
  phone_number?: string
  sms_code?: string
}

export const errorHandler = <T extends FieldValues>(
  e: unknown,
  setError: UseFormSetError<T>,
) => {
  const defaultMessage =
    "Произошла непредвиденная ошибка. Мы уже занимаемся этим."

  if (axios.isAxiosError(e)) {
    let lastMessage

    const data: ResponseData = e.response?.data

    if (!data || typeof data !== "object") {
      // Отправка на API отчет об ошибке
      setError("root" as Path<T>, { type: "manual", message: defaultMessage })
      return defaultMessage
    }

    const keys = Object.keys(data) as (keyof ResponseData)[]

    keys.forEach((key) => {
      const backendMessage = key === "detail" ? data[key]?.message : data[key]

      const finalMessage =
        typeof backendMessage === "string" ? backendMessage : defaultMessage

      console.log(key)

      if (key === "detail") {
        setError("root", { type: "manual", message: finalMessage })
      } else {
        setError(key as Path<T>, { type: "manual", message: finalMessage })
      }

      lastMessage = backendMessage
    })

    console.error(lastMessage, e?.response)

    return lastMessage

    // Отправка на API отчет об ошибке
  } else {
    console.error(defaultMessage)
    // Отправка на API отчет об ошибке
  }
}
