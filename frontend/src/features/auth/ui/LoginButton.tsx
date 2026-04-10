"use client"

import { useAuthStore } from "@/entities/authWindow/model/store"
import loginIcon from "@/shared/assets/icons/login-brand.svg"
import Image from "next/image"

export const LoginButton = () => {
  const toggleAuthWindow = useAuthStore((state) => state.toggle)

  return (
    <div className="flex items-center gap-4 shrink-0">
      <button
        className="p-1 rounded-l cursor-pointer"
        onClick={toggleAuthWindow}
      >
        <Image src={loginIcon} alt="Войти" width={25} height={25} />
      </button>
    </div>
  )
}
