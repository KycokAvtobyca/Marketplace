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
  isLoading: boolean
}

interface AuthWindowStore extends IActions, IInitialState {}

type AuthWindowStoreCreator = StateCreator<
  AuthWindowStore,
  [["zustand/immer", never], ["zustand/devtools", never]]
>

const initialState: IInitialState = {
  isOpen: false,
  isLoading: false,
}

const authWindowStore: AuthWindowStoreCreator = (set) => ({
  ...initialState,
  toggle: () => {
    set(
      (s) => {
        if (s.isOpen) {
          s.isOpen = false
        } else {
          s.isOpen = true
        }
      },
      false,
      "auth/authWindow_open",
    )
  },
  setIsOpen: (isOpen) => {
    genericSetAction(set, "isOpen", isOpen, "setIsOpen")
  },
})

export const useAuthWindowStore = create<AuthWindowStore>()(
  immer(devtools(authWindowStore)),
)

// interface AuthWindowState {
//   isOpen: boolean
//   isCodePage: boolean
//   isLoading: boolean

//   open: () => void
//   close: () => void
// }

// export const useAuthWindowStore = create<AuthWindowState>((set) => ({
//   isOpen: false,
//   isLoading: false,
//   isCodePage: false,

//   open: () => set({ isOpen: true }),
//   close: () => set({ isOpen: false }),
// }))
