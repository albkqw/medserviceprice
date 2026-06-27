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
}

export interface ApiSearchResultItem {
  service: ApiSearchServiceInfo
  clinic: ApiSearchClinicInfo
  price_kzt: string | number  // FastAPI serializes Decimal as string
  duration_days: number | null
  parsed_at: string
  source_url: string | null   // URL of the specific price page
}

export interface ApiSearchResponse {
  query: string
  total: number
  results: ApiSearchResultItem[]
}
