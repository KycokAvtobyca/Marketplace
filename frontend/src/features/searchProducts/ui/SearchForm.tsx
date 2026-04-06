import Image from "next/image"
import searchIcon from "@/shared/assets/icons/search-white.svg"
import styles from "./SearchForm.module.scss"

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
        <Image src={searchIcon} alt="Поиск" width={24} height={24} />
      </button>
    </form>
  )
}
