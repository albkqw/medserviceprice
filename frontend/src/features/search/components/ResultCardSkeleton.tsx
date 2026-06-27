import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export function ResultCardSkeleton() {
  return (
    <Card className="p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-5 w-20 rounded-full" />
          </div>
          <Skeleton className="h-4 w-64" />
          <div className="flex gap-4">
            <Skeleton className="h-3 w-32" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>
        <div className="flex items-center justify-between sm:flex-col sm:items-end gap-2">
          <Skeleton className="h-7 w-24" />
          <Skeleton className="h-5 w-20 rounded-full" />
        </div>
      </div>
    </Card>
  )
}
