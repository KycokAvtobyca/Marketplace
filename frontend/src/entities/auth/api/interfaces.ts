export interface RequestAuthData {
  phone_number?: string | [string]
  sms_code?: string | [string]
  code?: string | [string]
}

export interface ErrorResponseAuthFormData extends RequestAuthData {}

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
