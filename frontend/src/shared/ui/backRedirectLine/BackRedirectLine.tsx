"use client"

import Image from "next/image"
import close from "@/shared/assets/icons/close.svg"
import { Suspense } from "react"
import { clsx } from "clsx"

const BackIcon = ({ className }: { className?: string }) => (
  <Image
    src={close}
    alt="Вернуться назад"
    width={18}
    height={18}
    priority
    className={className}
  />
)

interface BackRedirectLineProps {
  className?: string
  logic?: () => void
}

export const BackRedirectLine: React.FC<BackRedirectLineProps> = ({
  logic,
  className,
}) => {
  // const searchParams = useSearchParams()
  // const fromParam = searchParams?.get("from")
  // const isSafeFrom = fromParam?.startsWith("/")

  return (
    <Suspense fallback={<BackIcon className="opacity-70 cursor-not-allowed" />}>
      <div onClick={logic}>
        <BackIcon className={clsx("cursor-pointer", className)} />
      </div>
    </Suspense>
  )
}
