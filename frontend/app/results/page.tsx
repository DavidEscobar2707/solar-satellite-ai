 'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import axios from 'axios'

interface Lead {
  address: string
  coordinates: { lat: number; lng: number }
  zillow: {
    price?: number
    beds?: number
    baths?: number
    livingArea?: number
    lotSize?: number
  }
  imagery: {
    image_url: string
  }
  vision: {
    backyard_status: string
    backyard_confidence?: number
    notes?: string
  }
  lead_score: number
}

function ResultsContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const location = searchParams.get('location') || ''
  const [leadCount, setLeadCount] = useState(10)
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (location) {
      fetchLeads()
    }
  }, [location, leadCount])

  const fetchLeads = async () => {
    setLoading(true)
    setError('')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/api/v1/leads`, {
        location,
        max_properties: leadCount,
      })

      setLeads(response.data.leads || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'We\'re having trouble fetching data. Please wait a moment and retry.')
    } finally {
      setLoading(false)
    }
  }

  const handleContinue = () => {
    router.push(`/checkout?location=${encodeURIComponent(location)}&count=${leadCount}`)
  }

  const unitPrice = 5.0 // $5 per lead
  const totalPrice = leadCount * unitPrice

  return (
    <main className="min-h-screen px-4 py-8 bg-white">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">Backyard Leads for {location}</h1>

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="mt-4 text-gray-600">Analyzing properties...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="mb-6">
              <label htmlFor="leadCount" className="block text-sm font-medium text-gray-700 mb-2">
                Number of leads
              </label>
              <select
                id="leadCount"
                value={leadCount}
                onChange={(e) => setLeadCount(Number(e.target.value))}
                className="border-2 border-gray-300 rounded-lg px-4 py-2 focus:border-primary focus:ring-2 focus:ring-primary"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <p className="mt-2 text-sm text-gray-600">
                Leads are property-level, analyzed from aerial imagery and public data. You&apos;ll receive CSV + JSON and image links.
              </p>
            </div>

            {leads.length > 0 && (
              <div className="mb-6">
                <p className="text-lg font-semibold mb-4">Found {leads.length} leads</p>
                <div className="grid gap-4 md:grid-cols-2">
                  {leads.slice(0, 6).map((lead, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4">
                      <img
                        src={lead.imagery.image_url}
                        alt={lead.address}
                        className="w-full h-32 object-cover rounded mb-2"
                      />
                      <p className="font-medium text-sm">{lead.address}</p>
                      <p className="text-xs text-gray-600 capitalize">
                        {lead.vision.backyard_status?.replace('_', ' ')}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <div className="flex justify-between items-center mb-4">
                <span className="text-gray-700">Total:</span>
                <span className="text-2xl font-bold text-gray-900">${totalPrice.toFixed(2)}</span>
              </div>
              <button
                onClick={handleContinue}
                className="w-full bg-primary text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
              >
                Continue to checkout
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  )
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen px-4 py-8 bg-white">
          <div className="max-w-4xl mx-auto">
            <p className="text-gray-600">Loading backyard leads...</p>
          </div>
        </main>
      }
    >
      <ResultsContent />
    </Suspense>
  )
}

