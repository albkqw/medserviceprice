import { Link, useLocation } from 'react-router-dom'
import { config } from '@/lib/config'

export function Header() {
  const location = useLocation()
  const isHome = location.pathname === '/'

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
        <Link
          to="/"
          className="flex items-center gap-2 text-lg font-bold text-foreground hover:opacity-80 transition-opacity"
        >
          <span className="text-blue-600">Med</span>
          <span>ServicePrice</span>
        </Link>

        {!isHome && (
          <p className="ml-auto text-xs text-muted-foreground hidden sm:block">
            {config.appName}
          </p>
        )}
      </div>
    </header>
  )
}
