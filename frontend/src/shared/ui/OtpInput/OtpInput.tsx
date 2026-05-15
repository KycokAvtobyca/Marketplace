import { useFormContext } from "react-hook-form"
import { useRef, useState } from "react"
import styles from "./OtpInput.module.scss"

export const OtpInput = () => {
  const { setValue, watch } = useFormContext()
  const [wasFilled, setWasFilled] = useState(false)

  // const value = watch("sms_code") || ""
  const inputsRef = useRef<(HTMLInputElement | null)[]>([])
  const value: string = watch("sms_code") || ""

  const handleChange = (index: number, inputValue: string) => {
    const char = inputValue.replace(/\D/g, "").slice(-1)

    const arr = value.split("")
    while (arr.length < 6) arr.push("")

    arr[index] = char

    const joined = arr.join("")

    const isFilled = joined.length === 6

    if (isFilled && !wasFilled) {
      setWasFilled(true)
    }

    setValue("sms_code", joined, {
      shouldDirty: true,
      shouldValidate: isFilled || wasFilled,
    })

    // clearErrors("sms_code")

    if (char && index < 5) {
      inputsRef.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    const arr = value.split("")
    while (arr.length < 6) arr.push("")

    if (e.key === "Backspace") {
      e.preventDefault()

      if (arr[index]) {
        arr[index] = ""
      } else if (index > 0) {
        arr[index - 1] = ""
        inputsRef.current[index - 1]?.focus()
      }

      setValue("sms_code", arr.join(""), {
        shouldDirty: true,
        shouldValidate: true,
      })

      // if (!codeArray[index] && index > 0) {
      //   inputsRef.current[index - 1]?.focus()
      // }
    }
  }

  return (
    <div className="flex w-full justify-between gap-1.5">
      {[...Array(6)].map((_, i) => (
        <input
          name="code"
          key={i}
          ref={(el) => {
            inputsRef.current[i] = el
          }}
          value={value[i] || ""}
          onChange={(e) => handleChange(i, e.target.value)}
          onKeyDown={(e) => handleKeyDown(i, e)}
          inputMode="numeric"
          maxLength={1}
          className={styles.codeInput}
        />
      ))}
    </div>
  )
}
