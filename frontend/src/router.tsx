import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { PatientHubPage } from '@/pages/PatientHubPage'
import { ProcessingPage } from '@/pages/ProcessingPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <LoginPage />,
  },
  {
    path: '/dashboard',
    element: <DashboardPage />,
  },
  {
    path: '/patient/:id',
    element: <PatientHubPage />,
  },
  {
    path: '/processing',
    element: <ProcessingPage />,
  },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
