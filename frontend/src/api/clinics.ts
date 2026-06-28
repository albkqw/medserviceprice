import type { ApiClinic, ApiClinicServiceItem } from '@/types/api'
import type { Clinic, ClinicService } from '@/types/domain'
import apiClient from './client'

export async function getClinic(id: string): Promise<Clinic> {
  const { data } = await apiClient.get<ApiClinic>(`/clinics/${id}`)
  return data
}

export async function getClinicServices(id: string): Promise<ClinicService[]> {
  const { data } = await apiClient.get<ApiClinicServiceItem[]>(`/clinics/${id}/services`)
  return data.map((item) => ({
    service_id: item.service_id,
    service_name: item.service_name,
    category: item.category,
    price_kzt: Number(item.price_kzt),
    duration_days: item.duration_days,
    parsed_at: item.parsed_at,
    source_url: item.source_url,
  }))
}
