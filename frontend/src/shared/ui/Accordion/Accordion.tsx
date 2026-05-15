"use client"

import { ReactNode, useState, useRef } from "react"
import { Icon } from "../Icons"
import { useMountTransition } from "@/shared/lib/hooks"
import clsx from "clsx"

export type AccordionItemProps = {
  title?: ReactNode // ЗАМЕНИ string на ReactNode
  content?: ReactNode
  isOpen?: boolean
  transitionDuration?: number
  onClickButton: () => void
  classNameAccordionItemOuterDiv?: string
}

const AccordionItem: React.FC<AccordionItemProps> = ({
  title,
  content,
  onClickButton,
  isOpen = false,
  transitionDuration = 300,
  classNameAccordionItemOuterDiv,
}) => {
  const divSwitchRef = useRef<HTMLDivElement>(null)

  const callbackBefore = () => {
    if (divSwitchRef.current) divSwitchRef.current.style.overflow = "hidden"
  }

  const callbackAfter = () => {
    if (divSwitchRef.current) divSwitchRef.current.style.overflow = ""
  }

  const { isVisible, shouldRender } = useMountTransition({
    isOpen,
    transitionDuration,
    callbackBeforeClose: callbackBefore,
    callbackAfterClose: callbackAfter,
    callbackBeforeOpen: callbackBefore,
    callbackAfterOpen: callbackAfter,
  })

  return (
    <div
      className={clsx(
        "mb-1 overflow-hidden transition-all duration-300",
        // Вместо бордера — легкий фон только когда открыто, либо оставляем прозрачным
        isOpen ? "bg-brand-main/5" : "bg-transparent",
        classNameAccordionItemOuterDiv,
      )}
    >
      <button
        type="button"
        onClick={onClickButton}
        // УБРАЛИ border-2. Добавили hover:bg и плавный переход цвета
        className="flex w-full justify-between p-2.5 items-center text-sm font-medium transition-colors hover:bg-brand-main/10 rounded-xl outline-none"
      >
        <span
          className={clsx(
            "transition-colors",
            isOpen ? "text-brand-main" : "text-slate-700",
          )}
        >
          {title}
        </span>

        {/* АНИМАЦИЯ СТРЕЛКИ */}
        <div
          className={clsx(
            "transition-transform duration-300 ease-in-out text-slate-400",
            isOpen && "rotate-180 text-brand-main",
          )}
        >
          <Icon.ARROWDOWN />
        </div>
      </button>

      {shouldRender && (
        <div
          ref={divSwitchRef}
          className={clsx(
            "overflow-hidden transition-all duration-300 ease-in-out",
            isVisible ? "max-h-[9999px] opacity-100" : "max-h-0 opacity-0",
          )}
        >
          <div className="py-1">
            {/* Тонкая, почти незаметная линия иерархии */}
            <div className="border-l-2 border-brand-main/20 ml-4 pl-3 space-y-1">
              {content}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

type Accordion = {
  items: Omit<AccordionItemProps, "onClickButton">[]
  classNameDiv?: string
  classNameAccordionItemOuterDiv?: string
}

export const Accordion: React.FC<Accordion> = ({
  items,
  classNameDiv,
  classNameAccordionItemOuterDiv,
}) => {
  const [openIndices, setOpenIndices] = useState<number[]>([])

  const handleItemClick = (index: number) => {
    const isOpen = openIndices.includes(index)

    if (isOpen) {
      setOpenIndices(openIndices.filter((value) => value !== index))
    } else {
      setOpenIndices([...openIndices, index])
    }
  }

  return (
    <div className={classNameDiv}>
      {items.map((item, index) => (
        <AccordionItem
          key={index}
          title={item.title}
          content={item.content}
          isOpen={openIndices.includes(index)}
          onClickButton={() => handleItemClick(index)}
          classNameAccordionItemOuterDiv={classNameAccordionItemOuterDiv}
        />
      ))}
    </div>
  )
}
