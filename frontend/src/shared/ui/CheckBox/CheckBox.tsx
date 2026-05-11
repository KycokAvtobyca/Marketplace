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
      className={`custom-checkbox text-center space-x-1 flex items-center cursor-pointer ${className}`}
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
      {children && <span className="custom-checkbox__label">{children}</span>}
    </label>
  )
}
