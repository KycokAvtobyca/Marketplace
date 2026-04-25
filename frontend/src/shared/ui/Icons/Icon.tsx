import { ICON_REGISTRY, ICON_SIZES } from "@/shared/config"
import { IconBase, IconProps } from "./"

type IconComponent = typeof IconBase & {
  [K in keyof typeof ICON_REGISTRY]: React.FC<
    Omit<IconProps, "name" | "width" | "height">
  > & {
    readonly width: string
    readonly height: string
  }
}

export const Icon = IconBase as IconComponent

Object.keys(ICON_REGISTRY).forEach((key) => {
  const name = key as keyof typeof ICON_REGISTRY
  const sizes = ICON_SIZES[name]
  const widthRem = `${sizes.width / 16}rem`
  const heightRem = `${sizes.height / 16}rem`

  const Component = (props: Omit<IconProps, "name" | "width" | "height">) => (
    <IconBase name={name} width={widthRem} height={heightRem} {...props} />
  )

  Component.width = widthRem
  Component.height = heightRem

  Icon[name] = Component as any
})
