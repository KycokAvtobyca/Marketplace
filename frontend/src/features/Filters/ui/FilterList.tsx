import { Accordion } from "@/shared/ui/Accordion"
import {
  BaseProperties,
  FilterItem,
  useFilterModalMenuStore,
} from "@/entities/filters"
import clsx from "clsx"
import { CheckBox } from "@/shared/ui/CheckBox"

interface FilterNode extends BaseProperties {
  id?: number | string
  children?:
    | FilterNode[]
    | {
        children?: FilterNode[]
        results?: FilterNode[]
      }
}

const getChildrenArray = (obj: FilterNode): FilterNode[] => {
  if (!obj.children) return []

  if (Array.isArray(obj.children)) {
    return obj.children
  }

  return obj.children.children || obj.children.results || []
}

const hasChildren = (obj: FilterNode): boolean => {
  return getChildrenArray(obj).length > 0
}

const sortChildrenFirst = (items: FilterNode[]): FilterNode[] => {
  return [...items].sort((a, b) => {
    const aHasChildren = hasChildren(a)
    const bHasChildren = hasChildren(b)

    if (aHasChildren !== bHasChildren) {
      return aHasChildren ? -1 : 1
    }

    return a.name.localeCompare(b.name, "ru")
  })
}

const FilterLeaf = ({ object, path }: { object: FilterNode; path?: string }) => {
  const toggleFilter = useFilterModalMenuStore((s) => s.toggleFilter)

  const itemValue = object.slug || object.id?.toString()
  const fullName = itemValue ? (path ? `${path}__${itemValue}` : itemValue) : ""

  const isChecked = useFilterModalMenuStore((s) =>
    s.selectedFilters.includes(fullName),
  )

  if (!itemValue) return null

  return (
    <div className="py-0.5">
      <CheckBox
        name={fullName}
        checked={isChecked}
        onChange={() => toggleFilter(fullName)}
        className="text-xs sm:text-sm py-1"
      >
        {object.name}
      </CheckBox>
    </div>
  )
}

interface FilterListProps {
  object?: FilterItem | FilterNode
  title?: string
  hasParent?: boolean
  isLastChild?: boolean
  nestingLevel?: number
  parentPath?: string
  isSidebar?: boolean
  loadMore?: {
    isLoading: boolean
    onClick: () => void
  }
}

export const FilterList: React.FC<FilterListProps> = ({
  title,
  object,
  isSidebar = false,
  hasParent = false,
  parentPath,
  loadMore,
}) => {
  if (!object) return null

  const children = getChildrenArray(object)
  const currentPath = parentPath || object.slug

  const renderContent = () => {
    return (
      <>
        {sortChildrenFirst(children).map((child, idx) => {
          if (hasChildren(child)) {
            return (
              <FilterList
                key={child.slug || child.id || idx}
                object={child}
                isSidebar={isSidebar}
                hasParent={true}
                parentPath={currentPath}
              />
            )
          }

          return (
            <FilterLeaf
              key={child.slug || child.id || idx}
              object={child}
              path={currentPath}
            />
          )
        })}
        {loadMore && (
          <button
            type="button"
            onClick={loadMore.onClick}
            disabled={loadMore.isLoading}
            className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-brand-main transition hover:border-brand-main disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loadMore.isLoading ? "Загрузка..." : "Показать еще"}
          </button>
        )
        }
      </>
    )
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
