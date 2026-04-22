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

interface DropDownProps {
  anchorRef: React.RefObject<HTMLElement | null>
  isOpen: boolean
  gapTop?: number
  isCenter?: boolean
  needTriangle?: boolean
  children?: React.ReactNode
}

export const DropDown = ({
  anchorRef,
  isOpen,
  gapTop = 15,
  needTriangle = true,
  children,
}: DropDownProps) => {
  const [coords, setCoords] = useState({
    top: 0,
    left: 0,
    minWidth: 0,
    transformX: "-50%",
    arrowLeft: 0,
    isTop: false,
  })
  const [shouldRender, setShouldRender] = useState(isOpen)
  const [isVisible, setIsVisible] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const updateCoords = useCallback(() => {
    console.log("resize")
    if (!anchorRef.current || !dropdownRef.current) return

    const rect = anchorRef.current.getBoundingClientRect()
    const dropdownRect = dropdownRef.current.getBoundingClientRect()

    // Базовая позиция. По вертикали - под кнопкой. По горизонтали - по центру кнопки.
    let top = rect.bottom + window.scrollY + gapTop
    let left = rect.left + rect.width / 2
    let transformX = "-50%"
    let isTop = false

    // По горизонтали
    const viewportWidth = window.innerWidth
    const dropdownWidth = dropdownRect.width

    const leftEdge = left - dropdownWidth / 2
    const rightEdge = left + dropdownWidth / 2

    if (leftEdge < 8) {
      left = 8 + window.scrollX
      transformX = "0%"
    } else if (rightEdge > viewportWidth - 8) {
      left = viewportWidth - 8 + window.scrollX
      transformX = "-100%"
    } else {
      transformX = "-50%" // Не забываем сбрасывать в дефолт, если мы в центре
    }

    // По вертикали
    const viewportHeight = window.innerHeight
    const dropdownHeight = dropdownRect.height

    const bottomEdge = rect.bottom + dropdownHeight + gapTop

    if (bottomEdge > viewportHeight) {
      // не помещается снизу - показываем сверху
      top = rect.top + window.scrollY - dropdownHeight - gapTop
      isTop = true
    }

    // Позиция стрелки
    const anchorCenter = rect.left + rect.width / 2 + window.scrollX

    let offset = 0

    if (transformX === "-50%") {
      offset = dropdownWidth / 2
    } else if (transformX === "-100%") {
      offset = dropdownWidth
    } else {
      offset = 0
    }

    let arrowLeft = anchorCenter - left + offset

    // ограничиваем, чтобы не вылезала
    arrowLeft = Math.max(16, Math.min(arrowLeft, dropdownWidth - 16))

    setCoords({
      top,
      left,
      transformX,
      minWidth: rect.width,
      arrowLeft,
      isTop,
    })
  }, [anchorRef, gapTop])

  useLayoutEffect(() => {
    if (isOpen) {
      updateCoords()
      let timer: NodeJS.Timeout
      let timer2: NodeJS.Timeout

      // Вызываем updateCoords несколько раз в последовательных кадрах
      // до браузер успеет применить стили и вычислить размеры
      let frameCount = 0
      const scheduleUpdate = () => {
        if (frameCount < 3) {
          frameCount++
          requestAnimationFrame(scheduleUpdate)
        }
        updateCoords()
      }
      requestAnimationFrame(scheduleUpdate)

      const handleResize = () => {
        clearTimeout(timer)
        document.body.style.overflow = "hidden"

        timer = setTimeout(() => {
          console.log("Ресайз закончился, обновляю координаты")
          requestAnimationFrame(updateCoords)

          timer2 = setTimeout(() => {
            document.body.style.overflow = ""
          }, 500)
        }, 300)
      }

      // Подписываемся на изменения
      window.addEventListener("resize", handleResize)
      // capture: true позволяет ловить скролл даже во внутренних контейнерах
      window.addEventListener("scroll", updateCoords, true)

      return () => {
        window.removeEventListener("resize", handleResize)
        window.removeEventListener("scroll", updateCoords)
        clearTimeout(timer)
        clearTimeout(timer2)
        document.body.style.overflow = ""
      }
    }
  }, [isOpen, updateCoords])

  useEffect(() => {
    if (isOpen) {
      setShouldRender(true)

      const frame = requestAnimationFrame(() => {
        setIsVisible(true)
      })
      return () => cancelAnimationFrame(frame)
    } else {
      setIsVisible(false)
      const timer = setTimeout(() => setShouldRender(false), 300)
      return () => clearTimeout(timer)
    }
  }, [isOpen])

  // if (!isOpen) return null

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
