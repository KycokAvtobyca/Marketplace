import { AuthForm } from "@/features/authByPhone/ui/AuthForm"
import { Window } from "@/shared/ui/window/Window"

export const AuthWindow = () => {
  return (
    <Window
      title="Аутенфикация"
      subtitle="Пожалуйста, войдите в систему, чтобы продолжить."
      as="article"
    >
      <AuthForm />
    </Window>
  )
}
