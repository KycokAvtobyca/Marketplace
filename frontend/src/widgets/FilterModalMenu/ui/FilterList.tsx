import { Accordion, AccordionItemProps } from "@/shared/ui/Accordion"
import {
  BaseProperties,
  Category,
  ProductType,
} from "@/entities/filters/api/interfaces"
import clsx from "clsx"
import { CheckBox } from "@/shared/ui/CheckBox"

// const categoryFilterList = (object: Category, nestingValue: number = 0) => {
//   const lastChildSlug = object.children?.[object.children.length - 1]?.slug

//   return object.children.map((childCategory) => {
//     return (
//       <FilterList
//         key={childCategory.slug}
//         object={childCategory}
//         hasParentCategory={true}
//         isLastChild={lastChildSlug === childCategory.slug}
//         nestingValue={nestingValue}
//       />
//     )
//   })
// }

// const defaultFilterList = (object?: ProductType | Category) => {
//   if (object) {
//     return (
//       <p>
//         {object.name} {object.slug}
//       </p>
//     )
//   } else {
//     return (
//       <span className="text-xs pl-4">
//         Здесь пока что ничего нет, но скоро все изменится...
//       </span>
//     )
//   }
// }

export interface FilterItem extends BaseProperties {
  children?: FilterItem[]
}

const hasChildren = (obj: any): obj is FilterItem & { children: any[] } => {
  return !!(obj && Array.isArray(obj.children) && obj.children.length > 0)
}

const contentWithoutChildren = (object: BaseProperties, path?: string) => {
  // Формируем финальное имя: путь_родителя__текущий_slug
  const fullName = path ? `${path}__${object.slug}` : object.slug

  return <CheckBox name={fullName}>{object.name}</CheckBox>
}

interface FilterListProps {
  object?: FilterItem
  title?: string
  hasParent?: boolean
  isLastChild?: boolean
  nestingLevel?: number
  parentPath?: string
}

export const FilterList: React.FC<FilterListProps> = ({
  title,
  object,
  hasParent = false,
  isLastChild,
  nestingLevel = 0,
  parentPath = "",
}) => {
  if (!object) return null

  const children = hasChildren(object) ? object.children : []
  const canExpand = children.length > 0
  const hasPlainItems = children.some((child) => !hasChildren(child))
  const currentPath = parentPath ? `${parentPath}__${object.slug}` : object.slug

  // Контент аккордеона
  const renderContent = () => {
    if (canExpand) {
      return children.map((child: FilterItem, idx: number) => {
        // КРИТИЧНО: Добавляем return перед компонентом
        if (hasChildren(child)) {
          return (
            <FilterList
              key={child.slug || idx} // Теперь slug доступен
              object={child}
              hasParent={true}
              nestingLevel={nestingLevel + 1}
              isLastChild={idx === children.length - 1}
              parentPath={currentPath}
            />
          )
        }

        // Если детей нет, рендерим "листовой" контент
        return (
          <div key={child.slug || idx}>
            {contentWithoutChildren(child, currentPath)}
          </div>
        )
      })
    }

    // Если сам текущий объект не может расширяться
    return contentWithoutChildren(object, parentPath)
  }

  const accordionItems = [
    {
      title: title || object.name,
      content: (
        <div
          style={{
            paddingLeft: hasPlainItems ? "1rem" : `${nestingLevel * 0.5}rem`,
          }}
          className={clsx(
            "flex py-2 flex-col gap-2 pl-2",
            isLastChild && hasParent && "mb-2",
            !hasParent && "p-2",
          )}
        >
          {renderContent()}
        </div>
      ),
    },
  ]

  return (
    <div
      style={{
        paddingLeft: hasParent ? `${nestingLevel * 0.5}rem` : "0",
      }}
      className="w-full"
    >
      <Accordion
        items={accordionItems}
        classNameAccordionItemOuterDiv={clsx(
          object.slug,
          hasParent ? "bg-transparent" : "bg-brand-main/20",
        )}
      />
    </div>
  )
}
