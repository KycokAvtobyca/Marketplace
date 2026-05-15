"use client"

import { useAuthWindowStore } from "@/entities/authWindow/"
import { Popover } from "@/shared/ui/Popover"
import { Icon } from "@/shared/ui/Icons/Icon"
import { useRef, useState } from "react"
import Link from "next/link"
import dynamic from "next/dynamic"
import styles from "./UserButton.module.scss"
import { useProfile } from "@/entities/user/api/useProfile"
import { useLogout } from "@/entities/auth/api/useLogout"
import { useAuthStore } from "@/entities/auth"

export const UserButtonBase = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const toggleAuthWindow = useAuthWindowStore((s) => s.toggle)
  const buttonRef = useRef<HTMLButtonElement>(null)

  const { data: profile, isError } = useProfile()
  const { mutate: logout, isPending: isLoggingOut } = useLogout()
  const authStoreIsAuth = useAuthStore((s) => s.isAuth)

  // isAuth определяем по профилю ИЛИ по стору авторизации,
  // чтобы интерфейс сразу реагировал на вход
  const isAuth = (!!profile && !isError) || authStoreIsAuth

  const handleLogout = () => {
    logout()
    setIsMenuOpen(false)
  }

  return (
    <div className="flex items-center gap-4 shrink-0 pl-1">
      {isAuth ? (
        <>
          <button
            className="cursor-pointer"
            ref={buttonRef}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <Icon.USER />
          </button>

          <Popover
            anchorRef={buttonRef}
            isOpen={isMenuOpen}
            onClose={() => setIsMenuOpen(false)}
          >
            <div className={styles.divP}>
              <Link href="/profile">
                <p>Личный кабинет</p>
              </Link>
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="w-full text-left text-red-500 hover:opacity-70 transition-opacity disabled:opacity-50"
              >
                {isLoggingOut ? "Выход..." : "Выйти"}
              </button>
            </div>
          </Popover>
        </>
      ) : (
        <button className="rounded-l cursor-pointer" onClick={toggleAuthWindow}>
          <Icon.AUTH />
        </button>
      )}
    </div>
  )
}

export const UserButton = dynamic(() => Promise.resolve(UserButtonBase), {
  ssr: false,
  loading: () => (
    <div
      style={{ width: Icon.USER.width, height: Icon.USER.height }}
      className="animate-shimmer p-1 rounded-full"
    />
  ),
})
