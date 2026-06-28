import { createContext, useCallback, useContext, useMemo } from 'react'
import type { ReactNode } from 'react'
import { useLocalStorage } from '@/hooks/useLocalStorage'
import type { SearchResult } from '@/types/domain'

export const MAX_COMPARE_CLINICS = 4

interface ComparisonContextValue {
  items: SearchResult[]
  uniqueClinics: SearchResult[]
  clinicCount: number
  isAdded: (clinicId: string, serviceId: string) => boolean
  canAdd: (clinicId: string) => boolean
  add: (result: SearchResult) => void
  remove: (clinicId: string, serviceId: string) => void
  removeClinic: (clinicId: string) => void
  clear: () => void
}

const ComparisonContext = createContext<ComparisonContextValue | null>(null)

export function ComparisonProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useLocalStorage<SearchResult[]>('comparison_items', [])

  const uniqueClinics = useMemo(() => {
    const seen = new Set<string>()
    return items.filter((item) => {
      if (seen.has(item.clinic_id)) return false
      seen.add(item.clinic_id)
      return true
    })
  }, [items])

  const clinicCount = uniqueClinics.length

  const isAdded = useCallback(
    (clinicId: string, serviceId: string) =>
      items.some((i) => i.clinic_id === clinicId && i.service_id === serviceId),
    [items],
  )

  const canAdd = useCallback(
    (clinicId: string) => {
      const ids = new Set(items.map((i) => i.clinic_id))
      return ids.has(clinicId) || ids.size < MAX_COMPARE_CLINICS
    },
    [items],
  )

  const add = useCallback(
    (result: SearchResult) => {
      setItems((prev) => {
        if (prev.some((i) => i.clinic_id === result.clinic_id && i.service_id === result.service_id))
          return prev
        const ids = new Set(prev.map((i) => i.clinic_id))
        if (!ids.has(result.clinic_id) && ids.size >= MAX_COMPARE_CLINICS) return prev
        return [...prev, result]
      })
    },
    [setItems],
  )

  const remove = useCallback(
    (clinicId: string, serviceId: string) => {
      setItems((prev) => prev.filter((i) => !(i.clinic_id === clinicId && i.service_id === serviceId)))
    },
    [setItems],
  )

  const removeClinic = useCallback(
    (clinicId: string) => {
      setItems((prev) => prev.filter((i) => i.clinic_id !== clinicId))
    },
    [setItems],
  )

  const clear = useCallback(() => setItems([]), [setItems])

  return (
    <ComparisonContext.Provider
      value={{ items, uniqueClinics, clinicCount, isAdded, canAdd, add, remove, removeClinic, clear }}
    >
      {children}
    </ComparisonContext.Provider>
  )
}

export function useComparison() {
  const ctx = useContext(ComparisonContext)
  if (!ctx) throw new Error('useComparison must be used within ComparisonProvider')
  return ctx
}
