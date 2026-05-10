"use client"

import { ReactNode, MouseEvent, useState, useRef } from "react"
import { Icon } from "../Icons"
import { useMountTransition } from "@/shared/lib/hooks"
import clsx from "clsx"

export type AccordionItemProps = {
  title?: string
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
        classNameAccordionItemOuterDiv
          ? classNameAccordionItemOuterDiv
          : "bg-brand-main/20",
        "rounded-xl last:mb-0 mb-2 overflow-hidden",
      )}
    >
      <button
        type="button"
        onClick={onClickButton}
        className={
          "border-2 rounded-xl border-brand-main/20 flex w-full justify-between p-2 items-center"
        }
      >
        <span>{title}</span>
        {isOpen ? <Icon.ARROWUP /> : <Icon.ARROWDOWN />}
      </button>
      {shouldRender && (
        <div
          style={{ transitionDuration: `${transitionDuration}ms` }}
          ref={divSwitchRef}
          className={clsx(
            // 1680px = 240 * 7, а 240 - это 4 закрытых аккордиона
            `grid transition-all overflow-auto max-h-420 ease`,
            isVisible ? "grid-rows-[1fr]" : "grid-rows-[0fr] overflow-hidden",
            // isVisible ? "overflow-y-auto" : "overflow-hidden",
          )}
        >
          <div className={clsx("min-h-0 space-y-2")}>{content}</div>
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
    <>
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
    </>
  )
}
