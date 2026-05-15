import styles from "./CheckBox.module.scss"

interface CheckBoxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  children?: React.ReactNode
}

export const CheckBox: React.FC<CheckBoxProps> = ({
  children,
  name,
  checked,
  onChange,
  className,
  ...props
}) => {
  return (
    <label
      className={`custom-checkbox relative flex min-w-0 cursor-pointer items-start gap-2 text-left ${className ?? ""}`}
    >
      <input
        type="checkbox"
        name={name}
        checked={checked}
        onChange={onChange}
        className={`custom-checkbox__input ${styles.inputHidden}`}
        {...props}
      />
      <span className={`custom-checkbox__checkmark ${styles.checkmark}`}></span>
      {children && (
        <span className="custom-checkbox__label min-w-0 break-words">
          {children}
        </span>
      )}
    </label>
  )
}
