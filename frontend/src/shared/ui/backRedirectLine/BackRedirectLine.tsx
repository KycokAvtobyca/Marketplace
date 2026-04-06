"use client"

import Image from "next/image"
import leftLine from "@/shared/assets/icons/arrow-left-obsidian.svg"
import Link from "next/link"
import { Suspense } from "react"
import { useSearchParams } from "next/navigation"

const BackIcon = ({ className }: { className?: string }) => (
  <Image
    src={leftLine}
    alt="Вернуться назад"
    width={30}
    height={30}
    priority
    className={className}
  />
)

const BackRedirectLineContent = () => {
  const searchParams = useSearchParams()
  const fromParam = searchParams?.get("from")
  const isSafeFrom = fromParam?.startsWith("/")

  return (
    <Link href={(isSafeFrom ? fromParam : null) || "/"} prefetch={false}>
      <BackIcon />
    </Link>
  )
}

export const BackRedirectLine = () => (
  <Suspense fallback={<BackIcon className="opacity-70" />}>
    <BackRedirectLineContent />
  </Suspense>
)
