import Close from "@/shared/assets/icons/close-brand.svg"
import ArrowRight from "@/shared/assets/icons/arrow-right-brand.svg"
import User from "@/shared/assets/icons/user-brand.svg"
import Search from "@/shared/assets/icons/search-white.svg"
import Auth from "@/shared/assets/icons/login-brand.svg"
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
}

export const ICON_SIZES = {
  ARROWRIGHT: {
    width: 20,
    height: 20,
  },
  ARROWLEFT: { width: 20, height: 20 },
  USER: {
    width: 30,
    height: 30,
  },
  AUTH: {
    width: 30,
    height: 30,
  },
  CLOSE: {
    width: 20,
    height: 23,
  },
  SEARCH: {
    width: 30,
    height: 30,
  },
} as const

export type IconName = keyof typeof ICON_REGISTRY
