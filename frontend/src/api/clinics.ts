import type { ApiClinic } from '@/types/api'
import type { Clinic } from '@/types/domain'
import apiClient from './client'

export async function getClinic(id: string): Promise<Clinic> {
  const { data } = await apiClient.get<ApiClinic>(`/clinics/${id}`)
  return data
}
