import { Accordion } from "@/shared/ui/Accordion"
import { BaseProperties, FilterItem } from "@/entities/filters"
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

const contentWithoutChildren = (object: BaseProperties, path?: string) => {
  const fullName = path ? `${path}__${object.slug}` : object.slug

  return (
    <div className="py-0.5">
      {" "}
      {/* Минимум отступов между чекбоксами */}
      <CheckBox
        name={fullName}
        className="text-xs sm:text-sm py-1" // Убедись, что в компоненте CheckBox можно передать размер
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
  hasParent = false, // ДОБАВИЛИ СЮДА
}) => {
  if (!object) return null

  const children = getChildrenArray(object)
  const currentPath = object.slug

  const renderContent = () => {
    return children.map((child: FilterItem, idx: number) => {
      if (hasChildren(child)) {
        return (
          <FilterList
            key={child.slug || idx}
            object={child}
            isSidebar={isSidebar}
            hasParent={true} // ПЕРЕДАЕМ ТУТ, чтобы дочерние знали, что они не корень
          />
        )
      }

      return (
        <div key={child.slug || idx} className="py-0.5">
          {contentWithoutChildren(child, currentPath)}
        </div>
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
          hasParent ? "mt-0" : "mt-1", // ТЕПЕРЬ ОШИБКИ НЕ БУДЕТ
        )}
      />
    </div>
  )
}
