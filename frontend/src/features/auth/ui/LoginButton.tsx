"use client"

import { useAuthStore } from "@/entities/auth/model/store"
import { useAuthWindowStore } from "@/entities/authWindow/"
import loginIcon from "@/shared/assets/icons/login-brand.svg"
import { DropDown } from "@/shared/ui/DropDown"
import { UserIcon } from "@/shared/ui/icons/icons"
import Image from "next/image"
import { useRef, useState } from "react"
import { useShallow } from "zustand/shallow"

export const LoginButton = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const toggleAuthWindow = useAuthWindowStore((s) => s.toggle)
  const buttonRef = useRef<HTMLButtonElement>(null)

  const { isAuth } = useAuthStore(
    useShallow((state) => ({
      isAuth: state.isAuth,
    })),
  )

  return (
    <div className="flex items-center gap-4 shrink-0">
      {isAuth ? (
        <>
          <button
            className="cursor-pointer"
            ref={buttonRef}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <UserIcon />
          </button>

          <DropDown anchorRef={buttonRef} isOpen={isMenuOpen}>
            <div className="text-sm">
              <p>Личный кабинет</p>
              <p>Заказы</p>
              <p>Выйти</p>
            </div>
          </DropDown>
        </>
      ) : (
        <button
          className="p-1 rounded-l cursor-pointer"
          onClick={toggleAuthWindow}
        >
          <Image src={loginIcon} alt="Войти" width={25} height={25} />
        </button>
      )}
    </div>
  )
}
