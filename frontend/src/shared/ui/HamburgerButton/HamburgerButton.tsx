import { Icon } from "@/shared/ui/Icons"

interface HamburgerButtonProps {
  className?: string
  onClick?: () => void
}

export const HamburgerButton: React.FC<HamburgerButtonProps> = ({
  className,
  onClick,
}) => {
  return (
    <button
      type="button"
      className={`cursor-pointer ${className ?? ""}`}
      onClick={onClick}
    >
      <Icon.HAMBURGERMENU />
    </button>
  )
}
