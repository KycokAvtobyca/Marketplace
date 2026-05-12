import { Accordion } from "@/shared/ui/Accordion"
import {
  BaseProperties,
  FilterItem,
  useFilterModalMenuStore,
} from "@/entities/filters"
import clsx from "clsx"
import { CheckBox } from "@/shared/ui/CheckBox"

// Хелпер для извлечения массива данных
const getChildrenArray = (obj: any): any[] => {
  if (!obj?.children) return []

  // Если это массив (Категории)
  if (Array.isArray(obj.children)) {
    return obj.children
  }

  // Если это объект пагинации (Атрибуты), достаем вложенный массив
  // Проверяем оба варианта ключей: 'children' или 'results'
  return obj.children.children || obj.children.results || []
}

// Обновленный hasChildren
const hasChildren = (obj: any): boolean => {
  return getChildrenArray(obj).length > 0
}

// Написать onchange для чекбокса, который будет обновлять состояние выбранных фильтров в родительском компоненте (например, через контекст или пропсы).
// Это позволит сохранять выбранные фильтры при открытии/закрытии аккордеона и при навигации по сайту.

const FilterLeaf = ({ object, path }: { object: any; path?: string }) => {
  const toggleFilter = useFilterModalMenuStore((s) => s.toggleFilter)

  // Достаем slug или id (так как у атрибутов в JSON используется id)
  const itemValue = object.slug || object.id?.toString()
  const fullName = path ? `${path}__${itemValue}` : itemValue

  // Проверяем, выбран ли текущий чекбокс
  const isChecked = useFilterModalMenuStore((s) =>
    s.selectedFilters.includes(fullName),
  )

  const handleChange = () => {
    toggleFilter(fullName)
  }

  return (
    <div className="py-0.5">
      <CheckBox
        name={fullName}
        checked={isChecked} // Связываем со стором
        onChange={handleChange} // Обработчик клика
        className="text-xs sm:text-sm py-1"
      >
        {object.name}
      </CheckBox>
    </div>
  )
}

interface FilterListProps {
  object?: FilterItem
  title?: string
  hasParent?: boolean
  isLastChild?: boolean
  nestingLevel?: number
  parentPath?: string
  isSidebar?: boolean
}

export const FilterList: React.FC<FilterListProps> = ({
  title,
  object,
  isSidebar = false,
  hasParent = false,
}) => {
  if (!object) return null

  const children = getChildrenArray(object)
  // Используем slug, если нет - id, как корень для текущего уровня
  const currentPath = object.slug

  const renderContent = () => {
    return children.map((child: any, idx: number) => {
      if (hasChildren(child)) {
        return (
          <FilterList
            key={child.slug || child.id || idx}
            object={child}
            isSidebar={isSidebar}
            hasParent={true}
          />
        )
      }

      // Используем новый компонент вместо вызова функции
      return (
        <FilterLeaf
          key={child.slug || child.id || idx}
          object={child}
          path={currentPath}
        />
      )
    })
  }

  return (
    <div className="w-full">
      <Accordion
        items={[
          {
            title: title || object.name,
            content: renderContent(),
          },
        ]}
        classNameAccordionItemOuterDiv={clsx(
          "bg-transparent",
          hasParent ? "mt-0" : "mt-1",
        )}
      />
    </div>
  )
}
