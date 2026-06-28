import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, ExternalLink, MapPin, Phone, Trash2 } from 'lucide-react'
import { useComparison } from '@/features/comparison/ComparisonContext'
import { formatPrice } from '@/lib/formatters'
import { DataFreshness } from '@/components/common/DataFreshness'
import type { SearchResult } from '@/types/domain'

function pluralClinics(n: number) {
  if (n === 1) return '1 клиника'
  if (n < 5) return `${n} клиники`
  return `${n} клиник`
}

export function ComparePage() {
  const { items, uniqueClinics, removeClinic, clear } = useComparison()

  // Unique services (rows), preserving insertion order
  const uniqueServices = useMemo(() => {
    const seen = new Set<string>()
    return items.filter((item) => {
      if (seen.has(item.service_id)) return false
      seen.add(item.service_id)
      return true
    })
  }, [items])

  // Fast lookup: `${clinic_id}|${service_id}` → SearchResult
  const priceMap = useMemo(() => {
    const map = new Map<string, SearchResult>()
    items.forEach((item) => map.set(`${item.clinic_id}|${item.service_id}`, item))
    return map
  }, [items])

  // Min price per service row (for highlighting)
  const minPricePerService = useMemo(() => {
    const mins = new Map<string, number>()
    uniqueServices.forEach((svc) => {
      const prices = uniqueClinics
        .map((c) => priceMap.get(`${c.clinic_id}|${svc.service_id}`)?.price_kzt)
        .filter((p): p is number => p !== undefined)
      if (prices.length > 0) mins.set(svc.service_id, Math.min(...prices))
    })
    return mins
  }, [uniqueServices, uniqueClinics, priceMap])

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-20 text-center">
        <p className="text-lg text-muted-foreground">Нет клиник для сравнения</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Найдите услугу и нажмите «Сравнить» на карточке клиники
        </p>
        <Link
          to="/search"
          className="mt-6 inline-flex items-center gap-2 text-sm text-primary hover:underline"
        >
          <ArrowLeft className="h-4 w-4" />
          Перейти к поиску
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Page header */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <Link
            to="/search"
            className="mb-2 flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Назад к поиску
          </Link>
          <h1 className="text-2xl font-bold">Сравнение клиник</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {pluralClinics(uniqueClinics.length)}, {uniqueServices.length}{' '}
            {uniqueServices.length === 1 ? 'услуга' : uniqueServices.length < 5 ? 'услуги' : 'услуг'}
          </p>
        </div>
        <button
          onClick={clear}
          className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-destructive transition-colors"
        >
          <Trash2 className="h-4 w-4" />
          Очистить всё
        </button>
      </div>

      {/* Comparison table */}
      <div className="overflow-x-auto rounded-xl border">
        <table className="w-full min-w-[600px] border-collapse text-sm">
          <thead>
            <tr className="border-b bg-muted/40">
              {/* Service column header */}
              <th className="sticky left-0 z-10 bg-muted/40 w-48 min-w-[180px] px-4 py-3 text-left font-semibold text-muted-foreground">
                Услуга
              </th>

              {/* One column per clinic */}
              {uniqueClinics.map((clinic) => (
                <th
                  key={clinic.clinic_id}
                  className="min-w-[200px] px-4 py-3 text-left align-top"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <Link
                        to={`/clinics/${clinic.clinic_id}`}
                        className="font-semibold text-foreground hover:text-primary hover:underline transition-colors"
                      >
                        {clinic.clinic_name}
                      </Link>
                      {clinic.address && (
                        <p className="mt-1 flex items-start gap-1 text-xs font-normal text-muted-foreground">
                          <MapPin className="mt-0.5 h-3 w-3 shrink-0" />
                          <span className="line-clamp-2">{clinic.address}</span>
                        </p>
                      )}
                      {clinic.phone && (
                        <a
                          href={`tel:${clinic.phone}`}
                          className="mt-0.5 flex items-center gap-1 text-xs font-normal text-muted-foreground hover:text-foreground transition-colors"
                        >
                          <Phone className="h-3 w-3 shrink-0" />
                          {clinic.phone}
                        </a>
                      )}
                    </div>
                    <button
                      onClick={() => removeClinic(clinic.clinic_id)}
                      className="shrink-0 text-muted-foreground hover:text-destructive transition-colors"
                      aria-label={`Убрать ${clinic.clinic_name}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {uniqueServices.map((svc, rowIndex) => {
              const minPrice = minPricePerService.get(svc.service_id)
              const offersCount = uniqueClinics.filter(
                (c) => priceMap.has(`${c.clinic_id}|${svc.service_id}`),
              ).length

              return (
                <tr
                  key={svc.service_id}
                  className={rowIndex % 2 === 0 ? 'bg-background' : 'bg-muted/20'}
                >
                  {/* Service name */}
                  <td className="sticky left-0 z-10 border-r px-4 py-4 font-medium bg-inherit">
                    <span>{svc.service_name}</span>
                    {offersCount < uniqueClinics.length && (
                      <span className="ml-2 text-xs text-muted-foreground">
                        ({offersCount} из {uniqueClinics.length})
                      </span>
                    )}
                  </td>

                  {/* Price cells */}
                  {uniqueClinics.map((clinic) => {
                    const item = priceMap.get(`${clinic.clinic_id}|${svc.service_id}`)
                    const isCheapest =
                      item !== undefined &&
                      minPrice !== undefined &&
                      item.price_kzt === minPrice &&
                      offersCount > 1

                    return (
                      <td key={clinic.clinic_id} className="px-4 py-4 align-top">
                        {item ? (
                          <div className="flex flex-col gap-1">
                            <span
                              className={`text-base font-bold ${isCheapest ? 'text-green-600 dark:text-green-400' : 'text-foreground'}`}
                            >
                              {isCheapest && (
                                <span className="mr-1 text-xs font-normal">↓</span>
                              )}
                              {formatPrice(item.price_kzt)}
                            </span>
                            <DataFreshness parsedAt={item.parsed_at} />
                            {item.source_url && (
                              <a
                                href={item.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-xs text-primary hover:underline"
                              >
                                На сайт <ExternalLink className="h-3 w-3" />
                              </a>
                            )}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-xs text-muted-foreground">
        ↓ — наименьшая цена среди сравниваемых клиник. Цены актуальны на дату последнего обновления.
      </p>
    </div>
  )
}
