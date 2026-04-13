import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config/routes"
import { create } from "zustand"

interface UserState {
  isLoggedIn: boolean
  isLoading: boolean
  setIsLoggedIn: (status: boolean) => void
  checkAuthInit: () => void
}

export const useUserStore = create<UserState>((set) => ({
  isLoggedIn: false,
  isLoading: true,
  setIsLoggedIn: (status) => set({ isLoggedIn: status }),
  checkAuthInit: async () => {
    try {
      const response = await api.get(ROUTES.PROFILE)

      if (response.status === 200) {
        set({ isLoggedIn: true, isLoading: false })
      }
    } catch (error) {
      set({ isLoggedIn: false, isLoading: false })
    }
  },
}))
