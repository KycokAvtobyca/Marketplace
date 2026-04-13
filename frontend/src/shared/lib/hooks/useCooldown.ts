import { useCallback, useEffect, useState } from "react"

interface CooldownResult {
  seconds: number
  isActive: boolean
  startCooldown: (customSeconds?: number) => void
}

export const useCooldown = (initialSeconds: number = 60): CooldownResult => {
  const [seconds, setSeconds] = useState(0)

  useEffect(() => {
    if (seconds <= 0) return

    const timer = setInterval(() => {
      setSeconds((prev) => prev - 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [seconds])

  const startCooldown = useCallback(
    (customSeconds?: number) => {
      setSeconds(customSeconds ?? initialSeconds)
    },
    [initialSeconds],
  )

  return {
    seconds: seconds,
    isActive: seconds > 0,
    startCooldown: startCooldown,
  }
}
