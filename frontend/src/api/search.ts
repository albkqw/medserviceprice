import type { ApiSearchResponse } from '@/types/api'
import type { SearchResult } from '@/types/domain'
import apiClient from './client'

export interface SearchParams {
  query: string
  city_slug: string
  min_price?: number
  max_price?: number
  category?: string
}

function toSearchResult(raw: ApiSearchResponse['results'][number]): SearchResult {
  return {
    clinic_id: raw.clinic.id,
    clinic_name: raw.clinic.name,
    city: raw.clinic.city,
    address: raw.clinic.address,
    phone: raw.clinic.phone,
    working_hours: raw.clinic.working_hours,
    source_url: raw.source_url ?? raw.clinic.website,
    service_id: raw.service.id,
    service_name: raw.service.name,
    category: raw.service.category,
    price_kzt: Number(raw.price_kzt),
    duration_days: raw.duration_days,
    parsed_at: raw.parsed_at,
    is_active: true,
  }
}

export async function searchPrices(params: SearchParams): Promise<SearchResult[]> {
  const { data } = await apiClient.get<ApiSearchResponse>('/search', { params })
  return data.results.map(toSearchResult)
}
