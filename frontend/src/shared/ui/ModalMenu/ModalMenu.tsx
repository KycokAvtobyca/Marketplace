import { ReactNode } from "react"

interface ModalMenuProps {
  className: string
  children: ReactNode
}

export const ModalMenu: React.FC<ModalMenuProps> = ({
  className,
  children,
}) => {
  return (
    <div className={`modal-menu ${className} w-full h-full`}>
      <h3>Модальное окно меню</h3>
      {children}
    </div>
  )
}
