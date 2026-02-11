import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bell, Search } from 'lucide-react'
import type { Notification, Doctor } from '@/types/patient'

interface HeaderProps {
  doctor: Doctor
  notifications?: Notification[]
}

export function Header({ doctor, notifications = [] }: HeaderProps) {
  const [showNotifications, setShowNotifications] = useState(false)
  const urgentCount = notifications.filter((n) => n.type === 'urgent').length

  return (
    <header className="border-b border-stone-100 bg-white/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        {/* Left: Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center">
            <span className="text-white font-bold text-xs">Aegis</span>
          </div>
          <div className="hidden sm:block">
            <h1 className="text-base font-semibold text-stone-900 leading-tight">Medical Command</h1>
            <p className="text-xs text-stone-400">Patient Overview</p>
          </div>
        </div>

        {/* Middle: Search */}
        <div className="hidden md:flex flex-1 max-w-sm mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
            <input
              type="text"
              placeholder="Search patients..."
              className="w-full bg-stone-50 border border-stone-200 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all placeholder-stone-400"
            />
          </div>
        </div>

        {/* Right: Actions & Profile */}
        <div className="flex items-center gap-4">
          {/* Status pill */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-emerald-50 rounded-full">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse-soft" />
            <span className="text-xs font-medium text-emerald-700">On Shift</span>
          </div>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg hover:bg-stone-100 transition-colors"
            >
              <Bell className="w-5 h-5 text-stone-500" />
              {urgentCount > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-rose-500 rounded-full" />
              )}
            </button>

            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: -8, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -8, scale: 0.96 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-full mt-2 w-72 bg-white rounded-xl border border-stone-200 shadow-lg p-3 z-50"
                >
                  <h3 className="text-sm font-semibold text-stone-900 mb-2 px-1">Notifications</h3>
                  {notifications.length === 0 ? (
                    <p className="text-sm text-stone-500 px-1">No new notifications</p>
                  ) : (
                    <div className="space-y-1">
                      {notifications.map((notif) => (
                        <div
                          key={notif.id}
                          className={`p-2.5 rounded-lg text-sm ${
                            notif.type === 'urgent'
                              ? 'bg-rose-50 text-rose-800'
                              : notif.type === 'warning'
                                ? 'bg-amber-50 text-amber-800'
                                : 'bg-stone-50 text-stone-700'
                          }`}
                        >
                          <p className="font-medium">{notif.message}</p>
                          <p className="text-xs opacity-70 mt-0.5">
                            {notif.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Profile */}
          <div className="flex items-center gap-3 pl-4 border-l border-stone-200">
            <div className="text-right hidden lg:block">
              <p className="text-sm font-semibold text-stone-900">{doctor.name}</p>
              <p className="text-xs text-stone-500">{doctor.specialty}</p>
            </div>
            <div className="w-9 h-9 rounded-full bg-stone-200 flex items-center justify-center text-stone-600 font-medium text-sm">
              {doctor.name.split(' ').slice(1).map(n => n[0]).join('')}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
