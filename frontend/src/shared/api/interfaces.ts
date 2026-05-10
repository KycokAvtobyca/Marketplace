export interface DefaultErrorResponse {
  message?: string
  detail?:
    | {
        message?: string
      }
    | string
}

export interface DefaultApiAction<T> {
  success: boolean
  data?: T
  error?: { data: DefaultErrorResponse }
}
