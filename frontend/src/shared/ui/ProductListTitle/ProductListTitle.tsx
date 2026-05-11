interface PageTitleProps {
  className?: string
  title?: string
}

export const PageTitle: React.FC<PageTitleProps> = ({
  className,
  title = "Главная страница",
}) => {
  return <h2 className={`${className} text-xl`}>{title}</h2>
}
