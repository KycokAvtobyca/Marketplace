import React from "react"
import styles from "./Window.module.scss"
import { Overlay } from "./Overlay"
import { clsx } from "clsx"

export interface WindowProps {
  as?: "section" | "article"
  children?: React.ReactNode
  className?: string
  title?: React.ReactNode
  subtitle?: React.ReactNode
  ariaLabel?: string
  isOpen?: boolean
  toggleWindow?: () => void
  backRedirect?: React.ReactNode
}

export const Window: React.FC<WindowProps> = ({
  as = "section",
  children,
  className,
  title,
  subtitle,
  ariaLabel,
  isOpen,
  toggleWindow,
  backRedirect,
}) => {
  const Element = as

  return (
    <div
      className={clsx(
        "transition-all duration-300",
        isOpen
          ? "visible opacity-100"
          : "invisible scale opacity-0 absolute pointer-events-none",
      )}
    >
      <Element
        className={clsx(styles.window, className)}
        aria-label={ariaLabel}
      >
        {backRedirect}
        <div className="flex flex-col gap-2 justify-start w-full">
          {title && (
            <header>
              <h1 className="text-xl">{title}</h1>
              {subtitle && <p className="text-xs opacity-50">{subtitle}</p>}
            </header>
          )}
          <div className="mt-4 w-full">{children}</div>
        </div>
      </Element>
      <Overlay toggleWindow={toggleWindow} />
    </div>
  )
}
