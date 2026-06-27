import { MapPin, Phone, Clock, ExternalLink } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import type { Clinic } from '@/types/domain'

interface ClinicContactCardProps {
  clinic: Clinic
}

export function ClinicContactCard({ clinic }: ClinicContactCardProps) {
  return (
    <Card className="p-5 space-y-3">
      <p className="text-sm font-semibold text-foreground">Контакты</p>

      {clinic.address && (
        <div className="flex items-start gap-2 text-sm">
          <MapPin className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
          <span className="text-foreground">{clinic.address}</span>
        </div>
      )}

      {clinic.phone && (
        <div className="flex items-center gap-2 text-sm">
          <Phone className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
          <a
            href={`tel:${clinic.phone}`}
            className="text-primary hover:underline font-medium"
          >
            {clinic.phone}
          </a>
        </div>
      )}

      {clinic.working_hours && (
        <div className="flex items-start gap-2 text-sm">
          <Clock className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
          <span className="text-foreground">{clinic.working_hours}</span>
        </div>
      )}

      {clinic.source_url && (
        <Button
          variant="outline"
          className="w-full mt-2"
          size="sm"
          render={
            <a href={clinic.source_url} target="_blank" rel="noopener noreferrer" />
          }
        >
          <ExternalLink className="mr-2 h-3.5 w-3.5" />
          Перейти на сайт
        </Button>
      )}
    </Card>
  )
}
