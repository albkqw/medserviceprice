import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/common/ErrorState'
import { ClinicHeader, ClinicHeaderSkeleton } from '@/features/clinic/components/ClinicHeader'
import { ClinicContactCard } from '@/features/clinic/components/ClinicContactCard'
import { useClinicDetail } from '@/features/clinic/hooks/useClinicDetail'

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
            <p className="mb-3 text-sm font-semibold text-foreground">Услуги и цены</p>
            <p className="text-sm text-muted-foreground">
              Детальный список услуг этой клиники появится здесь после добавления
              эндпоинта <code className="rounded bg-muted px-1 text-xs">/clinics/{'{id}'}/services</code> в бэкенд.
              Пока вы можете найти услуги этой клиники через{' '}
              <Link to="/" className="text-primary hover:underline">
                поиск на главной
              </Link>.
            </p>
          </div>
        </div>

        <div className="lg:w-72 lg:flex-shrink-0">
          <ClinicContactCard clinic={clinic} />
        </div>
      </div>
    </div>
  )
}
