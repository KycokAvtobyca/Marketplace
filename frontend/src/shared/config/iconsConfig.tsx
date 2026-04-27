import Close from "@/shared/assets/icons/close-brand.svg"
import ArrowRight from "@/shared/assets/icons/arrow-right-brand.svg"
import User from "@/shared/assets/icons/user-brand.svg"
import Search from "@/shared/assets/icons/search-white.svg"
import Auth from "@/shared/assets/icons/login-brand.svg"
import HamburgerMenu from "@/shared/assets/icons/hamburger-menu-brand.svg"
import clsx from "clsx"

export const ICON_REGISTRY = {
  ARROWRIGHT: ArrowRight,
  ARROWLEFT: (props: any) => (
    <ArrowRight {...props} className={clsx(props?.className, "rotate-180")} />
  ),
  USER: User,
  AUTH: Auth,
  CLOSE: Close,
  SEARCH: Search,
  HAMBURGERMENU: HamburgerMenu,
}

export const ICON_SIZES = {
  ARROWRIGHT: {
    width: 20,
    height: 20,
    viewBox: 38,
  },
  ARROWLEFT: { width: 20, height: 20, viewBox: 38 },
  USER: {
    width: 30,
    height: 30,
    viewBox: 22,
  },
  AUTH: {
    width: 30,
    height: 30,
    viewBox: 24,
  },
  CLOSE: {
    width: 20,
    height: 20,
    viewBox: 24,
  },
  SEARCH: {
    width: 30,
    height: 30,
    viewBox: 24,
  },
  HAMBURGERMENU: {
    width: 40,
    height: 40,
    viewBox: 24,
  },
} as const

export type IconName = keyof typeof ICON_REGISTRY
