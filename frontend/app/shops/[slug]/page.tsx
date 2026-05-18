"use client"

import { useParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ProductCard, ProductCardSkeleton, useCatalogProducts } from "@/entities/products"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"

type Shop = {
  name: string
  slug: string
  description?: string
  image?: string | null
}

export default function ShopPage() {
  const params = useParams()
  const slug = String(params?.slug || "")
  const { data: shop, isLoading: shopLoading } = useQuery({
    queryKey: ["shop", slug],
    queryFn: async () => {
      const { data } = await api.get<Shop>(`/users/shop/${slug}/`)
      return data
    },
    enabled: Boolean(slug),
  })
  const { data: products, isLoading: productsLoading } = useCatalogProducts(
    `shops=${encodeURIComponent(slug)}`,
  )

  return (
    <main className="space-y-6">
      <Breadcrumbs crumbs={[{ label: "Магазины" }, { label: shop?.name || slug }]} />
      <section className="grid gap-5 rounded-xl border border-slate-100 bg-white p-4 shadow-sm sm:grid-cols-[180px_1fr] sm:p-6">
        <div className="aspect-square overflow-hidden rounded-lg bg-slate-100">
          {shop?.image && (
            <img src={shop.image} alt={shop.name} className="h-full w-full object-cover" />
          )}
        </div>
        <div className="min-w-0">
          <h1 className="text-2xl font-bold text-slate-900">
            {shopLoading ? "Загрузка..." : shop?.name}
          </h1>
          {shop?.description && (
            <p className="mt-3 text-sm leading-6 text-slate-600">{shop.description}</p>
          )}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-bold text-slate-900">Товары магазина</h2>
        <div className="grid grid-cols-1 gap-3 min-[380px]:grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
          {productsLoading
            ? Array.from({ length: 4 }).map((_, index) => <ProductCardSkeleton key={index} />)
            : products?.results.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
        </div>
      </section>
    </main>
  )
}
