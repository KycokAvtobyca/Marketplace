import Close from "@/shared/assets/icons/close-brand.svg"
import ArrowRight from "@/shared/assets/icons/arrow-right-brand.svg"
import User from "@/shared/assets/icons/user-brand.svg"
import Search from "@/shared/assets/icons/search-white.svg"
import Auth from "@/shared/assets/icons/login-brand.svg"
import HamburgerMenu from "@/shared/assets/icons/hamburger-menu-brand.svg"
import ArrowDownWithoutLine from "@/shared/assets/icons/arrow-without-line-down-brand.svg"
import clsx from "clsx"

export const ICON_REGISTRY = {
  ARROWRIGHT: ArrowRight,
  ARROWLEFT: (props: any) => (
    <ArrowRight {...props} className={clsx(props?.className, "rotate-180")} />
  ),
  ARROWDOWN: ArrowDownWithoutLine,
  ARROWUP: (props: any) => (
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
} as const

export type IconName = keyof typeof ICON_REGISTRY
