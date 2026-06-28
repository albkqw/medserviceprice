import { PRICE_STALE_DAYS } from './constants'

const priceFormatter = new Intl.NumberFormat('ru-KZ', {
  style: 'decimal',
  maximumFractionDigits: 0,
})

export function formatPrice(amount: number): string {
  return `₸ ${priceFormatter.format(amount)}`
}

export function formatDate(dateString: string): string {
  return new Intl.DateTimeFormat('ru-KZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(dateString))
}

export function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString)
  const diffMs = Date.now() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Сегодня'
  if (diffDays === 1) return 'Вчера'
  if (diffDays < 7) return `${diffDays} дн. назад`
  if (diffDays < 14) return '1 нед. назад'
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} нед. назад`
  return formatDate(dateString)
}

export function pluralDays(n: number): string {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return `${n} день`
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return `${n} дня`
  return `${n} дней`
}

export type FreshnessLevel = 'fresh' | 'aging' | 'stale' | 'expired'

export function getFreshnessLevel(dateString: string): FreshnessLevel {
  const diffDays = Math.floor(
    (Date.now() - new Date(dateString).getTime()) / (1000 * 60 * 60 * 24),
  )
  if (diffDays > PRICE_STALE_DAYS) return 'expired'
  if (diffDays > 14) return 'stale'
  if (diffDays > 7) return 'aging'
  return 'fresh'
}
