import { useMutation } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export interface PhoneChangePayload {
  action: "send_old" | "verify_old" | "send_new" | "verify_new"
  new_phone?: string
  code?: string
}

export const usePhoneChange = () => {
  return useMutation({
    mutationFn: async (payload: PhoneChangePayload) => {
      const { data } = await api.post(ROUTES.PHONE_CHANGE, payload)
      return data
    },
  })
}
