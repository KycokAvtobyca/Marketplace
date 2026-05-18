"use client"

import React from "react"
import {
  useGetCart,
  useApplyPromocode,
  useRemovePromocode,
  useRemoveFromCart,
  useUpdateCartItemQuantity,
} from "@/entities/cart/api/useCart"
import { Icon } from "@/shared/ui/Icons/Icon"
import { useQueryClient } from "@tanstack/react-query"
import Link from "next/link"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"

export const CartPage = () => {
  const queryClient = useQueryClient()
  const { data, isLoading } = useGetCart()
  const { mutate: removeItem } = useRemoveFromCart()
  const { mutate: updateQuantity, isPending: isUpdating } =
    useUpdateCartItemQuantity()
  const { mutate: applyPromocode, isPending: isApplyingPromocode } =
    useApplyPromocode()
  const { mutate: removePromocode, isPending: isRemovingPromocode } =
    useRemovePromocode()
  const [promocode, setPromocode] = React.useState("")
  const [promocodeError, setPromocodeError] = React.useState("")
  const [quantityInputs, setQuantityInputs] = React.useState<
    Record<number, string>
  >({})
  const quantityTimers = React.useRef<
    Record<number, ReturnType<typeof setTimeout>>
  >({})

  React.useEffect(() => {
    if (!data?.cart_items) return
    const quantities: Record<number, string> = {}
    data.cart_items.forEach((item) => {
      quantities[item.id] = String(item.quantity)
    })
    setQuantityInputs(quantities)
  }, [data?.cart_items])

  React.useEffect(() => {
    return () => {
      Object.values(quantityTimers.current).forEach((timer) => {
        clearTimeout(timer)
      })
      quantityTimers.current = {}
    }
  }, [])

  const clearQuantityTimer = (id: number) => {
    if (quantityTimers.current[id]) {
      clearTimeout(quantityTimers.current[id])
      delete quantityTimers.current[id]
    }
  }

  const scheduleQuantityUpdate = (
    id: number,
    quantityString: string,
    currentQuantity: number,
    maxAmount: number,
  ) => {
    clearQuantityTimer(id)

    quantityTimers.current[id] = setTimeout(() => {
      handleQuantityInputSubmit(id, quantityString, currentQuantity, maxAmount)
    }, 1000)
  }

  const handleRemove = (id: number) => {
    clearQuantityTimer(id)
    removeItem(
      { cart_item_id: id },
      {
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
      },
    )
  }

  const handleQuantityChange = (id: number, quantity: number) => {
    if (quantity < 1) return
    updateQuantity(
      { cart_item_id: id, quantity },
      {
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
      },
    )
  }

  const handleQuantityInputChange = (
    id: number,
    value: string,
    maxAmount: number,
    currentQuantity: number,
  ) => {
    if (value === "") {
      setQuantityInputs((prev) => ({ ...prev, [id]: "" }))
      clearQuantityTimer(id)
      return
    }

    const sanitized = Number(value)
    if (Number.isNaN(sanitized)) return

    const rawValue = value.replace(/^0+/, "") || "0"
    const clamped = Math.max(
      1,
      Math.min(maxAmount, Math.trunc(Number(rawValue))),
    )
    const nextValue = String(clamped)
    setQuantityInputs((prev) => ({ ...prev, [id]: nextValue }))
    scheduleQuantityUpdate(id, nextValue, currentQuantity, maxAmount)
  }

  const handleQuantityInputSubmit = (
    id: number,
    quantity: string,
    currentQuantity: number,
    maxAmount: number,
  ) => {
    clearQuantityTimer(id)

    if (quantity === "") {
      setQuantityInputs((prev) => ({ ...prev, [id]: String(currentQuantity) }))
      return
    }

    const sanitized = Number(quantity)
    if (Number.isNaN(sanitized)) {
      setQuantityInputs((prev) => ({ ...prev, [id]: String(currentQuantity) }))
      return
    }

    const nextQuantity = Math.max(1, Math.min(maxAmount, Math.trunc(sanitized)))
    setQuantityInputs((prev) => ({ ...prev, [id]: String(nextQuantity) }))
    if (nextQuantity !== currentQuantity) {
      handleQuantityChange(id, nextQuantity)
    }
  }

  const formatPrice = (value: number | string | undefined) =>
    Number(value || 0).toLocaleString("ru-RU", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })

  const firstError = (value?: string | string[]) =>
    Array.isArray(value) ? value[0] : value

  const handleApplyPromocode = (event: React.FormEvent) => {
    event.preventDefault()
    setPromocodeError("")
    applyPromocode(promocode, {
      onSuccess: (result) => {
        if (!result.success) {
          setPromocodeError(
            firstError(result.error?.data.promocode) ||
              firstError(result.error?.data.error) ||
              firstError(result.error?.data.detail) ||
              "Не удалось применить промокод",
          )
          return
        }
        setPromocode("")
        queryClient.invalidateQueries({ queryKey: ["cart"] })
      },
    })
  }

  const handleRemovePromocode = () => {
    setPromocodeError("")
    removePromocode(undefined, {
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
    })
  }

  if (isLoading)
    return (
      <div className="mx-auto max-w-5xl px-4 py-12 text-center animate-pulse sm:p-12">
        Загрузка корзины...
      </div>
    )

  const cartItems = data?.cart_items || []

  if (cartItems.length === 0) {
    return (
      <main className="mx-auto flex max-w-5xl flex-col items-center gap-4 px-4 py-12 text-center sm:p-12">
        <Icon.CART className="w-16 h-16 text-slate-200" />
        <h2 className="text-xl font-bold text-slate-900">Ваша корзина пуста</h2>
        <Link
          href="/"
          className="mt-4 px-8 py-3 bg-brand-main text-white rounded-xl font-bold"
        >
          За покупками
        </Link>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-5xl p-3 sm:p-6">
      <Breadcrumbs crumbs={[{ label: "Корзина" }]} />
      <h1 className="text-2xl font-bold mb-8">Корзина</h1>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3 lg:gap-8">
        {/* Список товаров */}
        <div className="flex flex-col gap-4 lg:col-span-2">
          {cartItems.map((item) => (
            <div
              key={item.id}
              className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white p-3 shadow-sm transition-shadow hover:shadow-md min-[420px]:flex-row sm:p-4"
            >
              <img
                src={item.product_variant.image}
                className="h-44 w-full rounded-xl object-cover min-[420px]:h-32 min-[420px]:w-24"
                alt=""
              />

              <div className="flex min-w-0 flex-1 flex-col">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm sm:text-base font-semibold text-slate-800 line-clamp-2">
                    {item.product_variant.product_name}
                  </h3>
                  <button
                    onClick={() => handleRemove(item.id)}
                    className="text-slate-300 hover:text-red-500 transition-colors p-1"
                  >
                    <Icon.TRASH className="w-5 h-5" />
                  </button>
                </div>

                <p className="text-xs text-slate-400 mt-1">
                  Артикул: {item.product_variant.sku}
                </p>

                <div className="mt-4 flex flex-col gap-3 min-[520px]:flex-row min-[520px]:items-end min-[520px]:justify-between">
                  <div className="flex w-full items-center justify-between gap-2 rounded-lg bg-slate-50 px-2 py-1 min-[520px]:w-auto">
                    <button
                      type="button"
                      onClick={() =>
                        handleQuantityChange(item.id, item.quantity - 1)
                      }
                      disabled={isUpdating || item.quantity <= 1}
                      title="Уменьшить количество"
                      aria-label="Уменьшить количество"
                      className="px-2 py-1 hover:bg-slate-200 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      −
                    </button>
                    <input
                      type="number"
                      min={1}
                      max={item.product_variant.stock}
                      value={quantityInputs[item.id] ?? String(item.quantity)}
                      onChange={(e) =>
                        handleQuantityInputChange(
                          item.id,
                          e.target.value,
                          item.product_variant.stock,
                          item.quantity,
                        )
                      }
                      onBlur={() =>
                        handleQuantityInputSubmit(
                          item.id,
                          quantityInputs[item.id] ?? String(item.quantity),
                          item.quantity,
                          item.product_variant.stock,
                        )
                      }
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.currentTarget.blur()
                        }
                      }}
                      className="w-16 text-center bg-white border border-slate-200 rounded-lg py-1 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-brand-main appearance-none [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      aria-label="Количество товара"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        handleQuantityChange(item.id, item.quantity + 1)
                      }
                      disabled={
                        isUpdating ||
                        item.quantity >= item.product_variant.stock
                      }
                      title="Добавить количество"
                      aria-label="Добавить количество"
                      className="px-2 py-1 hover:bg-slate-200 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      +
                    </button>
                  </div>

                  <div className="text-left min-[520px]:text-right">
                    {item.has_promocode_discount ? (
                      <div>
                        <p className="text-sm text-slate-400 line-through">
                          {formatPrice(item.total_price)} ₽
                        </p>
                        <p className="text-lg font-bold text-brand-main">
                          {formatPrice(item.promocode_total_price)} ₽
                        </p>
                      </div>
                    ) : (
                      <p className="text-lg font-bold text-slate-900">
                        {formatPrice(item.total_price)} ₽
                      </p>
                    )}
                    <p className="text-[10px] text-slate-400">
                      {item.has_promocode_discount ? (
                        <>
                          <span className="line-through">
                            {formatPrice(item.product_variant.final_price)} ₽
                          </span>{" "}
                          <span className="text-brand-main">
                            {formatPrice(item.promocode_final_price)} ₽
                          </span>
                        </>
                      ) : (
                        <>{formatPrice(item.product_variant.final_price)} ₽</>
                      )}{" "}
                      / шт.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Итоги заказа (Sidebar) */}
        <div className="lg:col-span-1">
          <div className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm sm:p-6 lg:sticky lg:top-20">
            <h2 className="text-lg font-bold mb-6">Ваша корзина</h2>

            <div className="flex flex-col gap-3 mb-6">
              <div className="flex justify-between text-slate-500">
                <span>Товары ({cartItems.length})</span>
                <span>
                  {formatPrice(data?.total_items_price)} ₽
                </span>
              </div>
              <form onSubmit={handleApplyPromocode} className="space-y-2">
                <label className="text-sm font-medium text-slate-600">
                  Промокод
                </label>
                <div className="flex flex-col gap-2 min-[420px]:flex-row">
                  <input
                    value={promocode}
                    onChange={(e) => setPromocode(e.target.value)}
                    placeholder="SALE10"
                    disabled={isApplyingPromocode || !!data?.promocode_code}
                    className="min-w-0 flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-main disabled:bg-slate-50"
                  />
                  {data?.promocode_code ? (
                    <button
                      type="button"
                      onClick={handleRemovePromocode}
                      disabled={isRemovingPromocode}
                      className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm font-bold text-red-500 disabled:opacity-50 min-[420px]:w-auto"
                    >
                      Убрать
                    </button>
                  ) : (
                    <button
                      type="submit"
                      disabled={!promocode.trim() || isApplyingPromocode}
                      className="w-full rounded-xl bg-brand-main px-3 py-2 text-sm font-bold text-white disabled:opacity-50 min-[420px]:w-auto"
                    >
                      OK
                    </button>
                  )}
                </div>
                {data?.promocode_code && (
                  <p className="text-xs text-green-600">
                    Применён {data.promocode_code}
                    {data.promocode_discount
                      ? `, скидка ${formatPrice(data.promocode_discount)} ₽`
                      : ""}
                  </p>
                )}
                {promocodeError && (
                  <p className="text-xs text-red-500">{promocodeError}</p>
                )}
              </form>
              <div className="flex justify-between text-slate-500">
                <span>Доставка</span>
                <span className="text-green-500 font-medium">Бесплатно</span>
              </div>
              <hr className="border-slate-100 my-2" />
              <div className="flex flex-wrap items-end justify-between gap-2">
                <span className="font-bold">Итого</span>
                <span className="text-2xl font-black text-brand-main">
                  {formatPrice(data?.total_cost)} ₽
                </span>
              </div>
            </div>

            <Link
              href="/checkout"
              className="block w-full py-4 bg-brand-main text-white rounded-xl font-bold uppercase tracking-widest hover:brightness-110 shadow-lg shadow-brand-main/20 active:scale-[0.98] transition-all text-center"
            >
              Оформить заказ
            </Link>

            <p className="text-[10px] text-slate-400 mt-4 text-center">
              Нажимая кнопку, вы соглашаетесь с условиями оферты и политикой
              конфиденциальности.
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

export default function Page() {
  return <CartPage />
}
