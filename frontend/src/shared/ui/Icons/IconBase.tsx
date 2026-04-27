import { ICON_REGISTRY, IconName } from "@/shared/config"
import clsx from "clsx"

export interface IconProps {
  name: IconName
  className?: string
  color?: string
  ariaHidden?: boolean
  width: string
  height: string
}

export const IconBase = ({
  name,
  className,
  ariaHidden,
  width,
  height,
}: IconProps) => {
  const SvgIcon = ICON_REGISTRY[name]

  return (
    <SvgIcon
      width={width}
      height={height}
      className={clsx("object-contain", className)}
      aria-hidden={ariaHidden}
    />
  )
}
