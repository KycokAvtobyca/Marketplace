"use client"

import { AuthForm } from "@/features/AuthByPhone/ui/AuthForm"
import { Window } from "@/shared/ui/Window"
import { SuspenseIcon } from "@/shared/ui/SuspenseIcon"
import { useAuthWindowStore } from "@/entities/authWindow/"
import { useShallow } from "zustand/shallow"
import { useEffect, useState } from "react"
import { Icon } from "@/shared/ui/Icons"

import { useAuthStore } from "@/entities/auth"
import { createPortal } from "react-dom"

export const AuthWindow = () => {
  const { isOpen, toggle } = useAuthWindowStore(
    useShallow((state) => ({
      isOpen: state.isOpen,
      toggle: state.toggle,
    })),
  )

  // Добавляем стейт, чтобы знать, что мы в браузере
  const [mounted, setMounted] = useState(false)

  const isAuth = useAuthStore((state) => state.isAuth)

  const [isCodeStep, setIsCodeStep] = useState(false)
  const [isPossibleSwitchBackToSMS, setSwitchBackToSMS] = useState(false)

  // useEffect срабатывает только на клиенте после первого рендера
  useEffect(() => {
    if (!isOpen) return

    setMounted(true)

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") toggle()
    }

    window.addEventListener("keydown", handleKeyDown)

    return () => {
      window.removeEventListener("keydown", handleKeyDown)
    }
  })

  // Если мы еще не на клиенте или пользователь авторизован - ничего не рендерим
  if (!mounted || isAuth) return null

  const portalRoot = document.getElementById("modals")
  if (!portalRoot) return null

  return createPortal(
    <Window
      title="Вход"
      subtitle="Пожалуйста, войдите в систему, чтобы продолжить."
      wayAs="article"
      className={`max-w-96 w-full h-auto bg-default`}
      isOpen={isOpen}
      toggleWindow={toggle}
      backRedirect={
        !isCodeStep ? (
          <div className="w-full">
            {isPossibleSwitchBackToSMS ? (
              <SuspenseIcon
                logic={() => {
                  setIsCodeStep(true)
                  setSwitchBackToSMS(false)
                }}
                className="ml-auto"
                Icon={Icon.ARROWRIGHT}
              />
            ) : (
              <SuspenseIcon
                logic={toggle}
                className="ml-auto"
                Icon={Icon.CLOSE}
              />
            )}
          </div>
        ) : (
          <div className="w-full">
            <SuspenseIcon
              logic={() => {
                setIsCodeStep(false)
                setSwitchBackToSMS(true)
              }}
              className="mr-auto"
              Icon={Icon.ARROWLEFT}
            />
          </div>
        )
      }
    >
      <AuthForm
        isCodeStep={isCodeStep}
        setIsCodeStep={setIsCodeStep}
        setSwitchBackToSMS={setSwitchBackToSMS}
      />
    </Window>,
    portalRoot,
  )
}
