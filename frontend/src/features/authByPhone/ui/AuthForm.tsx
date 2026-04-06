"use client"

import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { PhoneInput } from "@/shared/ui/phoneInput/PhoneInput"

const phoneSchema = z.object({
  phone: z.string().length(10, "Введите корректный номер телефона"),
})

type PhoneSchema = z.infer<typeof phoneSchema>

export const AuthForm: React.FC = () => {
  const {
    control,
    handleSubmit,
    formState: { isSubmitting, errors },
  } = useForm<PhoneSchema>({
    resolver: zodResolver(phoneSchema),
    defaultValues: {
      phone: "",
    },
  })

  const onSubmit = async (data: PhoneSchema) => {
    // Вызов API
    console.log("Sending SMS to: +7", data.phone)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="phone"
        control={control}
        render={({ field }) => (
          <PhoneInput
            value={field.value}
            onChange={field.onChange}
            error={errors.phone?.message}
          />
        )}
      />

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Отправляем..." : "Получить код"}
      </button>
    </form>
  )
}
