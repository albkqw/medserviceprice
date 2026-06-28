import { useEffect, useState } from 'react'
import { SlidersHorizontal } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@/components/ui/drawer'
import { CitySelect } from '@/components/common/CitySelect'
import type { SearchFilters } from '../hooks/useSearchFilters'
import type { ServiceCategory } from '@/types/domain'
import { CATEGORY_LABELS, SORT_OPTIONS } from '@/types/domain'
import { cn } from '@/lib/utils'

interface FilterPanelProps {
  filters: SearchFilters
  onFilterChange: (updates: Partial<SearchFilters>) => void
  totalResults?: number
}

function FilterContent({ filters, onFilterChange }: Omit<FilterPanelProps, 'totalResults'>) {
  const [localMin, setLocalMin] = useState(filters.min_price?.toString() ?? '')
  const [localMax, setLocalMax] = useState(filters.max_price?.toString() ?? '')

  useEffect(() => {
    setLocalMin(filters.min_price?.toString() ?? '')
    setLocalMax(filters.max_price?.toString() ?? '')
  }, [filters.min_price, filters.max_price])

  const categories: Array<{ value: ServiceCategory | ''; label: string }> = [
    { value: '', label: 'Все категории' },
    ...Object.entries(CATEGORY_LABELS).map(([value, label]) => ({
      value: value as ServiceCategory,
      label,
    })),
  ]

  function applyPriceRange() {
    onFilterChange({
      min_price: localMin ? Number(localMin) : undefined,
      max_price: localMax ? Number(localMax) : undefined,
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="mb-2 text-sm font-medium">Сортировка</p>
        <div className="flex flex-col gap-1">
          {SORT_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => onFilterChange({ sort: opt.value })}
              className={cn(
                'rounded-md px-3 py-2 text-left text-sm transition-colors',
                filters.sort === opt.value
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-muted',
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <Separator />

      <div>
        <p className="mb-2 text-sm font-medium">Город</p>
        <CitySelect
          value={filters.city_slug}
          onChange={(slug) => onFilterChange({ city_slug: slug })}
          className="w-full"
        />
      </div>

      <Separator />

      <div>
        <p className="mb-2 text-sm font-medium">Категория</p>
        <div className="flex flex-col gap-1">
          {categories.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => onFilterChange({ category: value || undefined })}
              className={cn(
                'rounded-md px-3 py-2 text-left text-sm transition-colors',
                filters.category === value || (!filters.category && value === '')
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-muted',
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <Separator />

      <div>
        <p className="mb-2 text-sm font-medium">Цена (₸)</p>
        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder="от"
            value={localMin}
            onChange={(e) => setLocalMin(e.target.value)}
            onBlur={applyPriceRange}
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
          />
          <span className="text-muted-foreground">—</span>
          <input
            type="number"
            placeholder="до"
            value={localMax}
            onChange={(e) => setLocalMax(e.target.value)}
            onBlur={applyPriceRange}
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
          />
        </div>
      </div>
    </div>
  )
}

export function FilterPanel({ filters, onFilterChange, totalResults }: FilterPanelProps) {
  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:block w-56 flex-shrink-0">
        <div className="sticky top-20 rounded-lg border border-border bg-card p-4">
          <p className="mb-4 text-sm font-semibold text-foreground">Фильтры</p>
          <FilterContent filters={filters} onFilterChange={onFilterChange} />
        </div>
      </aside>

      {/* Mobile drawer */}
      <div className="lg:hidden">
        <Drawer>
          <DrawerTrigger asChild>
            <Button variant="outline" size="sm" className="flex items-center gap-2">
              <SlidersHorizontal className="h-4 w-4" />
              Фильтры
              {totalResults != null && (
                <span className="ml-1 text-xs text-muted-foreground">({totalResults})</span>
              )}
            </Button>
          </DrawerTrigger>
          <DrawerContent>
            <DrawerHeader>
              <DrawerTitle>Фильтры</DrawerTitle>
            </DrawerHeader>
            <div className="p-4 pb-8">
              <FilterContent filters={filters} onFilterChange={onFilterChange} />
            </div>
          </DrawerContent>
        </Drawer>
      </div>
    </>
  )
}
