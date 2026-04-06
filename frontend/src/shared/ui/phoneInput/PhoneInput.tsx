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
    <div>
      <label htmlFor="">Номер телефона</label>
      <PatternFormat
        id={id}
        format="+7 (###) ###-##-##"
        mask="_"
        value={value}
        onValueChange={(values) => onChange?.(values.value)}
        type="tel"
        className={`w-full p-3 rounded-lg border transition-all outline-none bg-obsidian/3 
          ${error ? "border-red-500" : "border-obsidian/10 focus:border-brand-main"}`}
      />
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  )
}
