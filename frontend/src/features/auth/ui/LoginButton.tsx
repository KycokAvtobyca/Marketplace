import loginIcon from "@/shared/assets/icons/login-brand.svg"
import Image from "next/image"

export const LoginButton = () => {
  return (
    <div className="flex items-center gap-4 shrink-0">
      <button className="p-1 rounded-l cursor-pointer">
        <Image src={loginIcon} alt="Войти" width={26} height={26} />
      </button>
    </div>
  )
}
