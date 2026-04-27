import { genericSetAction } from "@/shared/lib/zustand"
import { create, StateCreator } from "zustand"
import { devtools } from "zustand/middleware"
import { immer } from "zustand/middleware/immer"

interface IActions {
  toggleFilterModalMenu: () => void
  setIsFilterModalMenu: (isFilterModalMenu: boolean) => void
}

interface IInitialState {
  isFilterModalMenu: boolean
  isLoading: boolean
}

interface FilterModalMenuStore extends IActions, IInitialState {}

type FilterModalMenuStoreCreator = StateCreator<
  FilterModalMenuStore,
  [["zustand/immer", never], ["zustand/devtools", never]]
>

const initialState: IInitialState = {
  isFilterModalMenu: false,
  isLoading: false,
}

const filterModalMenuStore: FilterModalMenuStoreCreator = (set) => ({
  ...initialState,
  toggleFilterModalMenu: () => {
    set(
      (s) => {
        s.isFilterModalMenu = !s.isFilterModalMenu
      },
      false,
      "filterMenuModal/toggle",
    )
  },
  setIsFilterModalMenu: (isFilterModalMenu) => {
    genericSetAction(
      set,
      "isFilterModalMenu",
      isFilterModalMenu,
      "filterMenuModal/setIsFilterModalMenu",
    )
  },
})

export const useFilterModalMenuStore = create<FilterModalMenuStore>()(
  immer(devtools(filterModalMenuStore)),
)
