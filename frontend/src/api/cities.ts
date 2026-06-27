import type { ApiCity } from '@/types/api'
import type { City } from '@/types/domain'
import apiClient from './client'

function toCity(raw: ApiCity): City {
  return raw
}

export async function getCities(): Promise<City[]> {
  const { data } = await apiClient.get<ApiCity[]>('/cities')
  return data.map(toCity)
}
