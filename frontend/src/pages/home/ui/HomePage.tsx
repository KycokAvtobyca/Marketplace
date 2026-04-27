import { ProductListTitle } from "@/shared/ui/ProductListTitle"
import { ProductFiltersModal } from "@/features/ProductFiltersModal"

export const HomePage = () => {
  return (
    <section className="catalog py-15">
      {/* <h1
        id="hero-heading"
        className="text-4xl font-extrabold text-blue-600 mb-6 lg:text-5xl"
      >
        Маркетплейс Сиська
      </h1>
      <p className="text-lg text-slate-600 max-w-2xl">
        Здесь скоро появятся товары, которые мы будем получать по API из Django
        + DRF бэкенда.
      </p> */}
      <header className="catalog__header">
        <div className="flex justify-between items-center">
          <ProductListTitle className="catalog__title" />
          <ProductFiltersModal />
        </div>

        <div className="h-0.5 w-full rounded-full bg-brand-main mt-1 opacity-80" />
      </header>
    </section>
  )
}
