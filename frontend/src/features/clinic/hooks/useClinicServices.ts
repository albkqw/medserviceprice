import { useQuery } from '@tanstack/react-query'
import { getClinicServices } from '@/api/clinics'
import { queryKeys } from '@/api/queryKeys'

export function useClinicServices(clinicId: string) {
  return useQuery({
    queryKey: queryKeys.clinics.services(clinicId),
    queryFn: () => getClinicServices(clinicId),
    enabled: Boolean(clinicId),
    staleTime: 5 * 60 * 1000,
  })
}
