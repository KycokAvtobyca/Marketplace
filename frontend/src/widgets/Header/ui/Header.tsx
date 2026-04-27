import { SearchForm } from "@/features/SearchProducts"
import { Logo } from "@/shared/ui/Logo/ui/Logo"
import { UserButton } from "@/features/Auth"

export const Header = () => {
  return (
    // Семантичный тег header
    <header
      className="
      flex h-[8vw] min-h-12 w-full max-w-5xl max-h-12 items-center flex-row justify-between
      gap-[3vw] backdrop-blur rounded-xl sticky p-2 py-1.5 bg-[#edede295]"
    >
      <div className="hidden min-[450px]:block">
        <Logo />
      </div>
      <SearchForm />
      <UserButton />
    </header>
  )
}
