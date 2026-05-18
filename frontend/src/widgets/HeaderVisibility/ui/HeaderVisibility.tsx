"use client"

import clsx from "clsx"
import { ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react"

export const HeaderVisibility = ({ children }: { children: ReactNode }) => {
  const lastScrollY = useRef(0)
  const headerRef = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(true)

  useLayoutEffect(() => {
    const updateOffset = () => {
      const height = headerRef.current?.offsetHeight || 0
      const offset = isVisible ? height + 24 : 0
      document.documentElement.style.setProperty("--app-header-offset", `${offset}px`)
    }

    updateOffset()
    window.addEventListener("resize", updateOffset)
    return () => window.removeEventListener("resize", updateOffset)
  }, [isVisible])

  useEffect(() => {
    const onScroll = () => {
      const currentScrollY = window.scrollY
      const isNearTop = currentScrollY < 12
      const isScrollingDown = currentScrollY > lastScrollY.current

      setIsVisible(isNearTop || !isScrollingDown)
      lastScrollY.current = currentScrollY
    }

    lastScrollY.current = window.scrollY
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  return (
    <div
      ref={headerRef}
      className={clsx(
        "fixed left-1/2 top-3 z-[35] w-[calc(100%-1rem)] max-w-5xl -translate-x-1/2 transition-transform duration-200 ease-out sm:w-[calc(100%-1.5rem)]",
        isVisible
          ? "translate-y-0"
          : "-translate-y-[calc(100%+1rem)]",
      )}
    >
      {children}
    </div>
  )
}
