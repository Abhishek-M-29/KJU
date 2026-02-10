export interface Patient {
  id: string
  name: string
  age: number
  sex: 'M' | 'F'
  avatar?: string
  symptom: string
  bloodType: string
  primaryCondition: string
  vitals: {
    heartRate: number
    bloodPressure: string
    oxygenSaturation: number
  }
  labResults: {
    glucose: number
    cholesterol: number
    creatinine: number
  }
  riskLevel: 'low' | 'watch' | 'critical'
  riskPercentage: number
  riskHistory: { date: string; score: number }[]
  medications: string[]
  allergies: string[]
  clinicalSummary: string
  medicalLicenseId?: string
  lastVisit?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface Doctor {
  id: string
  name: string
  specialty: string
  medicalLicenseId: string
}

export interface Notification {
  id: string
  type: 'urgent' | 'info' | 'warning'
  message: string
  patientId?: string
  timestamp: Date
}
