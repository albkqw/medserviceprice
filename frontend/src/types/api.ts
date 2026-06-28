export type ApiServiceCategory = 'lab' | 'doctor' | 'diagnostic' | 'procedure'

export interface ApiCity {
  id: string
  name: string
  slug: string
}

export interface ApiClinic {
  id: string
  name: string
  city_id: string
  address: string | null
  phone: string | null
  working_hours: string | null
  source_url: string | null
}

export interface ApiService {
  id: string
  name: string
  category: ApiServiceCategory
  synonyms: string[]
}

// Actual backend SearchResponse shape (nested)
export interface ApiSearchServiceInfo {
  id: string
  name: string
  category: ApiServiceCategory
}

export interface ApiSearchClinicInfo {
  id: string
  name: string
  city: string
  address: string | null
  phone: string | null
  working_hours: string | null
  website: string | null
  lat: number | null
  lng: number | null
}

export interface ApiSearchResultItem {
  service: ApiSearchServiceInfo
  clinic: ApiSearchClinicInfo
  price_kzt: string | number  // FastAPI serializes Decimal as string
  duration_days: number | null
  parsed_at: string
  source_url: string | null
  source_slug: string | null  // parser source identifier: 'kdl' | 'invitro' | 'doq'
}

export interface ApiSearchResponse {
  query: string
  total: number
  results: ApiSearchResultItem[]
}

export interface ApiClinicServiceItem {
  service_id: string
  service_name: string
  category: ApiServiceCategory
  price_kzt: string | number
  duration_days: number | null
  parsed_at: string
  source_url: string | null
}
