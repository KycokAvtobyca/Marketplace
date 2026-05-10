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
        // На этом этапе, благодаря задержке в 10ms, React уже
        // отрисовал элемент и привязал ref
        callbackBeforeClose && callbackBeforeClose()

        frame = requestAnimationFrame(() => {
          setIsVisible(true)
        })

        // Ждем завершения анимации, прежде чем вернуть скролл
        timer = setTimeout(() => {
          callbackAfterClose?.() // Ставим overflow auto после анимации
        }, transitionDuration)
      }, 10) // Небольшая задержка для стабильности в разных браузерах
    } else {
      // Сначала запускаем анимацию исчезновения
      setIsVisible(false)

      callbackBeforeOpen && callbackBeforeOpen()

      // Ждем окончания анимации и только потом удаляем из DOM
      timer = setTimeout(() => {
        setShouldRender(false)
      }, transitionDuration)

      callbackAfterOpen && callbackAfterOpen()
    }

    return () => {
      clearTimeout(timer)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [isOpen, transitionDuration])

  return { shouldRender, isVisible }
}
