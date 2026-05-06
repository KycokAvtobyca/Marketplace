"use client"

import { useFilterModalMenuStore } from "@/entities/filterMenuModal"
import { HamburgerButton } from "@/shared/ui/HamburgerButton"
import { ModalMenu } from "@/shared/ui/ModalMenu"
import { CheckBox } from "@/shared/ui/CheckBox"
import {
  useCategories,
  useProductTypes,
  useMetaAttrs,
} from "@/entities/filters/"
import { useEffect } from "react"
import { FilterGroupList } from "./FilterGroupList"

interface FilterModalMenuProps {
  classNameHamburgerButton?: string
  classNameModalMenu?: string
}

export const FilterModalMenu: React.FC<FilterModalMenuProps> = ({
  classNameHamburgerButton,
  classNameModalMenu,
}) => {
  const { isFilterModalMenu, toggleFilterModalMenu } = useFilterModalMenuStore()
  // const { mutateAsync: mutateAsyncCategories } = useCategories()

  // useEffect(() => {
  //   const fetchData = async () => {
  //     const result = await mutateAsyncCategories({
  //       cursor: "cj0xJnA9MQ==",
  //     })
  //     console.log(result)
  //   }

  //   fetchData()
  // }, [])

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
        <FilterGroupList />
        {/* <div>
          <h3>Фильтры</h3>
          <CheckBox>
            <span>Розы</span>
          </CheckBox>
        </div> */}
      </ModalMenu>
    </>
  )
}
