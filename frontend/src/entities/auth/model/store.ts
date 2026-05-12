import { create, StateCreator } from "zustand"
import { createJSONStorage, devtools, persist } from "zustand/middleware"
import { immer } from "zustand/middleware/immer"
import { genericSetAction } from "@/shared/lib/zustand"

interface IActions {
  setIsAuth: (status: boolean) => void
  setIsCodeSent: (status: boolean) => void
}

interface IInitialState {
  isAuth: boolean
  isCodeSent: boolean
}

interface AuthStore extends IActions, IInitialState {}

type AuthStoreCreator = StateCreator<
  AuthStore,
  [
    ["zustand/immer", never],
    ["zustand/devtools", never],
    ["zustand/persist", unknown],
  ]
>

const initialState: IInitialState = {
  isAuth: false,
  isCodeSent: false,
}

const authStore: AuthStoreCreator = (set) => ({
  ...initialState,
  setIsAuth: (status) => {
    genericSetAction(set, "isAuth", status, "auth/setIsAuth")
  },
  setIsCodeSent: (status) => {
    genericSetAction(set, "isCodeSent", status, "auth/setIsCodeSent")
  },
})

export const useAuthStore = create<AuthStore>()(
  immer(
    devtools(
      persist(authStore, {
        name: "auth-storage",
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({ isCodeSent: state.isCodeSent }),
        onRehydrateStorage: () => (state) => {
          if (state) {
            state.isAuth = false
          }
        },
      }),
    ),
  ),
)
