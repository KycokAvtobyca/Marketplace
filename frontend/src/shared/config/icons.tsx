import Close from "@/shared/assets/icons/close-brand.svg"
import ArrowRight from "@/shared/assets/icons/arrow-right-brand.svg"
import User from "@/shared/assets/icons/user-brand.svg"
import Search from "@/shared/assets/icons/search-white.svg"
import Auth from "@/shared/assets/icons/login-brand.svg"
import HamburgerMenu from "@/shared/assets/icons/hamburger-menu-brand.svg"
import ArrowDownWithoutLine from "@/shared/assets/icons/arrow-without-line-down-brand.svg"
import HeartBrand from "@/shared/assets/icons/heart-brand.svg"
import HeartGray from "@/shared/assets/icons/heart-gray.svg"
import Cart from "@/shared/assets/icons/cart-brand.svg"
import Trash from "@/shared/assets/icons/trash-brand.svg"
import clsx from "clsx"
import type { ComponentProps } from "react"

type ArrowRightProps = ComponentProps<typeof ArrowRight>
type ArrowDownProps = ComponentProps<typeof ArrowDownWithoutLine>

export const ICON_REGISTRY = {
  ARROWRIGHT: ArrowRight,
  ARROWLEFT: (props: ArrowRightProps) => (
    <ArrowRight {...props} className={clsx(props?.className, "rotate-180")} />
  ),
  ARROWDOWN: ArrowDownWithoutLine,
  ARROWUP: (props: ArrowDownProps) => (
    <ArrowDownWithoutLine
      {...props}
      className={clsx(props?.className, "rotate-180")}
    />
  ),
  USER: User,
  AUTH: Auth,
  CLOSE: Close,
  SEARCH: Search,
  HAMBURGERMENU: HamburgerMenu,
  HEARTBRAND: HeartBrand,
  HEARTGRAY: HeartGray,
  CART: Cart,
  TRASH: Trash,
}

const setSize = (width: number, height: number, viewBox: number) => {
  return {
    width,
    height,
    viewBox,
  }
}

export const ICON_SIZES = {
  ARROWRIGHT: setSize(20, 20, 38),
  ARROWLEFT: setSize(20, 20, 38),
  ARROWDOWN: setSize(30, 30, 32),
  ARROWUP: setSize(30, 30, 32),
  USER: setSize(30, 30, 32),
  AUTH: setSize(30, 30, 24),
  CLOSE: setSize(20, 20, 24),
  SEARCH: setSize(30, 30, 24),
  HAMBURGERMENU: setSize(40, 40, 24),
  HEARTBRAND: setSize(30, 30, 24),
  HEARTGRAY: setSize(30, 30, 24),
  CART: setSize(30, 30, 24),
  TRASH: setSize(30, 30, 24),
} as const

export type IconName = keyof typeof ICON_REGISTRY
