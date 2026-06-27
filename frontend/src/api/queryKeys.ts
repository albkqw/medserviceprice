import type { SearchParams } from './search'

export const queryKeys = {
  cities: () => ['cities'] as const,
  clinics: {
    detail: (id: string) => ['clinics', id] as const,
  },
  search: (params: SearchParams) => ['search', params] as const,
  suggestions: (query: string) => ['suggestions', query] as const,
}
