import { MapPin, Phone, Clock, ExternalLink, FlaskConical, Stethoscope, Activity } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { PriceTag } from '@/components/common/PriceTag'
import { DataFreshness } from '@/components/common/DataFreshness'
import type { SearchResult, ServiceCategory } from '@/types/domain'
import { CATEGORY_LABELS } from '@/types/domain'

const categoryIcons: Record<ServiceCategory, React.ReactNode> = {
  lab: <FlaskConical className="h-3.5 w-3.5" />,
  doctor: <Stethoscope className="h-3.5 w-3.5" />,
  diagnostic: <Activity className="h-3.5 w-3.5" />,
  procedure: <Activity className="h-3.5 w-3.5" />,
}

interface ResultCardProps {
  result: SearchResult
}

export function ResultCard({ result }: ResultCardProps) {
  return (
    <Card className="p-4 transition-shadow hover:shadow-md">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <Link
              to={`/clinics/${result.clinic_id}`}
              className="text-base font-semibold text-foreground hover:text-primary hover:underline transition-colors"
            >
              {result.clinic_name}
            </Link>
            <Badge variant="secondary" className="flex items-center gap-1 text-xs">
              {categoryIcons[result.category]}
              {CATEGORY_LABELS[result.category]}
            </Badge>
          </div>

          <p className="mt-1 text-sm text-muted-foreground">{result.service_name}</p>

          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
            {result.address && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3 flex-shrink-0" />
                <span className="truncate max-w-[240px]">{result.address}</span>
              </span>
            )}
            {result.phone && (
              <a
                href={`tel:${result.phone}`}
                className="flex items-center gap-1 hover:text-foreground transition-colors"
              >
                <Phone className="h-3 w-3 flex-shrink-0" />
                {result.phone}
              </a>
            )}
            {result.working_hours && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3 flex-shrink-0" />
                {result.working_hours}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between gap-4 sm:flex-col sm:items-end">
          <PriceTag amount={result.price_kzt} />

          <div className="flex flex-col items-end gap-1.5">
            <DataFreshness parsedAt={result.parsed_at} />
            {result.duration_days != null && (
              <span className="text-xs text-muted-foreground">
                Срок: {result.duration_days} {result.duration_days === 1 ? 'день' : 'дн.'}
              </span>
            )}
            {result.source_url && (
              <a
                href={result.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-primary hover:underline"
              >
                На сайт <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}
