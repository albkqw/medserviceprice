import type { ReactNode } from 'react'
import { TooltipProvider } from '@/components/ui/tooltip'
import { QueryProvider } from './QueryProvider'
import { ComparisonProvider } from '@/features/comparison/ComparisonContext'

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <QueryProvider>
      <ComparisonProvider>
        <TooltipProvider>{children}</TooltipProvider>
      </ComparisonProvider>
    </QueryProvider>
  )
}
