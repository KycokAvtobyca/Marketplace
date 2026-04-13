import * as z from "zod"

export const phoneSchema = z.object({
  phone_number: z
    .string()
    .min(1, "Введите номер телефона")
    .refine(
      (val) => {
        const digits = val.replace(/\D/g, "")
        return digits.length === 10
      },
      {
        message: "Номер должен содержать 10 цифр",
      },
    )
    .refine(
      (val) => {
        const digits = val.replace(/\D/g, "")
        return /^9\d{9}$/.test(digits)
      },
      {
        message: "Номер должен начинаться с 9",
      },
    )
    .transform((val) => {
      const digits = val.replace(/\D/g, "")
      return `+7${digits}`
    }),
})

export const codeSchema = z.object({
  code: z.string().length(6, { message: "Код должен состоять из 6 цифр" }),
})

export type PhoneSchema = z.infer<typeof phoneSchema>
export type CodeSchema = z.infer<typeof codeSchema>
