import { Breadcrumbs } from "@/widgets/Breadcrumbs"

export default function BlockedPage() {
  return (
    <main className="mx-auto max-w-xl px-4 py-12 text-center sm:p-12">
      <Breadcrumbs crumbs={[{ label: "Аккаунт заблокирован" }]} />
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
        <h1 className="text-2xl font-bold text-red-700">
          Аккаунт заблокирован
        </h1>
        <p className="mt-3 text-sm text-red-600">
          Вы не можете войти на сайт и пользоваться сервисом. Обратитесь к
          администратору, если считаете блокировку ошибочной.
        </p>
      </div>
    </main>
  )
}
