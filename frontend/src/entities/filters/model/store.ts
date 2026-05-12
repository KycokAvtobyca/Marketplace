import { genericSetAction } from "@/shared/lib/zustand"
import { create, StateCreator } from "zustand"
import { devtools } from "zustand/middleware"
import { immer } from "zustand/middleware/immer"

// Тип для хранения выбранных фильтров
// Пример: { brands: ['nike', 'adidas'], category: ['obuv'] }
type FilterValue = string | number

interface IActions {
  toggleFilterModalMenu: () => void
  setIsFilterModalMenu: (isFilterModalMenu: boolean) => void
  toggleFilter: (filterId: string) => void
  resetFilters: () => void
  setAppliedQueryString: (query: string) => void
}

interface IInitialState {
  isFilterModalMenu: boolean
  selectedFilters: FilterValue[]
  appliedQueryString: string
}

interface FilterModalMenuStore extends IActions, IInitialState {}

type FilterModalMenuStoreCreator = StateCreator<
  FilterModalMenuStore,
  [["zustand/immer", never], ["zustand/devtools", never]]
>

const initialState: IInitialState = {
  isFilterModalMenu: false,
  selectedFilters: [],
  appliedQueryString: "",
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
  toggleFilter: (filterId) => {
    set(
      (state) => {
        const index = state.selectedFilters.indexOf(filterId)
        if (index === -1) {
          state.selectedFilters.push(filterId) // Если нет - добавляем
        } else {
          state.selectedFilters.splice(index, 1) // Если есть - удаляем
        }
      },
      false,
      "filterMenuModal/toggleFilter",
    )
  },
  setAppliedQueryString: (query) => {
    set(
      (s) => {
        s.appliedQueryString = query
      },
      false,
      "filter/setAppliedQuery",
    )
  },
  resetFilters: () => {
    set(
      (state) => {
        state.selectedFilters = []
        state.appliedQueryString = ""
      },
      false,
      "filterMenuModal/resetFilters",
    )
  },
})

export const useFilterModalMenuStore = create<FilterModalMenuStore>()(
  immer(devtools(filterModalMenuStore)),
)
