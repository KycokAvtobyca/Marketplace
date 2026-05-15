import { ICON_REGISTRY, ICON_SIZES } from "@/shared/config"
import { IconBase, IconProps } from "./"
import type { FC } from "react"

type StaticIconComponent = FC<
  Omit<IconProps, "name" | "width" | "height">
> & {
  width: string
  height: string
}

type IconComponent = typeof IconBase & {
  [K in keyof typeof ICON_REGISTRY]: StaticIconComponent
}

export const Icon = IconBase as IconComponent

Object.keys(ICON_REGISTRY).forEach((key) => {
  const name = key as keyof typeof ICON_REGISTRY
  const sizes = ICON_SIZES[name]
  const widthRem = `${sizes.width / 16}rem`
  const heightRem = `${sizes.height / 16}rem`

  const Component: StaticIconComponent = Object.assign(
    (props: Omit<IconProps, "name" | "width" | "height">) => (
      <IconBase name={name} width={widthRem} height={heightRem} {...props} />
    ),
    { width: widthRem, height: heightRem },
  )

  Icon[name] = Component
})
