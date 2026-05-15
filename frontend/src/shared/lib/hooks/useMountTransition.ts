import { useEffect, useState } from "react"

interface UseMountTransitionProps {
  isOpen: boolean
  transitionDuration: number
  callbackBeforeClose?: () => void
  callbackAfterClose?: () => void
  callbackBeforeOpen?: () => void
  callbackAfterOpen?: () => void
}

export const useMountTransition = ({
  isOpen,
  transitionDuration,
  callbackBeforeClose,
  callbackAfterClose,
  callbackBeforeOpen,
  callbackAfterOpen,
}: UseMountTransitionProps) => {
  const [shouldRender, setShouldRender] = useState(isOpen)
  const [isVisible, setIsVisible] = useState(isOpen)

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = []
    let frame: number | undefined

    const later = (callback: () => void, delay: number) => {
      const timer = setTimeout(callback, delay)
      timers.push(timer)
    }

    if (isOpen) {
      callbackBeforeOpen?.()

      later(() => {
        setShouldRender(true)

        frame = requestAnimationFrame(() => {
          setIsVisible(true)
          later(() => callbackAfterOpen?.(), transitionDuration)
        })
      }, 0)
    } else {
      callbackBeforeClose?.()

      frame = requestAnimationFrame(() => {
        setIsVisible(false)
      })

      later(() => {
        setShouldRender(false)
        callbackAfterClose?.()
      }, transitionDuration)
    }

    return () => {
      timers.forEach(clearTimeout)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [
    isOpen,
    transitionDuration,
    callbackBeforeClose,
    callbackAfterClose,
    callbackBeforeOpen,
    callbackAfterOpen,
  ])

  return { shouldRender, isVisible }
}
