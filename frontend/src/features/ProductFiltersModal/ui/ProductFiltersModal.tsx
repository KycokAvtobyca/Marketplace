"use client"

import { FilterSidebar } from "@/widgets/FilterSidebar"
import { useFilterModalMenuStore } from "@/entities/filterMenuModal"
import { HamburgerMenuButton } from "@/shared/ui/HamburgerMenuButton"
import { useMountTransition } from "@/shared/lib/hooks"
import clsx from "clsx"
import { createPortal } from "react-dom"
import { useEffect, useState } from "react"

interface ProductFiltersModalProps {
  transitionDuration: number
}

export const ProductFiltersModal: React.FC<ProductFiltersModalProps> = ({
  transitionDuration = 300,
}) => {
  const { isFilterModalMenu, toggleFilterModalMenu } = useFilterModalMenuStore()
  const { shouldRender, isVisible } = useMountTransition({
    isOpen: isFilterModalMenu,
    transitionDuration,
  })

  // Состояние для проверки, находимся ли мы на клиенте
  const [mounted, setMounted] = useState(false)

  // useEffect срабатывает только в браузере
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <HamburgerMenuButton onClick={toggleFilterModalMenu} />
  }

  // Теперь мы точно в браузере, и document существует
  const portalRoot = document.getElementById("modals")

  return (
    <>
      <HamburgerMenuButton onClick={toggleFilterModalMenu} />
      {shouldRender &&
        portalRoot &&
        createPortal(
          <FilterSidebar
            className={clsx(
              "fixed inset-0 bg-default w-dvw h-dvh transition-opacity duration-300 z-30",
              isVisible
                ? "opacity-100 pointer-events-auto"
                : "opacity-0 pointer-events-none",
            )}
          />,
          portalRoot,
        )}
    </>
  )
}
