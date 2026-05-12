"use client"

import React, { useState } from "react"
import { useProfile } from "@/entities/user/api/useProfile"
import { useUpdateProfile } from "@/entities/user/api/useUpdateProfile"
import { usePhoneChange } from "@/entities/user/api/usePhoneChange"
import { useMyShop } from "@/entities/user/api/useMyShop"
import { useCheckAdminAccess, useRedirectToAdmin } from "@/entities/user"
import { useOrders } from "@/entities/orders/api/useOrders"
import { Icon } from "@/shared/ui/Icons/Icon"
import Link from "next/link"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"

const BRANCHES = [
  { value: "LENINA_5A", label: "г. Иркутск, ул. Ленина, д. 5А" },
]

export default function ProfilePage() {
  const { data: profile, isLoading } = useProfile()
  const { mutate: updateProfile, isPending: isUpdating } = useUpdateProfile()
  const { mutate: phoneChange, isPending: isPhoneChanging } = usePhoneChange()
  const { data: shop, isError: shopError } = useMyShop()
  const { data: orders } = useOrders()
  const { data: hasAdminAccess } = useCheckAdminAccess()
  const { mutate: redirectToAdmin, isPending: isRedirecting } =
    useRedirectToAdmin()

  const [formData, setFormData] = useState({
    name: "",
    last_name: "",
    middle_name: "",
    email: "",
    address: "",
  })

  const [phoneStep, setPhoneStep] = useState<
    "idle" | "verify_old" | "enter_new" | "verify_new"
  >("idle")
  const [oldCode, setOldCode] = useState("")
  const [newPhone, setNewPhone] = useState("")
  const [newCode, setNewCode] = useState("")
  const [phoneError, setPhoneError] = useState("")

  React.useEffect(() => {
    if (profile) {
      setFormData({
        name: profile.name || "",
        last_name: profile.last_name || "",
        middle_name: profile.middle_name || "",
        email: profile.email || "",
        address: profile.address || "",
      })
    }
  }, [profile])

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto p-12 text-center animate-pulse">
        Загрузка профиля...
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="max-w-5xl mx-auto p-12 text-center">
        <p className="text-slate-500">Войдите, чтобы просмотреть профиль</p>
      </div>
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateProfile(formData, {
      onSuccess: () => alert("Данные успешно сохранены!"),
    })
  }

  const handleSendOldCode = () => {
    setPhoneError("")
    phoneChange(
      { action: "send_old" },
      {
        onSuccess: () => setPhoneStep("verify_old"),
        onError: () => setPhoneError("Ошибка отправки кода"),
      },
    )
  }

  const handleVerifyOldCode = () => {
    setPhoneError("")
    phoneChange(
      { action: "verify_old", code: oldCode },
      {
        onSuccess: () => setPhoneStep("enter_new"),
        onError: () => setPhoneError("Неверный код"),
      },
    )
  }

  const handleSendNewCode = () => {
    setPhoneError("")
    phoneChange(
      { action: "send_new", new_phone: newPhone },
      {
        onSuccess: () => setPhoneStep("verify_new"),
        onError: (err: any) =>
          setPhoneError(err.response?.data?.phone_number || "Ошибка"),
      },
    )
  }

  const handleVerifyNewCode = () => {
    setPhoneError("")
    phoneChange(
      { action: "verify_new", new_phone: newPhone, code: newCode },
      {
        onSuccess: () => {
          setPhoneStep("idle")
          setOldCode("")
          setNewPhone("")
          setNewCode("")
          window.location.reload()
        },
        onError: () => setPhoneError("Неверный код"),
      },
    )
  }

  return (
    <main className="max-w-5xl mx-auto p-4 sm:p-6 space-y-8">
      <Breadcrumbs crumbs={[{ label: "Личный кабинет" }]} />
      <h1 className="text-2xl font-bold">Личный кабинет</h1>

      {/* Основная информация */}
      <section className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
        <h2 className="text-lg font-bold mb-4">👤 Личные данные</h2>

        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 sm:grid-cols-2 gap-4"
        >
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">
              Имя
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">
              Фамилия
            </label>
            <input
              type="text"
              value={formData.last_name}
              onChange={(e) =>
                setFormData({ ...formData, last_name: e.target.value })
              }
              className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">
              Отчество
            </label>
            <input
              type="text"
              value={formData.middle_name}
              onChange={(e) =>
                setFormData({ ...formData, middle_name: e.target.value })
              }
              className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">
              Email
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-600 mb-1">
              Адрес
            </label>
            <textarea
              value={formData.address}
              onChange={(e) =>
                setFormData({ ...formData, address: e.target.value })
              }
              rows={2}
              className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none resize-none"
            />
          </div>
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={isUpdating}
              className="px-6 py-2 bg-brand-main text-white rounded-xl font-medium hover:brightness-110 transition-all disabled:opacity-50"
            >
              {isUpdating ? "Сохранение..." : "Сохранить изменения"}
            </button>
            <p
              className="text-xs text-green-600 mt-2 hidden"
              id="profile-success"
            >
              ✅ Данные сохранены
            </p>
          </div>
        </form>
      </section>

      {/* Телефон */}
      <section className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
        <h2 className="text-lg font-bold mb-4">📞 Номер телефона</h2>
        <div className="flex items-center gap-4">
          <span className="text-lg font-medium">{profile.phone_number}</span>
          {phoneStep === "idle" && (
            <button
              onClick={handleSendOldCode}
              disabled={isPhoneChanging}
              className="text-sm text-brand-main hover:underline disabled:opacity-50"
            >
              Сменить номер
            </button>
          )}
        </div>

        {phoneStep !== "idle" && (
          <div className="mt-4 space-y-3">
            {phoneStep === "verify_old" && (
              <>
                <p className="text-sm text-slate-500">
                  Введите код, отправленный на текущий номер
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={oldCode}
                    onChange={(e) => setOldCode(e.target.value)}
                    placeholder="Код из SMS"
                    maxLength={6}
                    className="px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main outline-none w-40"
                  />
                  <button
                    onClick={handleVerifyOldCode}
                    disabled={isPhoneChanging}
                    className="px-4 py-2 bg-brand-main text-white rounded-xl text-sm font-medium hover:brightness-110 disabled:opacity-50"
                  >
                    Подтвердить
                  </button>
                </div>
              </>
            )}
            {phoneStep === "enter_new" && (
              <>
                <p className="text-sm text-slate-500">
                  Введите новый номер телефона
                </p>
                <div className="flex gap-2">
                  <input
                    type="tel"
                    value={newPhone}
                    onChange={(e) => {
                      let val = e.target.value.replace(/\D/g, "")
                      if (val.startsWith("7")) val = "+" + val
                      else if (val.startsWith("8")) val = "+7" + val.slice(1)
                      else if (val && !val.startsWith("+")) val = "+7" + val
                      setNewPhone(val)
                    }}
                    placeholder="+7..."
                    className="px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main outline-none w-48"
                  />
                  <button
                    onClick={handleSendNewCode}
                    disabled={isPhoneChanging}
                    className="px-4 py-2 bg-brand-main text-white rounded-xl text-sm font-medium hover:brightness-110 disabled:opacity-50"
                  >
                    Отправить код
                  </button>
                </div>
              </>
            )}
            {phoneStep === "verify_new" && (
              <>
                <p className="text-sm text-slate-500">
                  Введите код, отправленный на новый номер
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newCode}
                    onChange={(e) => setNewCode(e.target.value)}
                    placeholder="Код из SMS"
                    maxLength={6}
                    className="px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main outline-none w-40"
                  />
                  <button
                    onClick={handleVerifyNewCode}
                    disabled={isPhoneChanging}
                    className="px-4 py-2 bg-brand-main text-white rounded-xl text-sm font-medium hover:brightness-110 disabled:opacity-50"
                  >
                    Подтвердить
                  </button>
                </div>
              </>
            )}
            {phoneError && <p className="text-sm text-red-500">{phoneError}</p>}
          </div>
        )}
      </section>

      {/* Магазин */}
      <section className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
        <h2 className="text-lg font-bold mb-4">🏪 Магазин</h2>
        {shop ? (
          <div className="space-y-3">
            <p className="font-medium">{shop.name}</p>
            <p className="text-sm text-slate-500">{shop.description}</p>
            {hasAdminAccess && (
              <button
                onClick={() => redirectToAdmin()}
                disabled={isRedirecting}
                className="inline-flex items-center gap-2 px-4 py-2 bg-brand-main text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all disabled:opacity-50"
              >
                ⚙️ {isRedirecting ? "Переход..." : "Панель администратора"}
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-slate-500">У вас пока нет магазина</p>
            <Link
              href="/shop/create"
              className="inline-flex items-center gap-2 px-4 py-2 bg-brand-main text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all"
            >
              ➕ Стать продавцом
            </Link>
          </div>
        )}
      </section>

      {/* Заказы */}
      <section className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
        <h2 className="text-lg font-bold mb-4">📦 История заказов</h2>
        {orders && orders.length > 0 ? (
          <div className="space-y-6">
            {orders.map((order) => (
              <div
                key={order.id}
                className="rounded-3xl border border-slate-200 bg-slate-50 p-5"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-semibold text-slate-900">
                      Заказ #{order.id}
                    </p>
                    <p className="text-sm text-slate-500">
                      {order.status_display} · {order.delivery_type_display}
                    </p>
                    <p className="text-sm text-slate-400">
                      {new Date(order.date_time_create).toLocaleDateString(
                        "ru-RU",
                      )}{" "}
                      •{" "}
                      {order.branch_display ||
                        order.address ||
                        "Адрес не указан"}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-500">Итого</p>
                    <p className="font-bold text-brand-main text-lg">
                      {Number(order.total_cost).toLocaleString("ru-RU")} ₽
                    </p>
                  </div>
                </div>

                <div className="mt-4 space-y-3">
                  {order.order_items.map((item) => (
                    <div
                      key={item.id}
                      className="grid grid-cols-[72px_1fr] gap-3 rounded-2xl bg-white p-3 shadow-sm"
                    >
                      <img
                        src={item.product_variant_image || "/placeholder.png"}
                        alt={item.product_variant_name}
                        className="h-18 w-18 rounded-2xl object-cover"
                      />
                      <div className="space-y-1 text-sm">
                        <p className="font-medium text-slate-900">
                          {item.product_variant_name}
                        </p>
                        <p className="text-slate-500">
                          Артикул: {item.product_variant_sku}
                        </p>
                        <p className="text-slate-500">
                          Количество: {item.quantity}
                        </p>
                        <p className="text-slate-500">
                          Цена:{" "}
                          {Number(
                            item.discounted_price_per_item,
                          ).toLocaleString("ru-RU")}{" "}
                          ₽
                        </p>
                        <p className="font-medium text-slate-900">
                          Сумма:{" "}
                          {Number(item.total_price).toLocaleString("ru-RU")} ₽
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">У вас пока нет заказов</p>
        )}
      </section>
    </main>
  )
}
