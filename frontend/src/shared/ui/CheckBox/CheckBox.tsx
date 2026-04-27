import { ReactNode } from "react"
import styles from "./CheckBox.module.scss"

interface CheckBoxProps {
  children?: ReactNode
}

export const CheckBox: React.FC<CheckBoxProps> = ({ children }) => {
  return (
    <label className="custom-checkbox">
      <input
        type="checkbox"
        className={`custom-checkbox__input ${styles.inputHidden}`}
      />
      <span className={`custom-checkbox__checkmark ${styles.checkmark}`}></span>
      {children ?? null}
    </label>
  )
}
