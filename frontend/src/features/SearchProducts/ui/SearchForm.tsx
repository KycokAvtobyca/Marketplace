"use client"

import { useEffect, useState } from "react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import styles from "./SearchForm.module.scss"
import { Icon } from "@/shared/ui/Icons"

export const SearchForm = () => {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [query, setQuery] = useState("")

  useEffect(() => {
    setQuery(searchParams?.get("search") || "")
  }, [searchParams])

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const params = new URLSearchParams(searchParams?.toString() || "")
    const trimmedQuery = query.trim()

    if (trimmedQuery) {
      params.set("search", trimmedQuery)
    } else {
      params.delete("search")
    }

    const targetPath = pathname?.startsWith("/catalog")
      ? "/catalog"
      : "/catalog"
    const queryString = params.toString()

    router.push(queryString ? `${targetPath}?${queryString}` : targetPath)
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <input
        name="search"
        type="search"
        placeholder="Найти товар"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
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
