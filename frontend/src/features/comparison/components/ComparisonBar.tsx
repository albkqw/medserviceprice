import { X } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useComparison } from '../ComparisonContext'

export function ComparisonBar() {
  const { uniqueClinics, clinicCount, removeClinic, clear } = useComparison()
  const location = useLocation()

  // Don't render the bar on the compare page itself
  if (location.pathname === '/compare') return null

  const visible = clinicCount > 0

  const label =
    clinicCount === 1
      ? '1 клиника'
      : clinicCount < 5
        ? `${clinicCount} клиники`
        : `${clinicCount} клиник`

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-50 border-t bg-background shadow-[0_-4px_16px_rgba(0,0,0,0.08)] transition-transform duration-300 ${
        visible ? 'translate-y-0' : 'translate-y-full'
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-3">
        <span className="shrink-0 text-sm font-medium text-muted-foreground">Сравнение:</span>

        <div className="flex min-w-0 flex-1 items-center gap-2 overflow-x-auto">
          {uniqueClinics.map((clinic) => (
            <span
              key={clinic.clinic_id}
              className="flex shrink-0 items-center gap-1.5 rounded-full border bg-secondary px-3 py-1 text-xs font-medium"
            >
              <span className="max-w-[140px] truncate">{clinic.clinic_name}</span>
              <button
                onClick={() => removeClinic(clinic.clinic_id)}
                className="text-muted-foreground hover:text-destructive transition-colors"
                aria-label={`Убрать ${clinic.clinic_name}`}
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>

        <button
          onClick={clear}
          className="shrink-0 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          Очистить
        </button>

        <Link
          to="/compare"
          className="shrink-0 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Сравнить {label}
        </Link>
      </div>
    </div>
  )
}
