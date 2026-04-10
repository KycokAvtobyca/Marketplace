import { AuthForm } from "@/features/authByPhone/ui/AuthForm"
import { Window } from "@/shared/ui/window/Window"

export const AuthWindow = () => {
  return (
    <Window
      title="Вход"
      subtitle="Пожалуйста, войдите в систему, чтобы продолжить."
      as="article"
      className="max-w-96 w-full h-auto bg-default"
    >
      <AuthForm />
    </Window>
  )
}
