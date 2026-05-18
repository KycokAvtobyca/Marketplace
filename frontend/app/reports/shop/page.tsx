"use client"

import React, { useEffect, useMemo, useState } from "react"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"
import { api } from "@/shared/api"
import { useCheckAdminAccess } from "@/entities/user"

type Option = {
  id: number | string
  name: string
}

const backendBase =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/api\/v1\/?$/, "") ||
  "http://127.0.0.1:8000"

const statusOptions = [
  { id: "", name: "Все кроме отмененных" },
  { id: "CREATED", name: "Оформлен" },
  { id: "ASSEMBLING", name: "Собирается" },
  { id: "DELIVERING", name: "В пути" },
  { id: "READY_FOR_PICKUP", name: "Готов к выдаче" },
  { id: "COMPLETED", name: "Получен, ожидает оплаты" },
  { id: "PAID", name: "Оплачен после получения" },
  { id: "CANCELED", name: "Отменен" },
]

const sortOptions = [
  { id: "product", name: "По товару" },
  { id: "revenue", name: "По выручке" },
  { id: "quantity", name: "По количеству" },
  { id: "views", name: "По просмотрам" },
]

function normalizeOptions(data: unknown): Option[] {
  const raw = Array.isArray(data)
    ? data
    : Array.isArray((data as { results?: unknown[] })?.results)
      ? (data as { results: unknown[] }).results
      : []

  return raw
    .map((item) => {
      const option = item as { id?: number; pk?: number; slug?: string; name?: string }
      return {
        id: option.id || option.pk || option.slug || "",
        name: option.name || String(option.slug || option.id || ""),
      }
    })
    .filter((item) => item.id && item.name)
}

export default function ShopReportPage() {
  const { data: hasAdminAccess } = useCheckAdminAccess()
  const [categories, setCategories] = useState<Option[]>([])
  const [productTypes, setProductTypes] = useState<Option[]>([])
  const [brands, setBrands] = useState<Option[]>([])
  const [form, setForm] = useState({
    date_from: "",
    date_to: "",
    all_time: true,
    category: "",
    product_type: "",
    brand: "",
    status: "",
    sort: "product",
  })

  useEffect(() => {
    api.get("/users/shop/report-options/").then(({ data }) => {
      setCategories(normalizeOptions(data.categories))
      setProductTypes(normalizeOptions(data.product_types))
      setBrands(normalizeOptions(data.brands))
    })
  }, [])

  const queryString = useMemo(() => {
    const params = new URLSearchParams()
    if (form.all_time) {
      params.set("all_time", "1")
    } else {
      if (form.date_from) params.set("date_from", form.date_from)
      if (form.date_to) params.set("date_to", form.date_to)
    }
    if (form.category) params.set("category", form.category)
    if (form.product_type) params.set("product_type", form.product_type)
    if (form.brand) params.set("brand", form.brand)
    if (form.status) params.set("status", form.status)
    if (form.sort) params.set("sort", form.sort)
    return params
  }, [form])

  const openReport = (format: "1" | "word") => {
    const params = new URLSearchParams(queryString)
    params.set("download", format)
    window.open(`${backendBase}/admin/reports/shop/?${params.toString()}`, "_blank")
  }

  return (
    <main className="mx-auto max-w-5xl space-y-6 p-3 sm:p-6">
      <Breadcrumbs
        crumbs={[
          { label: "Личный кабинет", href: "/profile" },
          { label: "Отчет магазина" },
        ]}
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-2xl font-bold text-slate-950">Отчет магазина</h1>
          <p className="mt-1 text-sm text-slate-500">
            Сформируйте аккуратный PDF или Word-документ с заказами, выручкой,
            продажами и просмотрами товаров.
          </p>
        </div>
        <a
          href={`${backendBase}/admin-login/`}
          className="inline-flex w-full items-center justify-center rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-brand-main hover:text-brand-main sm:w-auto"
        >
          Войти в админку
        </a>
      </div>

      {!hasAdminAccess && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Для скачивания отчета нужен доступ продавца или администратора.
        </div>
      )}

      <section className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm sm:p-5">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Дата с
            <input
              type="date"
              value={form.date_from}
              disabled={form.all_time}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, date_from: event.target.value }))
              }
              className="min-w-0 rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main disabled:bg-slate-50"
            />
          </label>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Дата по
            <input
              type="date"
              value={form.date_to}
              disabled={form.all_time}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, date_to: event.target.value }))
              }
              className="min-w-0 rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main disabled:bg-slate-50"
            />
          </label>
          <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
            <input
              type="checkbox"
              checked={form.all_time}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, all_time: event.target.checked }))
              }
              className="accent-brand-main"
            />
            За все время
          </label>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Сортировка
            <select
              value={form.sort}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, sort: event.target.value }))
              }
              className="min-w-0 rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main"
            >
              {sortOptions.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Категория
            <select
              value={form.category}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, category: event.target.value }))
              }
              className="min-w-0 rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main"
            >
              <option value="">Все категории</option>
              {categories.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Тип продукта
            <select
              value={form.product_type}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, product_type: event.target.value }))
              }
              className="min-w-0 rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main"
            >
              <option value="">Все типы</option>
              {productTypes.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Бренд
            <select
              value={form.brand}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, brand: event.target.value }))
              }
              className="min-w-0 rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main"
            >
              <option value="">Все бренды</option>
              {brands.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Статус заказа
            <select
              value={form.status}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, status: event.target.value }))
              }
              className="min-w-0 rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main"
            >
              {statusOptions.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="mt-5 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={() => openReport("1")}
            className="w-full rounded-xl bg-brand-main px-5 py-3 text-sm font-bold text-white transition hover:brightness-110 sm:w-auto"
          >
            Скачать PDF
          </button>
          <button
            type="button"
            onClick={() => openReport("word")}
            className="w-full rounded-xl border border-brand-main px-5 py-3 text-sm font-bold text-brand-main transition hover:bg-brand-main hover:text-white sm:w-auto"
          >
            Скачать Word
          </button>
        </div>
      </section>
    </main>
  )
}
