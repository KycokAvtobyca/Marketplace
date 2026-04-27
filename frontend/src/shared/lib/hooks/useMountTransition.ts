import { useEffect, useState } from "react"

interface UseMountTransitionProps {
  isOpen: boolean
  transitionDuration: number
}

export const useMountTransition = ({
  isOpen,
  transitionDuration,
}: UseMountTransitionProps) => {
  const [shouldRender, setShouldRender] = useState(isOpen)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>
    let frame: number

    if (isOpen) {
      // Сначала добавляем в DOM
      setShouldRender(true)

      // Ждем следующего кадра, чтобы браузер успел применить начальные стили (opacity: 0)
      // перед тем, как мы включим анимацию
      timer = setTimeout(() => {
        frame = requestAnimationFrame(() => {
          setIsVisible(true)
        })
      }, 10) // Небольшая задержка для стабильности в разных браузерах
    } else {
      // Сначала запускаем анимацию исчезновения
      setIsVisible(false)

      // Ждем окончания анимации и только потом удаляем из DOM
      timer = setTimeout(() => {
        setShouldRender(false)
      }, transitionDuration)
    }

    return () => {
      clearTimeout(timer)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [isOpen, transitionDuration])

  return { shouldRender, isVisible }
}
