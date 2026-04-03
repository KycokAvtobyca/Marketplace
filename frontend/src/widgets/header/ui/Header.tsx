import Link from "next/link"
import styles from "./Header.module.scss"

export const Header = () => {
  return (
    // Семантичный тег header
    <header className={styles.header}>
      <div className={""}>
        {/* aria-label помогает понять, куда ведет ссылка, если текст логотипа не очевиден */}
        <Link
          href="/"
          className={""}
          aria-label="На главную страницу Маркетплейса"
        >
          Флоппи
        </Link>

        {/* Семантичный тег nav для навигации */}
        <nav className={""} aria-label="Основная навигация">
          {/* Для SEO ссылки лучше оборачивать в список */}
          <ul className={""}>
            <li>
              <Link href="/catalog" className={""}>
                Каталог
              </Link>
            </li>
            <li>
              <Link href="/about" className={""}>
                О нас
              </Link>
            </li>
          </ul>
        </nav>

        {/* Блок действий (профиль/корзина) */}
        <div className="flex items-center gap-4">
          <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
            Войти
          </button>
        </div>
      </div>
    </header>
  )
}
