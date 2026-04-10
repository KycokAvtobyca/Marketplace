import { create } from "zustand"

interface AuthWindowState {
  isOpen: boolean
  toggle: () => void
}

export const useAuthStore = create<AuthWindowState>((set) => ({
  isOpen: false,
  toggle: () => set((state) => ({ isOpen: !state.isOpen })),
}))
