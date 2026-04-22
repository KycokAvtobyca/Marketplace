import Image from "next/image"
import close from "@/shared/assets/icons/close-brand.svg"
import arrowRight from "@/shared/assets/icons/arrow-right-brand.svg"
import user from "@/shared/assets/icons/user-brand.svg"
import search from "@/shared/assets/icons/search-white.svg"

export const CloseIcon = ({ className }: { className?: string }) => (
  <Image
    src={close}
    alt="Закрыть"
    width={30}
    height={33}
    priority
    className={`w-7.5 h-8 object-contain ${className}`}
  />
)

export const ArrowRightIcon = ({ className }: { className?: string }) => (
  <Image
    src={arrowRight}
    alt="К следующему шагу"
    width={30}
    height={30}
    priority
    className={`w-7.5 h-7.5 object-contain ${className}`}
  />
)

export const ArrowLeftIcon = ({ className }: { className?: string }) => (
  <Image
    src={arrowRight}
    alt="К прошлому шагу"
    width={30}
    height={30}
    priority
    className={`rotate-180 w-7.5 h-7.5 object-contain ${className}`}
  />
)

export const UserIcon = ({ className }: { className?: string }) => (
  <Image
    src={user}
    alt="Пользователь"
    width={30}
    height={30}
    priority
    className={`w-7.5 h-7.5 object-contain ${className}`}
  />
)

export const SearchIcon = ({ className }: { className?: string }) => (
  <Image
    src={search}
    alt="Поиск"
    width={30}
    height={30}
    priority
    className={`w-7.5 h-7.5 object-contain ${className}`}
  />
)
