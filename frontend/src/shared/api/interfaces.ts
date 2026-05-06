export interface DefaultErrorResponse {
  detail?:
    | {
        message?: string
      }
    | string
}

export interface DefaultApiAction {
  success: boolean
  data?: any
  error?: { data: DefaultErrorResponse }
}
