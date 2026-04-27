import React, { useEffect, useState } from "react"
import styles from "./Window.module.scss"
import { Overlay } from "./Overlay"
import { clsx } from "clsx"
import { useMountTransition } from "@/shared/lib/hooks"

export interface WindowProps {
  wayAs?: "section" | "article"
  children?: React.ReactNode
  className?: string
  title?: React.ReactNode
  subtitle?: React.ReactNode
  ariaLabel?: string
  isOpen?: boolean
  toggleWindow?: () => void
  backRedirect?: React.ReactNode
  transitionDuration?: number
}

export const Window: React.FC<WindowProps> = ({
  wayAs = "section",
  children,
  className,
  title,
  subtitle,
  ariaLabel,
  isOpen,
  toggleWindow,
  backRedirect,
  transitionDuration = 300,
}) => {
  const Element = wayAs
  const { isVisible, shouldRender } = useMountTransition({
    isOpen: !!isOpen,
    transitionDuration,
  })

  if (!shouldRender) return

  return (
    <div
      className={clsx(
        "transition-all",
        isVisible
          ? "visible opacity-100"
          : "invisible opacity-0 absolute pointer-events-none",
      )}
      style={{ transitionDuration: `${transitionDuration}ms` }}
    >
      <Element
        className={clsx(styles.window, className)}
        aria-label={ariaLabel}
      >
        {backRedirect}
        <div className="flex flex-col gap-2 justify-start w-full">
          {title && (
            <header>
              <h3 className="text-xl">{title}</h3>
              {subtitle && <p className="text-xs opacity-50">{subtitle}</p>}
            </header>
          )}
          <div className="mt-3 w-full">{children}</div>
        </div>
      </Element>
      <Overlay toggleWindow={toggleWindow} />
    </div>
  )
}
