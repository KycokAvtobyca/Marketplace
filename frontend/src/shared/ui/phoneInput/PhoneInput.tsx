import { PatternFormat } from "react-number-format"
import { useId } from "react"

interface PhoneInputProps {
  value?: string
  onChange?: (val: string) => void
  error?: string
}

export const PhoneInput: React.FC<PhoneInputProps> = ({
  value,
  onChange,
  error,
}) => {
  const id = useId()

  return (
    <div className="relative w-full">
      <PatternFormat
        id={id}
        format="+7 (###) ###-##-##"
        mask="_"
        value={value}
        onValueChange={(values) => onChange?.(values.value)}
        placeholder=" " // Обязательно пробел, чтобы CSS сработал
        className="peer p-2 w-full rounded-xl border-2 border-obsidian/10 bg-transparent outline-none transition-all focus:border-brand-main"
      />

      <label
        htmlFor={id}
        className="
          /* Базовые стили (состояние 'сверху') */
          absolute left-2 -top-3 p-0.5 bg-default text-sm text-brand-main transition-all cursor-text
          
          /* Состояние 'внутри' (когда плейсхолдер виден и нет фокуса) */
          peer-placeholder-shown:top-2
          peer-placeholder-shown:text-base 
          peer-placeholder-shown:text-gray-400
          
          /* Возврат наверх при фокусе */
          peer-focus:-top-3
          peer-focus:text-sm 
          peer-focus:text-brand-main
        "
      >
        Номер телефона
      </label>

      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  )
}
