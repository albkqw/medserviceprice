import type { ReactNode } from 'react'
import { TooltipProvider } from '@/components/ui/tooltip'
import { QueryProvider } from './QueryProvider'

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <QueryProvider>
      <TooltipProvider>{children}</TooltipProvider>
    </QueryProvider>
  )
}
