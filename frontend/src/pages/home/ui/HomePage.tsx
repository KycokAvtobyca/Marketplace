import { PageTitle } from "@/shared/ui/ProductListTitle"
import { FilterModalMenu } from "@/widgets/FilterModalMenu"
import { FilterSidebar } from "@/widgets/FilterSidebar"
import { ProductList } from "@/widgets/ProductList"
import { CategoryBreadcrumbs } from "@/widgets/Breadcrumbs/ui/CategoryBreadcrumbs"

export const HomePage = async () => {
  return (
    <section className="catalog space-y-4">
      <CategoryBreadcrumbs />
      <header className="catalog__header">
        <div className="flex flex-col gap-3 min-[480px]:flex-row min-[480px]:items-center min-[480px]:justify-between">
          <PageTitle className="catalog__title" />

          <div className="block min-[800px]:hidden">
            <FilterModalMenu classNameHamburgerButton="catalog__hamburger-button" />
          </div>
        </div>

        <div className="catalog-line h-0.5 w-full rounded-full bg-brand-main mt-1 opacity-80" />
      </header>

      {/* Основной контент*/}
      <div className="flex min-w-0 items-start gap-4">
        <FilterSidebar />

        <main className="min-w-0 grow">
          <ProductList />
        </main>
      </div>
    </section>
  )
}
