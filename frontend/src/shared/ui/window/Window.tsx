import React from "react"
import { BackRedirectLine } from "../backRedirectLine/BackRedirectLine"
import styles from "./Window.module.scss"

export interface WindowProps {
  as?: "section" | "article"
  children?: React.ReactNode
  className?: string
  title?: React.ReactNode
  subtitle?: React.ReactNode
  ariaLabel?: string
}

export const Window: React.FC<WindowProps> = ({
  as = "section",
  children,
  className,
  title,
  subtitle,
  ariaLabel,
}) => {
  const Element = as

  return (
    <Element className={`${styles.window} ${className}`} aria-label={ariaLabel}>
      <div className="flex flex-col gap-2">
        <BackRedirectLine />
        {title && (
          <header>
            <h1 className="text-2xl">{title}</h1>
            {subtitle && <p className="text-xs opacity-50">{subtitle}</p>}
          </header>
        )}

        <div>{children}</div>
      </div>
    </Element>
  )
}
