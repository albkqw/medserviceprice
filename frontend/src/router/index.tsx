import { createBrowserRouter } from 'react-router-dom'
import { RootLayout } from '@/components/layout/RootLayout'
import { HomePage } from '@/pages/HomePage'
import { SearchPage } from '@/pages/SearchPage'
import { ClinicPage } from '@/pages/ClinicPage'
import { ComparePage } from '@/pages/ComparePage'
import { NotFoundPage } from '@/pages/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'search', element: <SearchPage /> },
      { path: 'clinics/:id', element: <ClinicPage /> },
      { path: 'compare', element: <ComparePage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
