"use client"

import {
  useForm,
  Controller,
  FormProvider,
  UseFormSetError,
  FieldValues,
} from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { PhoneInput } from "@/shared/ui/PhoneInput"
import {
  codeSchema,
  CodeSchema,
  phoneSchema,
  PhoneSchema,
} from "../model/schemas"
import { useCooldown } from "@/shared/lib/hooks"
import { errorHandler } from "@/shared/lib/utils/errorHandler"
import { JSX, useEffect, useRef, useState } from "react"
import clsx from "clsx"
import styles from "./AuthForm.module.scss"
import { ApiAction, useAuthStore } from "@/entities/auth"
import { THROTTLES } from "@/shared/config/throttles"
import { OtpInput } from "@/shared/ui/OtpInput"

type Props = {
  isCodeStep: boolean
  setIsCodeStep: (v: boolean) => void
  setSwitchBackToSMS: (v: boolean) => void
}

export const AuthForm: React.FC<Props> = ({
  isCodeStep,
  setIsCodeStep,
  setSwitchBackToSMS,
}) => {
  // 1. Состояния UI
  const [isTyping, setIsTyping] = useState(false)

  // const { isAuth, isCodeSent, isLoading } = useAuthStore(
  //   useShallow((state) => ({
  //     isAuth: state.isAuth,
  //     isCodeSent: state.isCodeSent,
  //     isLoading: state.isLoading,
  //   })),
  // )

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
    defaultValues: {
      sms_code: "",
    },
  })

  const {
    // register, // Вручную вставляем через setValue
    handleSubmit: handleCodeSubmit,
    setError: setCodeError,
    clearErrors: clearCodeErrors,
    trigger: triggerCode,
    formState: {
      errors: codeErrors,
      isSubmitting: isCodeSubmitting,
      isValid: isCodeValid,
    },
  } = codeForm

  // 4. Таймеры
  const {
    seconds: secondsPhone,
    isActive: isActivePhone,
    startCooldown: startCooldownPhone,
  } = useCooldown(THROTTLES.PHONE)
  const {
    seconds: secondsCode,
    isActive: isActiveCode,
    startCooldown: startCooldownCode,
  } = useCooldown(THROTTLES.AUTH)

  // 5. Эффекты. Очищаем глобальные ошибки после таймера
  useEffect(() => {
    if (!isActivePhone) {
      clearPhoneErrors()
      triggerPhone()
    }
  }, [isActivePhone, clearPhoneErrors, triggerPhone])

  const isFirstRender = useRef(true)
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false
      return
    }

    // if (!isActiveCode) {
    //   clearCodeErrors()
    //   // triggerCode()
    // }
  }, [isActiveCode, clearCodeErrors, triggerCode])

  // 6. Обработчики событий

  const errorFromAPISet = <T extends FieldValues>(
    result: ApiAction,
    setError: UseFormSetError<T>,
    formData: T,
    startCooldown: (customSeconds?: number | undefined) => void,
    throttleSecondsLeft?: number,
  ) => {
    console.log("Ошибка errorFromAPISet", result.error)

    const secondsLeft = errorHandler(result.error, setError, formData)

    startCooldown(secondsLeft || throttleSecondsLeft || THROTTLES.PHONE)
  }

  // Отправка смс
  const onSubmitPhoneNumber = async (data: PhoneSchema) => {
    // Отправляем запрос на api
    const result = await useAuthStore.getState().sendSms(data.phone_number)

    // При ошибке вызываем обработчик и выходим
    if (!result.success) {
      errorFromAPISet(
        result,
        setPhoneError,
        phoneForm.getValues(),
        startCooldownPhone,
        THROTTLES.PHONE,
      )
      // console.log("Ошибка 1", result.error)

      // const secondsLeft = errorHandler(
      //   result.error,
      //   setPhoneError,
      //   phoneForm.getValues(),
      // )

      // startCooldownPhone(secondsLeft || THROTTLES.PHONE)

      // return
    }

    // Запускаем cooldown, если не было ошибки
    startCooldownPhone(THROTTLES.PHONE)

    // Если все успешно, то переходим на смс-код
    // useAuthWindowStore.getState().setIsPhonePage(false)
    setIsCodeStep(true)

    // Ресетим все
    phoneForm.reset(undefined, {
      keepIsSubmitted: false,
      keepTouched: false,
      keepValues: true,
    })
    triggerPhone()
  }

  // Проверка кода
  const onSubmitCode = async (data: CodeSchema) => {
    const phone = phoneForm.getValues("phone_number")

    console.log("Проверка перед отправкой", {
      phone_number: phone.startsWith("+7") ? phone : `+7${phone}`,
      sms_code: data.sms_code,
    })

    if (!data?.sms_code)
      setCodeError("sms_code", {
        type: "manual",
        message: "Введите смс-код.",
      })

    // Отправляем запрос с аутенфикацией
    const result = await useAuthStore.getState().auth(phone, data.sms_code)

    console.log("Проверка ошибки", result.error)

    // При ошибке вызываем обработчик и выходим
    if (!result.success) {
      const codeFormValues = codeForm.getValues()

      // console.log("Ошибка 2", result.error)
      errorFromAPISet(
        result,
        setCodeError,
        codeFormValues,
        startCooldownCode,
        THROTTLES.AUTH,
      )

      // const secondsLeft = errorHandler(
      //   result.error,
      //   setCodeError,
      //   codeForm.getValues(),
      // )

      // startCooldownCode(secondsLeft || THROTTLES.AUTH)

      // Сбрасываем форму
      codeForm.reset(codeFormValues, {
        keepErrors: true,
        keepIsSubmitted: false,
        keepTouched: false,
        keepValues: true,
      })

      return
    }

    // Все равно вызываем cooldown
    startCooldownPhone(THROTTLES.AUTH)

    // Сбрасываем форму
    // codeForm.reset()
  }

  // onClick для кнопки повторного смс
  const onClickRepeatSMS = async () => {
    const phone = phoneForm.getValues("phone_number")
    const result = await useAuthStore.getState().sendSms(phone)

    if (!result.success) {
      console.log("Ошибка 3. Повторный смс-код", result.error)
      errorFromAPISet(
        result,
        setPhoneError,
        phoneForm.getValues(),
        startCooldownPhone,
        THROTTLES.REPEAT_SMS,
      )
    }

    startCooldownPhone(THROTTLES.REPEAT_SMS)
  }

  // 7. Вычисляемые значения
  const isPhoneBtnDisabled: boolean =
    isPhoneSubmitting ||
    isActivePhone ||
    !!phoneErrors.phone_number ||
    !isPhoneValid

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
                setSwitchBackToSMS(false)
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
          : isActivePhone
            ? `Отправлено. Повторить можно через: ${secondsPhone}`
            : "Получить код"}
      </button>
    </form>
  )

  // Рендер этапа 2: Ввод смс-кода
  const renderCodeStep = (): JSX.Element => (
    <FormProvider {...codeForm}>
      <div className="flex flex-col items-center animate-in fade-in duration-500">
        <form
          onSubmit={handleCodeSubmit(onSubmitCode)}
          className="flex flex-col items-center space-y-4"
        >
          {phoneErrors.root && (
            <div className="text-red-500 text-sm mb-6 text-center">
              {phoneErrors.root.message}
            </div>
          )}

          {codeErrors.root && (
            <div className="text-red-500 text-sm mb-6 text-center">
              {codeErrors.root.message}
            </div>
          )}

          <OtpInput />
          {/* {[...Array(6)].map((_, i) => (
              <input
                key={i}
                ref={(el) => {
                  otpRefs.current[i] = el
                }}
                name="sms_code"
                type="text"
                inputMode="numeric"
                maxLength={1}
                onChange={(e) => handleOtpChange(i, e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Backspace" && !e.currentTarget.value && i > 0) {
                    otpRefs.current[i - 1]?.focus()
                  }
                }}
                className={styles.codeInput}
              />
            ))} */}

          {codeErrors.sms_code && (
            <p className="text-red-500 text-xs">
              {codeErrors.sms_code.message}
            </p>
          )}

          <button
            type="submit"
            disabled={
              isActiveCode ||
              !codeForm.formState.isDirty ||
              (codeForm.watch("sms_code") || "").length !== 6
            }
            className={styles.buttonAuth}
          >
            {isCodeValid && isCodeSubmitting
              ? "Проверка..."
              : isActiveCode
                ? `Повторить можно через: ${secondsCode}`
                : "Войти"}
          </button>

          <button
            type="button"
            disabled={isActivePhone}
            className={styles.buttonRepeatSMS}
            onClick={onClickRepeatSMS}
          >
            {isActivePhone
              ? `Повторно отправить смс-код можно через ${secondsPhone}`
              : "Отправить код снова"}
          </button>
        </form>
      </div>
    </FormProvider>
  )

  return <>{!isCodeStep ? renderPhoneStep() : renderCodeStep()}</>
}
