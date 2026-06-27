import { Building2 } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import type { Clinic } from '@/types/domain'
import { useCities } from '@/hooks/useCities'

interface ClinicHeaderProps {
  clinic: Clinic
}

export function ClinicHeader({ clinic }: ClinicHeaderProps) {
  const { data: cities = [] } = useCities()
  const city = cities.find((c) => c.id === clinic.city_id)

  return (
    <div className="flex items-start gap-4">
      <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
        <Building2 className="h-7 w-7" />
      </div>
      <div>
        <h1 className="text-2xl font-bold text-foreground">{clinic.name}</h1>
        {city && <p className="mt-0.5 text-sm text-muted-foreground">{city.name}</p>}
      </div>
    </div>
  )
}

export function ClinicHeaderSkeleton() {
  return (
    <div className="flex items-start gap-4">
      <Skeleton className="h-14 w-14 rounded-xl" />
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-24" />
      </div>
    </div>
  )
}
