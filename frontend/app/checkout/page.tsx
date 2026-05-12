"use client"

import React, { useState } from "react"
import { useGetCart } from "@/entities/cart/api/useCart"
import { useCreateOrder } from "@/entities/orders/api/useCreateOrder"
import { useProfile } from "@/entities/user/api/useProfile"
import { Icon } from "@/shared/ui/Icons/Icon"
import { useRouter } from "next/navigation"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"

const BRANCHES = [
  { value: "LENINA_5A", label: "г. Иркутск, ул. Ленина, д. 5А" },
]

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
    description: "",
  })

  const [error, setError] = useState("")
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
      <div className="max-w-5xl mx-auto p-12 text-center animate-pulse">
        Загрузка...
      </div>
    )
  }

  const cartItems = cart?.cart_items || []

  if (cartItems.length === 0 && !success) {
    return (
      <main className="max-w-5xl mx-auto p-12 text-center flex flex-col items-center gap-4">
        <Icon.CART className="w-16 h-16 text-slate-200" />
        <h2 className="text-xl font-bold text-slate-900">Корзина пуста</h2>
        <p className="text-slate-500">Добавьте товары, чтобы оформить заказ</p>
      </main>
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    const payload: any = {
      delivery_type: formData.delivery_type,
      name: formData.name,
      phone_number: formData.phone_number,
      description: formData.description,
      address_data: {},
    }

    if (formData.delivery_type === "PICKUP") {
      payload.branch = formData.branch
      payload.address = null
    } else {
      payload.address = formData.address
      payload.branch = null
    }

    createOrder(
      payload,
      {
        onSuccess: () => {
          setSuccess(true)
          setTimeout(() => router.push("/profile"), 2000)
        },
        onError: (err: any) => {
          setError(
            err.response?.data?.cart ||
              err.response?.data?.detail ||
              "Ошибка оформления заказа"
          )
        },
      }
    )
  }

  if (success) {
    return (
      <main className="max-w-xl mx-auto p-12 text-center">
        <div className="p-6 bg-green-50 border border-green-200 rounded-2xl">
          <div className="text-5xl mb-3">✅</div>
          <h2 className="text-xl font-bold text-green-700 mb-2">
            Заказ оформлен!
          </h2>
          <p className="text-green-600">
            Перенаправление в личный кабинет...
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-5xl mx-auto p-4 sm:p-6">
      <Breadcrumbs crumbs={[{ label: "Корзина", href: "/cart" }, { label: "Оформление заказа" }]} />
      <h1 className="text-2xl font-bold mb-8">Оформление заказа</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Форма */}
        <div className="lg:col-span-2 space-y-6">
          <form
            onSubmit={handleSubmit}
            className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm space-y-4"
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
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Телефон *
                </label>
                <input
                  type="tel"
                  value={formData.phone_number}
                  onChange={(e) =>
                    setFormData({ ...formData, phone_number: e.target.value })
                  }
                  required
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
                />
              </div>
            </div>

            <h2 className="text-lg font-bold pt-2">Доставка</h2>
            <div className="flex gap-4">
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
          <div className="sticky top-20 p-6 bg-white border border-slate-100 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold mb-4">Ваш заказ</h2>
            <div className="space-y-3 max-h-80 overflow-auto">
              {cartItems.map((item) => (
                <div key={item.id} className="flex gap-3">
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
            <div className="flex justify-between items-end">
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
