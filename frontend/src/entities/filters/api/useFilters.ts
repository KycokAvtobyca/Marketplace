import { useMutation } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { isAxiosError } from "axios"
import { ROUTES } from "@/shared/config"

export const useFilters = () => {
  return useMutation({
    mutationFn: async () => {},
  })
}
