"use client"

import React, { useState } from "react"
import { useCreateShop } from "@/entities/user/api/useCreateShop"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"
import { isAxiosError } from "axios"

interface ShopCreateError {
  detail?: string
}

export default function CreateShopPage() {
  const router = useRouter()
  const { mutate: createShop, isPending, error } = useCreateShop()
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [success, setSuccess] = useState(false)
  const errorMessage = isAxiosError<ShopCreateError>(error)
    ? error.response?.data?.detail
    : undefined

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createShop(
      { name, description },
      {
        onSuccess: () => {
          setSuccess(true)
        },
      }
    )
  }

  return (
    <main className="mx-auto max-w-xl p-3 sm:p-6">
      <Breadcrumbs crumbs={[{ label: "Личный кабинет", href: "/profile" }, { label: "Создание магазина" }]} />
      <Link
        href="/profile"
        className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-brand-main mb-4 transition-colors"
      >
        ← Вернуться в профиль
      </Link>
      <h1 className="text-2xl font-bold mb-6">Создание магазина</h1>

      {success ? (
        <div className="rounded-2xl border border-green-200 bg-green-50 p-4 text-center sm:p-6">
          <p className="text-lg font-bold text-green-700 mb-2">
            Заявка отправлена на модерацию!
          </p>
          <p className="text-sm text-green-600">
            Магазин появится после одобрения администратором.
          </p>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm sm:p-6"
        >
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">
              Название магазина *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              minLength={2}
              className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none"
              placeholder="Например, Мой магазин"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">
              Описание
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              maxLength={500}
              className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-brand-main focus:ring-1 focus:ring-brand-main outline-none resize-none"
              placeholder="Расскажите о своем магазине..."
            />
          </div>

          {error && (
            <p className="text-sm text-red-500">
              {errorMessage || "Ошибка создания магазина"}
            </p>
          )}

          <div className="flex flex-col gap-3 pt-2 min-[420px]:flex-row">
            <button
              type="button"
              onClick={() => router.back()}
              className="flex-1 py-3 border border-slate-200 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={isPending || !name.trim()}
              className="flex-1 py-3 bg-brand-main text-white rounded-xl font-medium hover:brightness-110 transition-all disabled:opacity-50"
            >
              {isPending ? "Создание..." : "Создать магазин"}
            </button>
          </div>
        </form>
      )}
    </main>
  )
}
