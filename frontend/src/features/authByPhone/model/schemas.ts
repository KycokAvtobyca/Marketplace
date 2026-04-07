import * as z from "zod"

export const phoneSchema = z.object({
  phone: z.string().length(10, "Введите корректный номер телефона"),
})

export type PhoneSchema = z.infer<typeof phoneSchema>
