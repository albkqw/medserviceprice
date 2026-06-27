import { useQuery } from '@tanstack/react-query'
import { getClinic } from '@/api/clinics'
import { queryKeys } from '@/api/queryKeys'

export function useClinicDetail(id: string) {
  return useQuery({
    queryKey: queryKeys.clinics.detail(id),
    queryFn: () => getClinic(id),
    enabled: Boolean(id),
    staleTime: 10 * 60 * 1000,
  })
}
