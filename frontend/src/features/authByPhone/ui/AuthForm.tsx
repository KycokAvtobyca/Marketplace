"use client"

import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { PhoneInput } from "@/shared/ui/phoneInput"
import { phoneSchema, PhoneSchema } from "../model/schemas"
import { useCooldown } from "@/shared/lib/hooks"

export const AuthForm: React.FC = () => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { isSubmitting, isSubmitted, isValid },
  } = useForm<PhoneSchema>({
    resolver: zodResolver(phoneSchema),
    mode: "onChange",
    defaultValues: {
      phone: "",
    },
  })

  const { seconds, isActive, startCooldown } = useCooldown(2)

  const onSubmit = async (data: PhoneSchema) => {
    try {
      // Вызов API
      console.log("Sending SMS to: +7", data.phone)
      startCooldown()

      reset(data, {
        keepIsSubmitted: false,
        keepTouched: false,
        keepValues: true,
      })
    } catch (e) {
      console.error("Ошибка при отправке", e)
    }
  }

  const isDisabled = isSubmitting || !isValid || isActive
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
        className={`whitespace-nowrap pt-2 transition-all cursor-pointer
         disabled:text-gray-400 disabled:cursor-not-allowed}  
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
