import { Suspense } from "react"
import { clsx } from "clsx"

interface SuspenseIconProps {
  Icon: React.FC<{ className?: string }>
  className?: string
  logic?: () => void
}

export const SuspenseIcon: React.FC<SuspenseIconProps> = ({
  Icon,
  className,
  logic,
}) => {
  // const searchParams = useSearchParams()
  // const fromParam = searchParams?.get("from")
  // const isSafeFrom = fromParam?.startsWith("/")

  return (
    <Suspense fallback={<Icon className="opacity-70 cursor-not-allowed" />}>
      <div onClick={logic}>
        <Icon className={clsx("cursor-pointer", className)} />
      </div>
    </Suspense>
  )
}
