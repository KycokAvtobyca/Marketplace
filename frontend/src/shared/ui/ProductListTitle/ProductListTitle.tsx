interface ProductListTitleProps {
  className?: string
  title?: string
}

export const ProductListTitle: React.FC<ProductListTitleProps> = ({
  className,
  title = "Все товары",
}) => {
  return <h2 className={`${className} text-xl`}>{title}</h2>
}
