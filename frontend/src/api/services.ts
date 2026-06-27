import type { ApiService } from '@/types/api'
import type { Service } from '@/types/domain'
import apiClient from './client'

export async function getServiceSuggestions(query: string): Promise<Service[]> {
  const { data } = await apiClient.get<ApiService[]>('/services', {
    params: { query, limit: 8 },
  })
  return data
}
