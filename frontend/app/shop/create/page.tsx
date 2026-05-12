"use client"

import React, { useState } from "react"
import { useCreateShop } from "@/entities/user/api/useCreateShop"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"

export default function CreateShopPage() {
  const router = useRouter()
  const { mutate: createShop, isPending, error } = useCreateShop()
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [success, setSuccess] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createShop(
      { name, description },
      {
        onSuccess: () => {
          setSuccess(true)
          setTimeout(() => {
            window.location.href = "http://127.0.0.1:8000/admin-login/"
          }, 2000)
        },
      }
    )
  }

  return (
    <main className="max-w-xl mx-auto p-4 sm:p-6">
      <Breadcrumbs crumbs={[{ label: "Личный кабинет", href: "/profile" }, { label: "Создание магазина" }]} />
      <Link
        href="/profile"
        className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-brand-main mb-4 transition-colors"
      >
        ← Вернуться в профиль
      </Link>
      <h1 className="text-2xl font-bold mb-6">Создание магазина</h1>

      {success ? (
        <div className="p-6 bg-green-50 border border-green-200 rounded-2xl text-center">
          <p className="text-lg font-bold text-green-700 mb-2">
            Магазин успешно создан!
          </p>
          <p className="text-sm text-green-600">
            Перенаправление в панель администратора...
          </p>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm space-y-4"
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
              {(error as any)?.response?.data?.detail || "Ошибка создания магазина"}
            </p>
          )}

          <div className="flex gap-3 pt-2">
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
