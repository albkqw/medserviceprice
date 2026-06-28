export type ServiceCategory = 'lab' | 'doctor' | 'diagnostic' | 'procedure'

export type ParserSource = 'kdl' | 'invitro' | 'doq'

export const SOURCE_LABELS: Record<ParserSource, string> = {
  kdl: 'KDL',
  invitro: 'Invitro',
  doq: 'DOQ',
}

export const SOURCE_BADGE_CLASSES: Record<ParserSource, string> = {
  kdl: 'bg-blue-100 text-blue-700 border-blue-200',
  invitro: 'bg-rose-100 text-rose-700 border-rose-200',
  doq: 'bg-emerald-100 text-emerald-700 border-emerald-200',
}

export interface City {
  id: string
  name: string
  slug: string
}

export interface Clinic {
  id: string
  name: string
  city_id: string
  address: string | null
  phone: string | null
  working_hours: string | null
  source_url: string | null
}

export interface Service {
  id: string
  name: string
  category: ServiceCategory
  synonyms: string[]
}

export interface SearchResult {
  clinic_id: string
  clinic_name: string
  city: string
  address: string | null
  phone: string | null
  working_hours: string | null
  source_url: string | null
  source: ParserSource | null
  lat: number | null
  lng: number | null
  service_id: string
  service_name: string
  category: ServiceCategory
  price_kzt: number
  duration_days: number | null
  parsed_at: string
  is_active: boolean
}

export const CATEGORY_LABELS: Record<ServiceCategory, string> = {
  lab: 'Лаборатория',
  doctor: 'Приём врача',
  diagnostic: 'Диагностика',
  procedure: 'Процедура',
}

export interface ClinicService {
  service_id: string
  service_name: string
  category: ServiceCategory
  price_kzt: number
  duration_days: number | null
  parsed_at: string
  source_url: string | null
}

export const SORT_OPTIONS = [
  { value: 'price_asc', label: 'Сначала дешевле' },
  { value: 'price_desc', label: 'Сначала дороже' },
  { value: 'date_desc', label: 'Свежие данные' },
] as const

export type SortOption = (typeof SORT_OPTIONS)[number]['value']
