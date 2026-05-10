import { DefaultErrorResponse, DefaultApiAction } from "@/shared/api"

export interface RequestAuthData {
  phone_number?: string | [string]
  sms_code?: string | [string]
  code?: string | [string]
}

export interface ErrorResponseAuthFormData extends RequestAuthData {}

export interface ErrorResponseAuthData
  extends ErrorResponseAuthFormData, DefaultErrorResponse {
  detail?: {
    message?: string
    seconds_left?: string
  }
}

export interface AuthApiAction extends DefaultApiAction<undefined> {
  success: boolean
  error?: { data: ErrorResponseAuthData }
}
