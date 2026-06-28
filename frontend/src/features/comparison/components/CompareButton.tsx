import { Check, Scale } from 'lucide-react'
import { useComparison, MAX_COMPARE_CLINICS } from '../ComparisonContext'
import type { SearchResult } from '@/types/domain'

interface CompareButtonProps {
  result: SearchResult
}

export function CompareButton({ result }: CompareButtonProps) {
  const { isAdded, canAdd, add, remove } = useComparison()
  const added = isAdded(result.clinic_id, result.service_id)
  const allowed = canAdd(result.clinic_id)

  if (added) {
    return (
      <button
        onClick={() => remove(result.clinic_id, result.service_id)}
        className="flex items-center gap-1 text-xs font-medium text-primary hover:text-primary/70 transition-colors"
      >
        <Check className="h-3 w-3" />
        В сравнении
      </button>
    )
  }

  return (
    <button
      onClick={() => add(result)}
      disabled={!allowed}
      title={!allowed ? `Максимум ${MAX_COMPARE_CLINICS} клиники` : 'Добавить к сравнению'}
      className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
    >
      <Scale className="h-3 w-3" />
      Сравнить
    </button>
  )
}
