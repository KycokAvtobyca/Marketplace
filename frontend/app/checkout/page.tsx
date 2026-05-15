"use client"

import React, { useState } from "react"
import { useGetCart } from "@/entities/cart/api/useCart"
import {
  CreateOrderPayload,
  useCreateOrder,
} from "@/entities/orders/api/useCreateOrder"
import { useProfile } from "@/entities/user/api/useProfile"
import { Icon } from "@/shared/ui/Icons/Icon"
import { useRouter } from "next/navigation"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"
import { PhoneInput } from "@/shared/ui/PhoneInput"
import { isAxiosError } from "axios"

const BRANCHES = [
  { value: "LENINA_5A", label: "г. Иркутск, ул. Ленина, д. 5А" },
]

interface CheckoutErrorResponse {
  address?: string | string[]
  date_time_deliver?: string | string[]
  phone_number?: string | string[]
  name?: string | string[]
  branch?: string | string[]
  promocode?: string | string[]
  cart?: string | string[]
  detail?: string | { message?: string }
}

type CheckoutFieldErrors = Partial<Record<keyof CheckoutErrorResponse, string>>

const firstMessage = (value?: string | string[]) =>
  Array.isArray(value) ? value[0] : value

const getCheckoutErrorMessage = (error: unknown) => {
  if (!isAxiosError<CheckoutErrorResponse>(error)) {
    return "Ошибка оформления заказа"
  }

  const data = error.response?.data
  const cartMessage = Array.isArray(data?.cart) ? data?.cart[0] : data?.cart
  const detailMessage =
    typeof data?.detail === "string" ? data.detail : data?.detail?.message

  return cartMessage || detailMessage || "Ошибка оформления заказа"
}

const getCheckoutErrors = (error: unknown) => {
  const fallback = getCheckoutErrorMessage(error)
  if (!isAxiosError<CheckoutErrorResponse>(error)) {
    return { form: fallback, fields: {} as CheckoutFieldErrors }
  }

  const data = error.response?.data
  const fields: CheckoutFieldErrors = {
    address: firstMessage(data?.address),
    date_time_deliver: firstMessage(data?.date_time_deliver),
    phone_number: firstMessage(data?.phone_number),
    name: firstMessage(data?.name),
    branch: firstMessage(data?.branch),
    promocode: firstMessage(data?.promocode),
  }

  return { form: firstMessage(data?.promocode) || fallback, fields }
}

