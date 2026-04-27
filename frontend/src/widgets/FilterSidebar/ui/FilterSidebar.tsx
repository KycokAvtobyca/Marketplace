interface FilterSidebarProps {
  className?: string
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({ className }) => {
  return (
    <div className={className}>
      <h2>Фильтры</h2>
    </div>
  )
}
