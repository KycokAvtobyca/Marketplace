import axios, { AxiosInstance } from "axios"

export const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
})

export type { DefaultErrorResponse, DefaultApiAction } from "./interfaces"
