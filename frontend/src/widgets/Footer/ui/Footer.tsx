import Link from "next/link"

export const Footer = () => {
  return (
    <footer className="w-full mt-auto py-8 border-t border-slate-100 bg-white/50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          {/* О проекте */}
          <div>
            <h3 className="font-bold text-brand-main mb-3">Floppi</h3>
            <p className="text-sm text-slate-500">
              Современный маркетплейс для покупок и продаж. Курсовая работа
              Лыскова Ивана.
            </p>
          </div>

          {/* Навигация */}
          <div>
            <h3 className="font-bold text-slate-800 mb-3">Навигация</h3>
            <ul className="space-y-2 text-sm text-slate-500">
              <li>
                <Link href="/" className="hover:text-brand-main transition-colors">
                  Главная
                </Link>
              </li>
              <li>
                <Link href="/cart" className="hover:text-brand-main transition-colors">
                  Корзина
                </Link>
              </li>
              <li>
                <Link href="/favorites" className="hover:text-brand-main transition-colors">
                  Избранное
                </Link>
              </li>
              <li>
                <Link href="/profile" className="hover:text-brand-main transition-colors">
                  Личный кабинет
                </Link>
              </li>
            </ul>
          </div>

          {/* Контакты */}
          <div>
            <h3 className="font-bold text-slate-800 mb-3">Контакты</h3>
            <ul className="space-y-2 text-sm text-slate-500">
              <li>г. Иркутск, ул. Ленина, д. 5А</li>
              <li>support@floppi.ru</li>
              <li>+7 (3952) 00-00-00</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-4 border-t border-slate-100 text-center text-xs text-slate-400">
          © 2026 Floppi Marketplace. Все права защищены.
        </div>
      </div>
    </footer>
  )
}
