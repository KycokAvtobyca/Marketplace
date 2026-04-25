"use client"

import clsx from "clsx"
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react"
import { createPortal } from "react-dom"

interface PopoverProps {
  anchorRef: React.RefObject<HTMLElement | null>
  isOpen: boolean
  onClose: () => void
  needTriangle?: boolean
  children?: React.ReactNode
  padding?: number
  transitionDuration?: number
}

export const Popover = ({
  anchorRef,
  isOpen,
  onClose,
  needTriangle = true,
  children,
  padding = 8,
  transitionDuration = 300,
}: PopoverProps) => {
  const [coords, setCoords] = useState({
    top: 0,
    left: 0,
    minWidth: 0,
    transformX: "-50%",
    arrowLeft: 0,
    isTop: false,
  })
  // shouldRender управляет наличием в DOM
  const [shouldRender, setShouldRender] = useState(isOpen)
  // isVisible - классом анимации
  const [isVisible, setIsVisible] = useState(false)

  // Создаем Ref для хранения ID текущего кадра
  const frameId = useRef<number>(0)

  const dropdownRef = useRef<HTMLDivElement | null>(null)

  const updatePosition = useCallback(() => {
    const anchor = anchorRef.current
    const dropdown = dropdownRef.current
    if (!anchor || !dropdown) return

    // Вычисляем, сколько сейчас пикселей в 1rem
    const rootFontSize = parseFloat(
      getComputedStyle(document.documentElement).fontSize,
    )
    const currentPaddingPx = (padding / 16) * rootFontSize

    // Считаем высоту и ширину экрана вычитая скроллбар
    const windowWidth =
      window.innerWidth -
      (window.innerWidth - document.documentElement.clientWidth)
    const windowHeight =
      window.innerHeight -
      (window.innerHeight - document.documentElement.clientHeight)

    const a = anchor.getBoundingClientRect()
    const d = dropdown.getBoundingClientRect()

    // Резиновый Gap (1% от вьюпорта, зажат между 5 и 14)
    // Math.max(2, Math.min(windowWidth * 0.03, 14))
    const gap = (14 / 16) * rootFontSize

    const anchorCenter = a.left + a.width / 2

    // Края по горизонтали
    const minLeft = currentPaddingPx + d.width / 2
    const maxLeft = windowWidth - currentPaddingPx - d.width / 2

    // Зажимаем центр попапа в границах экрана
    // Новый центр поповера
    const targetLeft = Math.max(minLeft, Math.min(anchorCenter, maxLeft))

    // Проверка вертикального флипа
    const isTop = a.bottom + d.height + gap > windowHeight
    const top = isTop
      ? a.top + window.scrollY - d.height - gap
      : a.bottom + window.scrollY + gap

    setCoords({
      top,
      left: targetLeft + window.scrollX,
      transformX: "-50%",
      minWidth: a.width,
      arrowLeft: d.width / 2 + (anchorCenter - targetLeft),
      isTop,
    })
  }, [anchorRef, isOpen])

  // Создаем умную версию функции обновления
  const scheduleUpdate = useCallback(() => {
    // Если обновление уже запланировано в этом кадре — ничего не делаем
    if (frameId.current) return

    // Планируем расчет на следующий кадр
    frameId.current = requestAnimationFrame(() => {
      updatePosition()
      frameId.current = 0 // Сбрасываем флаг после выполнения
    })
  }, [updatePosition])

  // До отрисовки. Добавляется пустой
  // div, благодаря setShouldRender
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>
    let frame: number

    if (isOpen) {
      // Компонент добавился в DOM,
      // но он еще не нарисован с opacity 0
      setShouldRender(true)

      timer = setTimeout(
        () => (frame = requestAnimationFrame(() => setIsVisible(true))),
        0,
      )
    } else {
      setIsVisible(false)
      timer = setTimeout(() => setShouldRender(false), transitionDuration)
    }

    return () => {
      if (timer) clearTimeout(timer)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [isOpen])

  // Сразу после того, как элемент вставился в DOM, но до
  // того как браузер успел нарисовать этот кадр на экране
  useLayoutEffect(() => {
    if (!shouldRender || !isOpen) return

    // ResizeObserver для изменений внутри элементов
    // Создаем мозг обcервера
    const observer = new ResizeObserver(scheduleUpdate)

    // Привязываем его к реальным элементам
    if (anchorRef.current) observer.observe(anchorRef.current)
    if (dropdownRef.current) observer.observe(dropdownRef.current)

    // Мгновенный расчет при монтировании
    scheduleUpdate()

    // Закрытие при клике на esc
    const handleKeyDown = (e: KeyboardEvent) => e.key === "Escape" && onClose()

    // Закрытие при стороннем клике
    const handleOutsideClick = (e: MouseEvent) => {
      const target = e.target

      if (!(target instanceof Node)) return

      if (
        !dropdownRef.current?.contains(target) &&
        !anchorRef.current?.contains(target)
      ) {
        onClose()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    window.addEventListener("mousedown", handleOutsideClick)

    // ресайз для изменений вьюпорта (когда элементы просто едут по экрану)
    window.addEventListener("resize", scheduleUpdate)

    // capture: true позволяет ловить
    // скролл даже во внутренних контейнерах
    window.addEventListener("scroll", scheduleUpdate, true)

    return () => {
      observer.disconnect()
      window.removeEventListener("keydown", handleKeyDown)
      window.removeEventListener("mousedown", handleOutsideClick)
      window.removeEventListener("resize", scheduleUpdate)
      window.removeEventListener("scroll", scheduleUpdate, true)

      // Отменяем запланированный кадр
      if (frameId.current) {
        cancelAnimationFrame(frameId.current)
        frameId.current = 0
      }
    }
  }, [shouldRender, isOpen, scheduleUpdate, onClose, anchorRef])

  if (!shouldRender) return null

  const portalRoot = document.getElementById("dropdowns")
  if (!portalRoot) return null

  return createPortal(
    <div
      ref={dropdownRef}
      style={{
        position: "absolute",
        top: `${coords.top}px`,
        left: `${coords.left}px`,
        transform: `translateX(${coords.transformX})`,
        minWidth: `${coords.minWidth}px`,
      }}
      className={`
      bg-default w-max rounded-xl shadow-default opacity-0 transition-opacity duration-300
        ${
          isVisible
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none"
        }
      `}
    >
      {needTriangle && (
        <div
          className={clsx(
            "absolute w-4.5 h-4.5 bg-default",
            coords.isTop ? "-bottom-2" : "-top-2",
          )}
          style={{
            boxShadow: "-1px -1px 4px -3px #06030c8a",
            left: coords.arrowLeft,
            transform: "translateX(-50%) rotate(45deg)",
          }}
        />
      )}

      <div className="overflow-auto p-2">{children}</div>
    </div>,
    portalRoot,
  )
}