export default function CheckoutPage() {
  const router = useRouter()
  const { data: cart, isLoading: cartLoading } = useGetCart()
  const { data: profile } = useProfile()
  const { mutate: createOrder, isPending } = useCreateOrder()

  const [formData, setFormData] = useState({
    delivery_type: "PICKUP" as "PICKUP" | "COURIER",
    branch: "LENINA_5A",
    address: "",
    name: "",
    phone_number: "",
    date_time_deliver: "",
    description: "",
  })

  const [error, setError] = useState("")
  const [fieldErrors, setFieldErrors] = useState<CheckoutFieldErrors>({})
  const [success, setSuccess] = useState(false)

  React.useEffect(() => {
    if (profile) {
      setFormData((prev) => ({
        ...prev,
        name: prev.name || profile.name || "",
        phone_number: prev.phone_number || profile.phone_number || "",
        address: prev.address || profile.address || "",
      }))
    }
  }, [profile])

  if (cartLoading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-12 text-center animate-pulse sm:p-12">
        Загрузка...
      </div>
    )
  }

  const cartItems = cart?.cart_items || []

  if (cartItems.length === 0 && !success) {
    return (
      <main className="mx-auto flex max-w-5xl flex-col items-center gap-4 px-4 py-12 text-center sm:p-12">
        <Icon.CART className="w-16 h-16 text-slate-200" />
        <h2 className="text-xl font-bold text-slate-900">Корзина пуста</h2>
        <p className="text-slate-500">Добавьте товары, чтобы оформить заказ</p>
      </main>
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setFieldErrors({})

    const payload: CreateOrderPayload = {
      delivery_type: formData.delivery_type,
      branch: formData.delivery_type === "PICKUP" ? formData.branch : null,
      address: formData.delivery_type === "COURIER" ? formData.address : null,
      date_time_deliver:
        formData.delivery_type === "COURIER" && formData.date_time_deliver
          ? new Date(formData.date_time_deliver).toISOString()
          : null,
      name: formData.name,
      phone_number: formData.phone_number,
      description: formData.description,
      address_data: {},
    }

    createOrder(payload, {
      onSuccess: () => {
        setSuccess(true)
        setTimeout(() => router.push("/profile"), 2000)
      },
      onError: (err: unknown) => {
        const nextErrors = getCheckoutErrors(err)
        setError(nextErrors.form)
        setFieldErrors(nextErrors.fields)
      },
    })
  }

  if (success) {
    return (
      <main className="mx-auto max-w-xl px-4 py-12 text-center sm:p-12">
        <div className="rounded-2xl border border-green-200 bg-green-50 p-4 sm:p-6">
          <div className="text-5xl mb-3">✅</div>
          <h2 className="text-xl font-bold text-green-700 mb-2">
            Заказ оформлен!
          </h2>
          <p className="text-green-600">Перенаправление в личный кабинет...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-5xl p-3 sm:p-6">
      <Breadcrumbs
        crumbs={[
          { label: "Корзина", href: "/cart" },
          { label: "Оформление заказа" },
        ]}
      />
      <h1 className="text-2xl font-bold mb-8">Оформление заказа</h1>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3 lg:gap-8">
        {/* Форма */}
        <div className="lg:col-span-2 space-y-6">
          <form
            onSubmit={handleSubmit}
            className="space-y-4 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm sm:p-6"
          >
            <h2 className="text-lg font-bold">Контактные данные</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Имя получателя *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required
                  minLength={2}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
                />
                {fieldErrors.name && (
                  <p className="mt-1 text-xs text-red-500">
                    {fieldErrors.name}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Телефон *
                </label>
                <PhoneInput
                  value={formData.phone_number}
                  onChange={(val) =>
                    setFormData({ ...formData, phone_number: val })
                  }
                  error={fieldErrors.phone_number}
                  hideLabel
                />
              </div>
            </div>

            <h2 className="text-lg font-bold pt-2">Доставка</h2>
            <div className="flex flex-col gap-3 min-[420px]:flex-row min-[420px]:gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="delivery_type"
                  value="PICKUP"
                  checked={formData.delivery_type === "PICKUP"}
                  onChange={() =>
                    setFormData({ ...formData, delivery_type: "PICKUP" })
                  }
                  className="accent-brand-main"
                />
                <span className="text-sm">Самовывоз</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="delivery_type"
                  value="COURIER"
                  checked={formData.delivery_type === "COURIER"}
                  onChange={() =>
                    setFormData({ ...formData, delivery_type: "COURIER" })
                  }
                  className="accent-brand-main"
                />
                <span className="text-sm">Курьерская доставка</span>
              </label>
            </div>

            {formData.delivery_type === "PICKUP" ? (
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Пункт выдачи *
                </label>
                <select
                  value={formData.branch}
                  onChange={(e) =>
                    setFormData({ ...formData, branch: e.target.value })
                  }
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
                >
                  {BRANCHES.map((b) => (
                    <option key={b.value} value={b.value}>
                      {b.label}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Адрес доставки *
                </label>
                <textarea
                  value={formData.address}
                  onChange={(e) =>
                    setFormData({ ...formData, address: e.target.value })
                  }
                  required
                  rows={2}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none resize-none"
                />
                {fieldErrors.address && (
                  <p className="mt-1 text-xs text-red-500">
                    {fieldErrors.address}
                  </p>
                )}
                <label className="mt-4 block text-sm font-medium text-slate-600 mb-1">
                  Время доставки *
                </label>
                <input
                  type="datetime-local"
                  value={formData.date_time_deliver}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      date_time_deliver: e.target.value,
                    })
                  }
                  required
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
                />
                {fieldErrors.date_time_deliver && (
                  <p className="mt-1 text-xs text-red-500">
                    {fieldErrors.date_time_deliver}
                  </p>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">
                Примечание к заказу
              </label>
              <textarea
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={2}
                maxLength={2000}
                className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none resize-none"
              />
            </div>

            {error && <p className="text-sm text-red-500">{error}</p>}

            <button
              type="submit"
              disabled={isPending}
              className="w-full py-4 bg-brand-main text-white rounded-xl font-bold uppercase tracking-widest hover:brightness-110 shadow-lg shadow-brand-main/20 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {isPending ? "Оформление..." : "Подтвердить заказ"}
            </button>
          </form>
        </div>

        {/* Сводка */}
        <div className="lg:col-span-1">
          <div className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm sm:p-6 lg:sticky lg:top-20">
            <h2 className="text-lg font-bold mb-4">Ваш заказ</h2>
            <div className="space-y-3 max-h-80 overflow-auto">
              {cartItems.map((item) => (
                <div key={item.id} className="flex min-w-0 gap-3">
                  <img
                    src={item.product_variant.image}
                    className="w-14 h-14 object-cover rounded-lg"
                    alt=""
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {item.product_variant.product_name}
                    </p>
                    <p className="text-xs text-slate-400">
                      {item.quantity} шт.
                    </p>
                    <p className="text-sm font-bold text-brand-main">
                      {Number(item.total_price).toLocaleString("ru-RU")} ₽
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <hr className="border-slate-100 my-4" />
            <div className="flex flex-wrap items-end justify-between gap-2">
              <span className="font-bold">Итого</span>
              <span className="text-2xl font-black text-brand-main">
                {Number(cart?.total_cost || 0).toLocaleString("ru-RU")} ₽
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
