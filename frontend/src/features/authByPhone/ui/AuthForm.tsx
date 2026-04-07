"use client"

import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { PhoneInput } from "@/shared/ui/phoneInput/PhoneInput"
import { phoneSchema, PhoneSchema } from "../model/schemas"
import { useCooldown } from "@/shared/lib/hooks"

export const AuthForm: React.FC = () => {
  const {
    control,
    handleSubmit,
    formState: { isSubmitting, isSubmitted, errors, isValid },
  } = useForm<PhoneSchema>({
    resolver: zodResolver(phoneSchema),
    mode: "onChange",
    defaultValues: {
      phone: "",
    },
  })

  const { seconds, isActive, startCooldown } = useCooldown(60)

  const onSubmit = async (data: PhoneSchema) => {
    // Вызов API
    console.log("Sending SMS to: +7", data.phone)
    startCooldown()
  }

  const isDisabled = isSubmitting || isSubmitted || !isValid

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col items-end">
      <Controller
        name="phone"
        control={control}
        render={({ field, fieldState }) => (
          <PhoneInput
            {...field}
            error={
              fieldState.isTouched || isSubmitted
                ? fieldState.error?.message
                : undefined
            }
          />
        )}
      />

      <button
        type="submit"
        disabled={isDisabled}
        className={`whitespace-nowrap pt-2 transition-all
          ${isActive ? "text-gray-400 cursor-not-allowed" : "cursor-pointer"}  
        `}
      >
        {isSubmitting
          ? "Отправляем..."
          : isActive
            ? `Отправлено. Повторить можно через: ${seconds}`
            : "Получить код"}
      </button>
    </form>
  )
}
