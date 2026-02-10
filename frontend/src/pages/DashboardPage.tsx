import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, Users, AlertTriangle, Clock } from 'lucide-react'
import { Header } from '@/components/layout/Header'
import { PatientCard } from '@/components/patient/PatientCard'
import { mockPatients, mockDoctor, mockNotifications } from '@/data/patients'
import type { Patient } from '@/types/patient'

type FilterType = 'all' | 'critical' | 'warning' | 'stable'

export function DashboardPage() {
  const navigate = useNavigate()
  const [patients] = useState<Patient[]>(mockPatients)
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')

  const handleViewDetails = (patientId: string) => {
    navigate(`/patient/${patientId}`)
  }

  const filteredPatients = patients.filter((p) => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'critical') return p.riskLevel === 'critical'
    if (activeFilter === 'warning') return p.riskLevel === 'watch'
    return p.riskLevel === 'low'
  })

  const counts = {
    all: patients.length,
    critical: patients.filter((p) => p.riskLevel === 'critical').length,
    warning: patients.filter((p) => p.riskLevel === 'watch').length,
    stable: patients.filter((p) => p.riskLevel === 'low').length,
  }

  const filters: { key: FilterType; label: string; icon: React.ReactNode; color: string }[] = [
    { key: 'all', label: 'All', icon: <Users className="w-4 h-4" />, color: 'stone' },
    { key: 'critical', label: 'Critical', icon: <AlertTriangle className="w-4 h-4" />, color: 'rose' },
    { key: 'warning', label: 'Monitor', icon: <Clock className="w-4 h-4" />, color: 'amber' },
    { key: 'stable', label: 'Stable', icon: <Users className="w-4 h-4" />, color: 'emerald' },
  ]

  return (
    <div className="min-h-screen bg-stone-50">
      <Header doctor={mockDoctor} notifications={mockNotifications} />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Page title & filters */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h2 className="text-2xl font-display font-semibold text-stone-900">Patients</h2>
            <p className="text-sm text-stone-500 mt-0.5">
              {filteredPatients.length} {activeFilter === 'all' ? 'total' : activeFilter}
            </p>
          </div>

          {/* Filter pills */}
          <div className="flex gap-2">
            {filters.map((f) => {
              const isActive = activeFilter === f.key
              return (
                <button
                  key={f.key}
                  onClick={() => setActiveFilter(f.key)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                    isActive
                      ? f.color === 'stone'
                        ? 'bg-stone-900 text-white'
                        : f.color === 'rose'
                          ? 'bg-rose-500 text-white'
                          : f.color === 'amber'
                            ? 'bg-amber-500 text-white'
                            : 'bg-emerald-500 text-white'
                      : 'bg-white text-stone-600 border border-stone-200 hover:border-stone-300'
                  }`}
                >
                  {f.icon}
                  {f.label}
                  <span
                    className={`ml-1 text-xs ${isActive ? 'opacity-80' : 'text-stone-400'}`}
                  >
                    {counts[f.key]}
                  </span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Patient Cards Grid */}
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
          initial="hidden"
          animate="visible"
          variants={{
            visible: { transition: { staggerChildren: 0.05 } },
          }}
        >
          {filteredPatients.map((patient) => (
            <motion.div
              key={patient.id}
              variants={{
                hidden: { opacity: 0, y: 12 },
                visible: { opacity: 1, y: 0 },
              }}
              transition={{ duration: 0.3 }}
            >
              <PatientCard
                patient={patient}
                onViewDetails={handleViewDetails}
              />
            </motion.div>
          ))}
        </motion.div>
      </main>

      {/* FAB */}
      <motion.button
        className="fixed bottom-6 right-6 w-14 h-14 bg-primary hover:bg-primary-dark text-white rounded-full shadow-lg flex items-center justify-center transition-colors"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => alert('Add Patient')}
      >
        <Plus className="w-6 h-6" />
      </motion.button>
    </div>
  )
}
