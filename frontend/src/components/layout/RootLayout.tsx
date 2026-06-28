import { Outlet, useLocation } from 'react-router-dom'
import { Header } from './Header'
import { Footer } from './Footer'
import { ComparisonBar } from '@/features/comparison/components/ComparisonBar'
import { useComparison } from '@/features/comparison/ComparisonContext'

function LayoutInner() {
  const { clinicCount } = useComparison()
  const location = useLocation()
  const barVisible = clinicCount > 0 && location.pathname !== '/compare'

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />
      <main className={`flex-1 ${barVisible ? 'pb-16' : ''}`}>
        <Outlet />
      </main>
      <Footer />
      <ComparisonBar />
    </div>
  )
}

export function RootLayout() {
  return <LayoutInner />
}
