import { ReactNode } from "react"
import { useMountTransition } from "@/shared/lib/hooks"
import clsx from "clsx"
import { createPortal } from "react-dom"
import { useEffect, useState } from "react"
import { Icon } from "@/shared/ui/Icons"

interface ModalMenuProps {
  isOpen: boolean
  toggleModalMenu: () => void
  children: ReactNode
  className?: string
  transitionDuration?: number
}

export const ModalMenu: React.FC<ModalMenuProps> = ({
  className,
  transitionDuration = 300,
  isOpen,
  toggleModalMenu,
  children,
}) => {
  const { shouldRender, isVisible } = useMountTransition({
    isOpen: isOpen,
    transitionDuration,
  })

  // Состояние для проверки, находимся ли мы на клиенте
  const [mounted, setMounted] = useState(false)

  // useEffect срабатывает только в браузере
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return
  }

  // Теперь мы точно в браузере, и document существует
  const portalRoot = document.getElementById("modals")

  return (
    <>
      {shouldRender &&
        portalRoot &&
        createPortal(
          <div
            className={clsx(
              `${className ?? ""} fixed inset-0 px-2 py-3 bg-default w-dvw h-dvh transition-opacity duration-300 z-30`,
              isVisible
                ? "opacity-100 pointer-events-auto"
                : "opacity-0 pointer-events-none",
            )}
          >
            <div className="w-full flex">
              <button
                onClick={toggleModalMenu}
                className="ml-auto cursor-pointer"
              >
                <Icon.CLOSE />
              </button>
            </div>
            {children}
          </div>,
          portalRoot,
        )}
    </>
  )
}
