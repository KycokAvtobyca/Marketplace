"use client"

import React from "react"
import { useGetCart, useRemoveFromCart, useUpdateCartItemQuantity } from "@/entities/cart/api/useCart"
import { Icon } from "@/shared/ui/Icons/Icon"
import { useQueryClient } from "@tanstack/react-query"
import Link from "next/link"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"

export const CartPage = () => {
  const queryClient = useQueryClient()
  const { data, isLoading } = useGetCart()
  const { mutate: removeItem } = useRemoveFromCart()
  const { mutate: updateQuantity, isPending: isUpdating } = useUpdateCartItemQuantity()

  const handleRemove = (id: number) => {
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

  if (isLoading)
    return (
      <div className="max-w-5xl mx-auto p-12 text-center animate-pulse">
        Загрузка корзины...
      </div>
    )

  const cartItems = data?.cart_items || []

  if (cartItems.length === 0) {
    return (
      <main className="max-w-5xl mx-auto p-12 text-center flex flex-col items-center gap-4">
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
    <main className="max-w-5xl mx-auto p-4 sm:p-6">
      <Breadcrumbs crumbs={[{ label: "Корзина" }]} />
      <h1 className="text-2xl font-bold mb-8">Корзина</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Список товаров */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          {cartItems.map((item) => (
            <div
              key={item.id}
              className="flex gap-4 p-4 bg-white border border-slate-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow"
            >
              <img
                src={item.product_variant.image}
                className="w-20 h-24 sm:w-24 sm:h-32 object-cover rounded-xl"
                alt=""
              />

              <div className="flex flex-col flex-1">
                <div className="flex justify-between items-start">
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

                <div className="mt-auto flex justify-between items-end">
                  <div className="flex items-center gap-2 bg-slate-50 px-2 py-1 rounded-lg">
                    <button
                      onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                      disabled={isUpdating || item.quantity <= 1}
                      className="px-2 py-1 hover:bg-slate-200 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      −
                    </button>
                    <span className="px-3 py-1 text-sm font-bold min-w-12 text-center">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                      disabled={isUpdating || item.quantity >= item.product_variant.stock}
                      className="px-2 py-1 hover:bg-slate-200 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      +
                    </button>
                  </div>

                  <div className="text-right">
                    <p className="text-lg font-bold text-slate-900">
                      {Number(item.total_price).toLocaleString("ru-RU")} ₽
                    </p>
                    <p className="text-[10px] text-slate-400">
                      {Number(item.product_variant.final_price).toLocaleString(
                        "ru-RU",
                      )}{" "}
                      ₽ / шт.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Итоги заказа (Sidebar) */}
        <div className="lg:col-span-1">
          <div className="sticky top-20 p-6 bg-white border border-slate-100 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold mb-6">Ваша корзина</h2>

            <div className="flex flex-col gap-3 mb-6">
              <div className="flex justify-between text-slate-500">
                <span>Товары ({cartItems.length})</span>
                <span>
                  {Number(data?.total_items_price).toLocaleString("ru-RU")} ₽
                </span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Доставка</span>
                <span className="text-green-500 font-medium">Бесплатно</span>
              </div>
              <hr className="border-slate-100 my-2" />
              <div className="flex justify-between items-end">
                <span className="font-bold">Итого</span>
                <span className="text-2xl font-black text-brand-main">
                  {Number(data?.total_cost).toLocaleString("ru-RU")} ₽
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
