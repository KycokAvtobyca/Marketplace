"use client"

import { useFilterModalMenuStore } from "@/entities/filterMenuModal"
import { HamburgerButton } from "@/shared/ui/HamburgerButton"
import { ModalMenu } from "@/shared/ui/ModalMenu"

interface FilterModalMenuProps {
  classNameHamburgerButton?: string
  classNameModalMenu?: string
}

export const FilterModalMenu: React.FC<FilterModalMenuProps> = ({
  classNameHamburgerButton,
  classNameModalMenu,
}) => {
  const { isFilterModalMenu, toggleFilterModalMenu } = useFilterModalMenuStore()

  return (
    <>
      <HamburgerButton
        className={classNameHamburgerButton}
        onClick={toggleFilterModalMenu}
      />
      <ModalMenu
        className={classNameModalMenu}
        isOpen={isFilterModalMenu}
        toggleModalMenu={toggleFilterModalMenu}
      >
        <div>
          <h3>Фильтры</h3>
        </div>
      </ModalMenu>
    </>
  )
}
