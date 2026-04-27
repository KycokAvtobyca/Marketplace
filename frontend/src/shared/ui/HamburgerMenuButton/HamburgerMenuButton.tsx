import { Icon } from "@/shared/ui/Icons"

interface HamburgerMenuButtonProps {
  className?: string
  onClick?: () => void
}

export const HamburgerMenuButton: React.FC<HamburgerMenuButtonProps> = ({
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
