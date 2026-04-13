"use client"

import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { PhoneInput } from "@/shared/ui/phoneInput"
import {
  codeSchema,
  CodeSchema,
  phoneSchema,
  PhoneSchema,
} from "../model/schemas"
import { useCooldown } from "@/shared/lib/hooks"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config/routes"
import axios from "axios"
import { errorHandler, ResponseData } from "@/shared/lib/utils/errorHandler"
import { JSX, useEffect, useState } from "react"
import clsx from "clsx"

export const AuthForm: React.FC = () => {
  // 1. Состояния UI
  const [isTyping, setIsTyping] = useState(false)
  const [isCodeSent, setIsCodeSent] = useState(false)

  // 2. Форма №1: номер телефона
  const phoneForm = useForm<PhoneSchema>({
    resolver: zodResolver(phoneSchema),
    mode: "onChange",
    defaultValues: {
      phone_number: "",
    },
  })

  const {
    control,
    handleSubmit: handlePhoneSubmit,
    setError: setPhoneError,
    clearErrors: clearPhoneErrors,
    trigger: triggerPhone,
    formState: {
      errors: phoneErrors,
      isSubmitting: isPhoneSubmitting,
      isValid: isPhoneValid,
    },
  } = phoneForm

  // 3. Форма №2: смс-код
  const codeForm = useForm<CodeSchema>({
    resolver: zodResolver(codeSchema),
    mode: "onChange",
  })

  const {
    handleSubmit: handleCodeSubmit,
    setValue: setCodeValue,
    formState: { errors: codeErrors, isSubmitting: isVerifying },
  } = codeForm

  // 4. Таймер
  const { seconds, isActive, startCooldown } = useCooldown(60)

  // 5. Эффекты. Очищаем глобальные ошибки после таймера
  useEffect(() => {
    if (!isActive) {
      clearPhoneErrors("root")
      triggerPhone()
    }
  }, [isActive, clearPhoneErrors, triggerPhone])

  // 6. Обработчики событий

  // Отправка смс
  const onSubmitPhoneNumber = async (data: PhoneSchema) => {
    try {
      const { phone_number } = data

      const response = await api.post(ROUTES.API_AUTH_SEND_SMS, {
        phone_number: phone_number,
      })

      startCooldown()
      setIsCodeSent(true)

      phoneForm.reset(data, {
        keepIsSubmitted: false,
        keepTouched: false,
        keepValues: true,
      })
      triggerPhone()
    } catch (e: unknown) {
      if (axios.isAxiosError(e)) {
        const data: ResponseData = e.response?.data
        const secondsLeft = data?.detail?.seconds_left

        if (secondsLeft) startCooldown(secondsLeft)
      }

      errorHandler(e, setPhoneError)
    }
  }

  // Проверка кода
  // pass

  // Логика OTP-инпута (автопереход)
  // const handleOtpChange = (index: number, value: string) => {
  //   const char = value.slice(-1)

  //   // Вызвать ошибку
  //   if (!/^\d?$/.test(char)) return

  // }

  // 7. Вычисляемые значения
  const isPhoneBtnDisabled: boolean =
    isPhoneSubmitting || isActive || !!phoneErrors.phone_number || !isPhoneValid

  // 8. Рендер

  // Рендер этапа 1: Ввод номера телефона
  const renderPhoneStep = (): JSX.Element => (
    <form
      onSubmit={handlePhoneSubmit(onSubmitPhoneNumber)}
      className="flex flex-col items-end"
    >
      {phoneErrors.root && (
        <div className="text-red-500 text-sm mb-6 text-center">
          {phoneErrors.root.message}
        </div>
      )}

      <Controller
        name="phone_number"
        control={control}
        render={({ field, fieldState }) => {
          const digits = field.value.replace(/\D/g, "")

          return (
            <PhoneInput
              {...field}
              onChange={(value) => {
                setIsTyping(true)
                field.onChange(value)
              }}
              onBlur={() => {
                setIsTyping(false)
                field.onBlur()
              }}
              error={
                digits.length > 0 &&
                ((digits.length >= 10 && fieldState.invalid) || !isTyping)
                  ? fieldState.error?.message
                  : undefined
              }
            />
          )
        }}
      />

      <button
        type="submit"
        disabled={isPhoneBtnDisabled}
        className={clsx("whitespace-nowrap pt-2 transition-all", {
          "text-gray-400 cursor-not-allowed": isPhoneBtnDisabled,
          "cursor-pointer hover:opacity-80": !isPhoneBtnDisabled,
        })}
      >
        {isPhoneSubmitting
          ? "Отправляем..."
          : isActive
            ? `Отправлено. Повторить можно через: ${seconds}`
            : "Получить код"}
      </button>
    </form>
  )

  // Рендер этапа 2: Ввод смс-кода
  const renderCodeStep = (): JSX.Element => (
    <div className="flex flex-col items-center animate-in fade-in duration-500">
      <form className="flex flex-col items-center">
        <div className="flex gap-2 mb-4">
          {[...Array(6)].map((_, i) => (
            <input
              key={i}
              name="code"
              type="text"
              inputMode="numeric"
              maxLength={1}
              onKeyDown={(e) => {
                if (e.key === "Backspace" && !e.currentTarget.value && i > 0) {
                }
              }}
            />
          ))}
        </div>

        {codeErrors.code && (
          <p className="text-red-500 text-xs mb-4">{codeErrors.code.message}</p>
        )}

        <button
          type="submit"
          disabled={isVerifying}
          className="w-full bg-black text-white py-2 rounded-lg disabled:bg-gray-300"
        >
          {isVerifying ? "Проверка..." : "Войти"}
        </button>

        <button
          type="button"
          onClick={() => setIsCodeSent(false)}
          className="mt-4 text-sm text-gray-500 underline"
        >
          Изменить номер
        </button>
      </form>
    </div>
  )

  return <>{!isCodeSent ? renderPhoneStep() : renderCodeStep()}</>
}
