import { genericSetAction } from "@/shared/lib/zustand"
import { create, StateCreator } from "zustand"
import { devtools } from "zustand/middleware"
import { immer } from "zustand/middleware/immer"

interface IActions {
  toggle: () => void
  setIsOpen: (isOpen: boolean) => void
}

interface IInitialState {
  isOpen: boolean
}

interface AuthWindowStore extends IActions, IInitialState {}

type AuthWindowStoreCreator = StateCreator<
  AuthWindowStore,
  [["zustand/immer", never], ["zustand/devtools", never]]
>

const initialState: IInitialState = {
  isOpen: false,
}

const authWindowStore: AuthWindowStoreCreator = (set) => ({
  ...initialState,
  toggle: () => {
    set(
      (s) => {
        s.isOpen = !s.isOpen
      },
      false,
      "authWindow/toggle",
    )
  },
  setIsOpen: (isOpen) => {
    genericSetAction(set, "isOpen", isOpen, "authWindow/setIsOpen")
  },
})

export const useAuthWindowStore = create<AuthWindowStore>()(
  immer(devtools(authWindowStore)),
)
