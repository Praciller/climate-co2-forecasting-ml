import type { ReactNode, Ref } from 'react'

export interface PageHeaderProps {
  title: string
  description: string
  headingId?: string
  headingRef?: Ref<HTMLHeadingElement>
  children?: ReactNode
}

export function PageHeader({
  children,
  description,
  headingId = 'page-heading',
  headingRef,
  title,
}: PageHeaderProps) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-5">
      <div>
        <h1
          id={headingId}
          ref={headingRef}
          tabIndex={-1}
          className="text-2xl font-semibold tracking-tight sm:text-3xl"
        >
          {title}
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          {description}
        </p>
      </div>
      {children ? <div className="shrink-0">{children}</div> : null}
    </header>
  )
}
