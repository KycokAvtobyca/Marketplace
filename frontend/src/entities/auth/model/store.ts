import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config/routes"
import axios, { AxiosResponse } from "axios"
import { create, StateCreator } from "zustand"
import { createJSONStorage, devtools, persist } from "zustand/middleware"
import { immer } from "zustand/middleware/immer"
import { genericSetAction } from "@/shared/lib/zustand"

interface RequestAuthData {
  phone_number?: string | [string]
  sms_code?: string | [string]
  code?: string | [string]
}

interface ErrorResponseAuthFormData extends RequestAuthData {}

export interface ErrorResponseAuthData extends ErrorResponseAuthFormData {
  detail?: {
    message?: string
    seconds_left?: string
  }
}

export interface ApiAction {
  success: boolean
  error?: { data: ErrorResponseAuthData }
}

interface IActions {
  // setAction: (
  //   stateObj: string,
  //   newValue: IInitialState[keyof IInitialState],
  //   action?: string | undefined,
  //   shouldReplace?: false | undefined,
  // ) => void
  setIsAuth: (status: boolean) => void
  setIsCodeSent: (status: boolean) => void
  setIsLoading: (status: boolean) => void

  checkAuth: (phone: string) => Promise<void>
  sendSms: (phone: string) => Promise<ApiAction>
  auth: (phone: string, code: string) => Promise<ApiAction>
}

interface IInitialState {
  isAuth: boolean
  isCodeSent: boolean

  isLoading: boolean
}

interface AuthStore extends IActions, IInitialState {}

const initialState: IInitialState = {
  isAuth: false,
  isCodeSent: false,
  isLoading: false,
}

type AuthStoreCreator = StateCreator<
  AuthStore,
  [
    ["zustand/immer", never],
    ["zustand/devtools", never],
    ["zustand/persist", unknown],
  ]
>

const authStore: AuthStoreCreator = (set, get) => ({
  ...initialState,
  // Инициализация стандартного action
  // setAction: (stateObj, newValue, action, shouldReplace) => {
  //   set(
  //     (state) => {
  //       if (!(stateObj in state))
  //         throw new Error(`В useAuthStore не найден ${stateObj}`)

  //       if (state[stateObj] !== newValue) state[stateObj] = newValue
  //     },
  //     shouldReplace,
  //     action,
  //   )
  // },

  setIsLoading: (status) => {
    genericSetAction(set, "isLoading", status, "auth/setIsLoading")
  },
  setIsAuth: (status) => {
    genericSetAction(set, "isAuth", status, "auth/setIsAuth")
  },
  setIsCodeSent: (status) => {
    genericSetAction(set, "isCodeSent", status, "auth/setIsCodeSent")
  },

  checkAuth: async (phone) => {},
  sendSms: async (phone) => {
    // get().setIsLoading(true)
    // get().setErrorMessage(undefined)

    set(
      (s) => {
        s.isLoading = true
      },
      false,
      "auth/sendSms_start",
    )

    try {
      await api.post<
        ErrorResponseAuthData,
        AxiosResponse<ErrorResponseAuthData>,
        RequestAuthData
      >(ROUTES.AUTH_SEND_SMS, {
        phone_number: phone.startsWith("+7") ? phone : `+7${phone}`,
      })

      // get().setIsLoading(false)
      // get().setIsCodeSent(true)
      set(
        (s) => {
          s.isLoading = false
          s.isCodeSent = true
        },
        false,
        "auth/sendSms_success",
      )

      return { success: true }
    } catch (e: unknown) {
      const defaultErrorMessage = "Ошибка при попытке отправить смс-код"
      if (axios.isAxiosError<ErrorResponseAuthData>(e)) {
        const eResponse = e.response?.data

        console.error("autherror", e.response)

        // get().setIsLoading(false)
        // get().setErrorMessage(serverMessage || defaultErrorMessage)
        // get().setCooldownUntil(futureTimestamp)
        // get().setErrorCode(e.code)

        const parsedError: ApiAction["error"] = {
          data: {
            phone_number: eResponse?.phone_number,
            sms_code: eResponse?.sms_code,
            detail: eResponse?.detail,
          },
        }

        set(
          (s) => {
            s.isLoading = false
          },
          false,
          "auth/sendSms_error",
        )

        return { success: false, error: parsedError }
      } else {
        // get().setIsLoading(false)
        // get().setErrorMessage(defaultErrorMessage)
        // get().setCooldownUntil(Date.now() + 60000)

        set(
          (s) => {
            s.isLoading = false
          },
          false,
          "auth/sendSms_error",
        )

        return {
          success: false,
          error: {
            data: {
              detail: {
                message: defaultErrorMessage,
                seconds_left: "60",
              },
            },
          },
        }
      }
    }
  },

  auth: async (phone, code) => {
    set(
      (s) => {
        s.isLoading = true
      },
      false,
      "auth/auth_start",
    )

    // get().setIsLoading(true)

    try {
      const response = await api.post<
        ErrorResponseAuthData,
        AxiosResponse<ErrorResponseAuthData>,
        RequestAuthData
      >(ROUTES.AUTH_TOKEN, {
        phone_number: phone.startsWith("+7") ? phone : `+7${phone}`,
        sms_code: code,
      })

      console.log(response)

      set(
        (s) => {
          s.isLoading = false
          s.isAuth = true
        },
        false,
        "auth/auth_success",
      )

      return { success: true }
    } catch (e: unknown) {
      const defaultErrorMessage = "Ошибка при попытке входа"
      if (axios.isAxiosError(e)) {
        const eData = e.response?.data
        const parsedError: ApiAction["error"] = {
          data: {
            phone_number: eData?.phone_number,
            sms_code: eData?.code ?? eData?.sms_code,
            detail: eData?.detail,
          },
        }

        console.error("autherror", e.response)

        set(
          (s) => {
            s.isLoading = false
          },
          false,
          "auth/auth_error",
        )

        return { success: false, error: parsedError }
      } else {
        console.error("Ошибка22", e)
        set(
          (s) => {
            s.isLoading = false
          },
          false,
          "auth/auth_error",
        )

        return {
          success: false,
          error: {
            data: {
              detail: {
                message: defaultErrorMessage,
                seconds_left: "60",
              },
            },
          },
        }
      }
    }
  },
})

export const useAuthStore = create<AuthStore>()(
  immer(
    devtools(
      persist(authStore, {
        name: "auth-storage",
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({ isAuth: state.isAuth }),
      }),
    ),
  ),
)

// ----

// export interface User {
//   phone: string
//   name: string
//   lastName: string
//   // и т.д.
// }

// const userStore = (set, get) => ({
//   user
//   setUser: async (phone) => {}
// })
