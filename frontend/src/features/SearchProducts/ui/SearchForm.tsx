"use client"

import { useEffect, useState } from "react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import styles from "./SearchForm.module.scss"
import { Icon } from "@/shared/ui/Icons"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

interface SearchSuggestion {
  id: number
  name: string
  image?: string | null
  price?: number | string | null
}

export const SearchForm = () => {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [query, setQuery] = useState("")
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([])
  const [isFocused, setIsFocused] = useState(false)

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setQuery(searchParams?.get("search") || "")
    }, 0)

    return () => window.clearTimeout(timeoutId)
  }, [searchParams])

  useEffect(() => {
    const trimmedQuery = query.trim()
    if (trimmedQuery.length < 2) {
      return
    }

    const controller = new AbortController()
    const timeoutId = window.setTimeout(async () => {
      try {
        const { data } = await api.get(
          `${ROUTES.PRODUCTSCATALOG}?search=${encodeURIComponent(trimmedQuery)}`,
          { signal: controller.signal },
        )
        setSuggestions((data.results || data).slice(0, 5))
      } catch {
        if (!controller.signal.aborted) {
          setSuggestions([])
        }
      }
    }, 250)

    return () => {
      controller.abort()
      window.clearTimeout(timeoutId)
    }
  }, [query])

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const params = new URLSearchParams(searchParams?.toString() || "")
    const trimmedQuery = query.trim()

    if (trimmedQuery) {
      params.set("search", trimmedQuery)
    } else {
      params.delete("search")
    }

    const targetPath = pathname?.startsWith("/catalog") ? "/catalog" : "/catalog"
    const queryString = params.toString()

    setSuggestions([])
    router.push(queryString ? `${targetPath}?${queryString}` : targetPath)
  }

  const showSuggestions = isFocused && suggestions.length > 0

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className="relative flex h-full min-w-0 grow">
        <input
          name="search"
          type="search"
          placeholder="Найти товар"
          value={query}
          onFocus={() => setIsFocused(true)}
          onBlur={() => window.setTimeout(() => setIsFocused(false), 120)}
          onChange={(e) => {
            setQuery(e.target.value)
            if (e.target.value.trim().length < 2) {
              setSuggestions([])
            }
          }}
          className={styles.input}
        />
        {showSuggestions && (
          <div className="absolute left-0 right-0 top-[calc(100%+6px)] z-50 max-h-80 overflow-y-auto rounded-xl border border-slate-100 bg-white shadow-xl">
            {suggestions.map((item) => (
              <button
                key={item.id}
                type="button"
                onMouseDown={(event) => {
                  event.preventDefault()
                  setSuggestions([])
                  router.push(`/products/${item.id}`)
                }}
                className="flex w-full items-center gap-3 px-3 py-2 text-left text-sm hover:bg-slate-50"
              >
                <span className="line-clamp-2 min-w-0 flex-1 text-slate-800">
                  {item.name}
                </span>
                {item.price != null && (
                  <span className="hidden shrink-0 font-semibold text-brand-main min-[360px]:inline">
                    {Number(item.price).toLocaleString("ru-RU", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}{" "}
                    ₽
                  </span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
      <button
        type="submit"
        className="flex h-full shrink-0 cursor-pointer items-center justify-center rounded-xl rounded-l-none bg-brand-main px-2"
      >
        <Icon.SEARCH />
      </button>
    </form>
  )
}
