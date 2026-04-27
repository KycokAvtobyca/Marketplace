import styles from "./SearchForm.module.scss"
import { Icon } from "@/shared/ui/Icons"

export const SearchForm = () => {
  return (
    <form className={styles.form}>
      <input
        name="search"
        type="search"
        placeholder="Найти товар"
        className={styles.input}
      />
      <button
        type="submit"
        className="bg-brand-main cursor-pointer px-1 h-full rounded-xl rounded-l-none"
      >
        <Icon.SEARCH />
      </button>
    </form>
  )
}
