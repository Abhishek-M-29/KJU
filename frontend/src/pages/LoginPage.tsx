import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Fingerprint } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

export function LoginPage() {
  const navigate = useNavigate()
  const [licenseId, setLicenseId] = useState('')
  const [password, setPassword] = useState('')
  const [isScanning, setIsScanning] = useState(false)
  const [scanComplete, setScanComplete] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsScanning(true)
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setScanComplete(true)
    await new Promise((resolve) => setTimeout(resolve, 400))
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-stone-100">
      {/* Decorative background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-accent/5 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-sm relative z-10"
      >
        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl shadow-stone-200/50 p-8 border border-stone-100">
          {/* Brand */}
          <div className="text-center mb-8">
            <motion.div
              className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
            >
              <span className="text-white font-bold text-lg">Kju</span>
            </motion.div>
            <h1 className="text-xl font-display font-semibold text-stone-900">Welcome back</h1>
            <p className="text-stone-500 text-sm mt-1">Sign in to continue</p>
          </div>

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <Input
              id="licenseId"
              label="Medical License ID"
              placeholder="ML-XXXX-XXXX"
              value={licenseId}
              onChange={(e) => setLicenseId(e.target.value)}
              required
            />

            <Input
              id="password"
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <div className="pt-2">
              <Button
                type="submit"
                size="lg"
                className="w-full relative overflow-hidden"
                disabled={isScanning}
              >
                <AnimatePresence mode="wait">
                  {!isScanning ? (
                    <motion.span
                      key="idle"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex items-center justify-center gap-2"
                    >
                      <Fingerprint className="w-5 h-5" />
                      Sign In
                    </motion.span>
                  ) : scanComplete ? (
                    <motion.span
                      key="complete"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex items-center justify-center gap-2 text-emerald-100"
                    >
                      ✓ Access Granted
                    </motion.span>
                  ) : (
                    <motion.span
                      key="scanning"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex items-center justify-center gap-2"
                    >
                      Verifying...
                    </motion.span>
                  )}
                </AnimatePresence>

                {isScanning && !scanComplete && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-b from-white/0 via-white/30 to-white/0"
                    animate={{ top: ['-100%', '100%'] }}
                    transition={{ duration: 1, repeat: 2, ease: 'linear' }}
                  />
                )}
              </Button>
            </div>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center text-stone-400 text-xs mt-6">
          Powered by Hybrid Agentic Swarm
        </p>
      </motion.div>
    </div>
  )
}
