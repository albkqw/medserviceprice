import { useQuery } from '@tanstack/react-query'
import { getCities } from '@/api/cities'
import { queryKeys } from '@/api/queryKeys'

export function useCities() {
  return useQuery({
    queryKey: queryKeys.cities(),
    queryFn: getCities,
    staleTime: Infinity,
  })
}
