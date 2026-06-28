import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { ErrorState } from '@/components/common/ErrorState'
import { PriceTag } from '@/components/common/PriceTag'
import { DataFreshness } from '@/components/common/DataFreshness'
import { ClinicHeader, ClinicHeaderSkeleton } from '@/features/clinic/components/ClinicHeader'
import { ClinicContactCard } from '@/features/clinic/components/ClinicContactCard'
import { useClinicDetail } from '@/features/clinic/hooks/useClinicDetail'
import { useClinicServices } from '@/features/clinic/hooks/useClinicServices'
import { CATEGORY_LABELS } from '@/types/domain'
import type { ServiceCategory } from '@/types/domain'

function ClinicServicesTable({ clinicId }: { clinicId: string }) {
  const { data: services = [], isLoading, isError } = useClinicServices(clinicId)

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full rounded" />
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <p className="text-sm text-muted-foreground">
        Не удалось загрузить список услуг.
      </p>
    )
  }

  if (services.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Актуальных цен не найдено. Данные обновляются ежедневно.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[520px] text-sm border-collapse">
        <thead>
          <tr className="border-b text-left text-xs text-muted-foreground">
            <th className="pb-2 pr-4 font-medium">Услуга</th>
            <th className="pb-2 pr-4 font-medium">Категория</th>
            <th className="pb-2 pr-4 font-medium text-right">Цена</th>
            <th className="pb-2 pr-4 font-medium">Актуальность</th>
            <th className="pb-2 font-medium" />
          </tr>
        </thead>
        <tbody>
          {services.map((svc) => (
            <tr key={svc.service_id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
              <td className="py-2.5 pr-4 font-medium text-foreground">{svc.service_name}</td>
              <td className="py-2.5 pr-4">
                <Badge variant="secondary" className="text-xs">
                  {CATEGORY_LABELS[svc.category as ServiceCategory] ?? svc.category}
                </Badge>
              </td>
              <td className="py-2.5 pr-4 text-right">
                <PriceTag amount={svc.price_kzt} />
              </td>
              <td className="py-2.5 pr-4">
                <DataFreshness parsedAt={svc.parsed_at} />
              </td>
              <td className="py-2.5">
                {svc.source_url && (
                  <a
                    href={svc.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-primary hover:underline whitespace-nowrap"
                  >
                    На сайт <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function ClinicPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: clinic, isLoading, isError, refetch } = useClinicDetail(id ?? '')

  if (isLoading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <Skeleton className="mb-6 h-4 w-32" />
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
          <div className="flex-1 space-y-6">
            <ClinicHeaderSkeleton />
            <Skeleton className="h-48 w-full rounded-lg" />
          </div>
          <Skeleton className="h-48 w-full rounded-lg lg:w-72" />
        </div>
      </div>
    )
  }

  if (isError || !clinic) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <ErrorState
          title="Клиника не найдена"
          description="Возможно, данная клиника была удалена или ссылка устарела."
          onRetry={isError ? refetch : undefined}
        />
        <div className="mt-4 flex justify-center">
          <Button variant="outline" onClick={() => navigate(-1)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <Link
        to={-1 as unknown as string}
        onClick={(e) => { e.preventDefault(); navigate(-1) }}
        className="mb-6 flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Назад к результатам
      </Link>

      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <div className="flex-1 min-w-0 space-y-6">
          <ClinicHeader clinic={clinic} />

          <div className="rounded-lg border border-border bg-card p-5">
            <p className="mb-4 text-sm font-semibold text-foreground">Услуги и цены</p>
            <ClinicServicesTable clinicId={id ?? ''} />
          </div>
        </div>

        <div className="lg:w-72 lg:flex-shrink-0">
          <ClinicContactCard clinic={clinic} />
        </div>
      </div>
    </div>
  )
}
