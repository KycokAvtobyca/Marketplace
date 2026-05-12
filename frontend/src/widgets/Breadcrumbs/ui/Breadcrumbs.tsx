import Link from "next/link"

interface Crumb {
  label: string
  href?: string
}

export const Breadcrumbs = ({ crumbs }: { crumbs: Crumb[] }) => {
  return (
    <nav className="flex items-center gap-1 text-sm text-slate-500 mb-4">
      <Link href="/" className="hover:text-brand-main transition-colors">
        Главная
      </Link>
      {crumbs.map((crumb, idx) => (
        <span key={idx} className="flex items-center gap-1">
          <span className="text-slate-300">/</span>
          {crumb.href ? (
            <Link
              href={crumb.href}
              className="hover:text-brand-main transition-colors"
            >
              {crumb.label}
            </Link>
          ) : (
            <span className="text-slate-700">{crumb.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}
