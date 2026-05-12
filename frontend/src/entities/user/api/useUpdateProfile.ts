import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export interface UpdateProfileData {
  name?: string
  last_name?: string
  middle_name?: string
  email?: string
  address?: string
  address_data?: Record<string, any>
}

export const useUpdateProfile = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: UpdateProfileData) => {
      const { data: response } = await api.patch(ROUTES.PROFILE.ROOT, data)
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] })
    },
  })
}
