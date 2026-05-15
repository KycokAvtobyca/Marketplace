import { DefaultErrorResponse, DefaultApiAction } from "@/shared/api"

export interface RequestAuthData {
  phone_number?: string | [string]
  sms_code?: string | [string]
  code?: string | [string]
  password?: string
}

export type ErrorResponseAuthFormData = RequestAuthData

export interface ErrorResponseAuthData
  extends ErrorResponseAuthFormData, DefaultErrorResponse {
  detail?: {
    message?: string
    seconds_left?: string
    code?: string
  }
  non_field_errors?: string[]
}

export interface AuthApiAction extends DefaultApiAction<undefined> {
  success: boolean
  requiresPassword?: boolean
  error?: { data: ErrorResponseAuthData }
}
