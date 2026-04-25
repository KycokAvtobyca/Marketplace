"use client"

import { useAuthStore } from "@/entities/auth/model/store"
import { useAuthWindowStore } from "@/entities/authWindow/"
import { Popover } from "@/shared/ui/Popover"
import { Icon } from "@/shared/ui/Icons/Icon"
import { useRef, useState } from "react"
import { useShallow } from "zustand/shallow"
import Link from "next/link"
import dynamic from "next/dynamic"
import { ROUTES } from "@/shared/config/routes"
import styles from "./UserButton.module.scss"

export const UserButtonBase = () => {
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
            <Icon.USER />
          </button>

          <Popover
            anchorRef={buttonRef}
            isOpen={isMenuOpen}
            onClose={() => setIsMenuOpen(false)}
          >
            <div className={styles.divP}>
              <Link href={ROUTES.PROFILE}>
                <p>Личный кабинет</p>
              </Link>
              <Link href={ROUTES.ORDERS}>
                <p>Заказы</p>
              </Link>
              <Link href={ROUTES.EXIT}>
                <p>Выйти</p>
              </Link>
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
