import { SearchBar } from '@/features/search/components/SearchBar'
import { FilterPanel } from '@/features/search/components/FilterPanel'
import { ResultsList } from '@/features/search/components/ResultsList'
import { useSearchFilters } from '@/features/search/hooks/useSearchFilters'
import { useSearchResults } from '@/features/search/hooks/useSearchResults'

export function SearchPage() {
  const { filters, setFilters } = useSearchFilters()

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
        <div className="mb-4 flex items-center justify-between">
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

          {/* Mobile filter trigger is rendered inside FilterPanel */}
          <div className="lg:hidden">
            <FilterPanel
              filters={filters}
              onFilterChange={setFilters}
              totalResults={results.length}
            />
          </div>
        </div>
      )}

      {hasQuery ? (
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
      ) : (
        <div className="py-16 text-center text-sm text-muted-foreground">
          Введите название услуги и выберите город для поиска
        </div>
      )}
    </div>
  )
}
