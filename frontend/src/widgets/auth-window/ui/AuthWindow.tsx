"use client"

import { AuthForm } from "@/features/authByPhone/ui/AuthForm"
import { Window } from "@/shared/ui/window/Window"
import { useAuthStore } from "@/entities/authWindow/model/store"
import { BackRedirectLine } from "@/shared/ui/backRedirectLine"

export const AuthWindow = () => {
  const stateAuth = useAuthStore((state) => state)

  return (
    <>
      <Window
        title="Вход"
        subtitle="Пожалуйста, войдите в систему, чтобы продолжить."
        as="article"
        className={`max-w-96 w-full h-auto bg-default`}
        isOpen={stateAuth.isOpen}
        toggleWindow={stateAuth.toggle}
        backRedirect={
          <div className="w-full">
            <BackRedirectLine logic={stateAuth.toggle} className="ml-auto" />
          </div>
        }
      >
        <AuthForm />
      </Window>
    </>
  )
}
