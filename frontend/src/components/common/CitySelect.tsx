import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useCities } from '@/hooks/useCities'
import { cn } from '@/lib/utils'

interface CitySelectProps {
  value: string
  onChange: (citySlug: string) => void
  placeholder?: string
  className?: string
}

function handleValueChange(
  onChange: (slug: string) => void,
): (value: string | null) => void {
  return (value) => { if (value) onChange(value) }
}

export function CitySelect({
  value,
  onChange,
  placeholder = 'Выберите город',
  className,
}: CitySelectProps) {
  const { data: cities = [], isLoading } = useCities()

  return (
    <Select value={value} onValueChange={handleValueChange(onChange)} disabled={isLoading}>
      <SelectTrigger className={cn('h-12 min-w-[180px]', className)}>
        <SelectValue placeholder={isLoading ? 'Загрузка...' : placeholder} />
      </SelectTrigger>
      <SelectContent>
        {cities.map((city) => (
          <SelectItem key={city.id} value={city.slug}>
            {city.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
