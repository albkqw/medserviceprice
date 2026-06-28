import { useState } from 'react'
import { List, Map } from 'lucide-react'
import { SearchBar } from '@/features/search/components/SearchBar'
import { FilterPanel } from '@/features/search/components/FilterPanel'
import { ResultsList } from '@/features/search/components/ResultsList'
import { MapView } from '@/features/search/components/MapView'
import { useSearchFilters } from '@/features/search/hooks/useSearchFilters'
import { useSearchResults } from '@/features/search/hooks/useSearchResults'

type ViewMode = 'list' | 'map'

export function SearchPage() {
  const { filters, setFilters } = useSearchFilters()
  const [viewMode, setViewMode] = useState<ViewMode>('list')

  const { data: results = [], isLoading, isError, isFetching, refetch } = useSearchResults({
    query: filters.query,
    city_slug: filters.city_slug,
    min_price: filters.min_price,
    max_price: filters.max_price,
    category: filters.category,
  })

  const hasQuery = filters.query.length >= 2 && filters.city_slug

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      {/* Search bar */}
      <div className="mb-6">
        <SearchBar
          initialQuery={filters.query}
          initialCity={filters.city_slug}
          onSearch={(query, citySlug) => setFilters({ query, city_slug: citySlug })}
        />
      </div>

      {hasQuery && (
        <div className="mb-4 flex items-center justify-between gap-2">
          <p className="text-sm text-muted-foreground">
            {isLoading || isFetching ? (
              'Поиск...'
            ) : (
              <>
                Найдено <strong className="text-foreground">{results.length}</strong> результатов
                по запросу «{filters.query}»
              </>
            )}
          </p>

          <div className="flex items-center gap-2">
            {/* View toggle */}
            <div className="flex rounded-md border overflow-hidden text-sm">
              <button
                onClick={() => setViewMode('list')}
                className={`flex items-center gap-1.5 px-3 py-1.5 transition-colors ${
                  viewMode === 'list'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-background text-muted-foreground hover:bg-muted'
                }`}
              >
                <List className="h-3.5 w-3.5" />
                Список
              </button>
              <button
                onClick={() => setViewMode('map')}
                className={`flex items-center gap-1.5 px-3 py-1.5 transition-colors ${
                  viewMode === 'map'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-background text-muted-foreground hover:bg-muted'
                }`}
              >
                <Map className="h-3.5 w-3.5" />
                Карта
              </button>
            </div>

            {/* Mobile filter trigger (only in list mode) */}
            {viewMode === 'list' && (
              <div className="lg:hidden">
                <FilterPanel
                  filters={filters}
                  onFilterChange={setFilters}
                  totalResults={results.length}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {hasQuery ? (
        viewMode === 'map' ? (
          <MapView results={results} />
        ) : (
          <div className="flex gap-6">
            {/* Desktop filter sidebar */}
            <FilterPanel filters={filters} onFilterChange={setFilters} />

            {/* Results */}
            <div className="flex-1 min-w-0">
              <ResultsList
                results={results}
                isLoading={isLoading}
                isError={isError}
                onRetry={refetch}
                query={filters.query}
                sort={filters.sort}
              />
            </div>
          </div>
        )
      ) : (
        <div className="py-16 text-center text-sm text-muted-foreground">
          Введите название услуги и выберите город для поиска
        </div>
      )}
    </div>
  )
}
