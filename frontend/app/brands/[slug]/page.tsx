"use client"

import { useParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ProductCard, ProductCardSkeleton, useCatalogProducts } from "@/entities/products"
import { Breadcrumbs } from "@/widgets/Breadcrumbs"

type Brand = {
  name: string
  slug: string
  description?: string
  image?: string | null
}

export default function BrandPage() {
  const params = useParams()
  const slug = String(params?.slug || "")
  const { data: brand, isLoading: brandLoading } = useQuery({
    queryKey: ["brand", slug],
    queryFn: async () => {
      const { data } = await api.get<Brand>(`/catalog/brands/${slug}/`)
      return data
    },
    enabled: Boolean(slug),
  })
  const { data: products, isLoading: productsLoading } = useCatalogProducts(
    `brands=${encodeURIComponent(slug)}`,
  )

  return (
    <main className="space-y-6">
      <Breadcrumbs crumbs={[{ label: "Бренды" }, { label: brand?.name || slug }]} />
      <section className="grid gap-5 rounded-xl border border-slate-100 bg-white p-4 shadow-sm sm:grid-cols-[180px_1fr] sm:p-6">
        <div className="aspect-square overflow-hidden rounded-lg bg-slate-100">
          {brand?.image && (
            <img src={brand.image} alt={brand.name} className="h-full w-full object-cover" />
          )}
        </div>
        <div className="min-w-0">
          <h1 className="text-2xl font-bold text-slate-900">
            {brandLoading ? "Загрузка..." : brand?.name}
          </h1>
          {brand?.description && (
            <p className="mt-3 text-sm leading-6 text-slate-600">{brand.description}</p>
          )}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-bold text-slate-900">Товары бренда</h2>
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
