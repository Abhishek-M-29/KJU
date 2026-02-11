import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import { LandingPage } from '@/pages/LandingPage'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { PatientHubPage } from '@/pages/PatientHubPage'
import { ProcessingPage } from '@/pages/ProcessingPage'
import { ScalingPage } from '@/pages/ScalingPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/home',
    element: <Navigate to="/" replace />,
  },
  {
    path: '/login',
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
  {
    path: '/scaling',
    element: <ScalingPage />,
  },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
