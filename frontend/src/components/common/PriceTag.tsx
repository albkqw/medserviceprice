import { cn } from '@/lib/utils'
import { formatPrice } from '@/lib/formatters'

interface PriceTagProps {
  amount: number
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

const sizeClasses = {
  sm: 'text-base font-semibold',
  md: 'text-xl font-bold',
  lg: 'text-3xl font-bold',
}

export function PriceTag({ amount, className, size = 'md' }: PriceTagProps) {
  return (
    <span className={cn('text-primary tabular-nums', sizeClasses[size], className)}>
      {formatPrice(amount)}
    </span>
  )
}
