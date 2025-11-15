'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'

function SuccessContent() {
  const searchParams = useSearchParams()
  const location = searchParams.get('location') || ''
  const count = Number(searchParams.get('count')) || 10
  const [companyName, setCompanyName] = useState('')
  const [email, setEmail] = useState('')
  const [leadsData, setLeadsData] = useState<any>(null)

  useEffect(() => {
    // Retrieve data from sessionStorage
    const storedLeads = sessionStorage.getItem('leadsData')
    const storedCompany = sessionStorage.getItem('companyName')
    const storedEmail = sessionStorage.getItem('email')

    if (storedLeads) {
      setLeadsData(JSON.parse(storedLeads))
    }
    if (storedCompany) setCompanyName(storedCompany)
    if (storedEmail) setEmail(storedEmail)
  }, [])

  const downloadFile = (format: 'csv' | 'json') => {
    if (!leadsData) return

    if (format === 'json') {
      const blob = new Blob([JSON.stringify(leadsData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `backyard-leads-${location.replace(/\s+/g, '-')}.json`
      a.click()
      URL.revokeObjectURL(url)
    } else {
      // For CSV, you'd need to convert the data
      // For MVP, we'll just download JSON
      downloadFile('json')
    }
  }

  return (
    <main className="min-h-screen px-4 py-8 bg-white">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-4 text-gray-900">Your backyard leads are ready</h1>
        <p className="text-lg text-gray-600 mb-8">
          Download your files below. We&apos;ve also sent a copy to {email}.
        </p>

        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <button
            onClick={() => downloadFile('csv')}
            className="bg-primary text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
          >
            Download CSV
          </button>
          <button
            onClick={() => downloadFile('json')}
            className="bg-primary text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
          >
            Download JSON
          </button>
          <a
            href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(location)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-gray-200 text-gray-800 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition-colors text-center"
          >
            Open in map
          </a>
        </div>

        {leadsData && leadsData.leads && (
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="font-semibold mb-4">Lead Summary</h2>
            <p className="text-sm text-gray-700 mb-2">
              <strong>Location:</strong> {location}
            </p>
            <p className="text-sm text-gray-700 mb-2">
              <strong>Total leads:</strong> {leadsData.count}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Company:</strong> {companyName}
            </p>
          </div>
        )}

        <div className="mt-8 text-sm text-gray-600">
          <p>Questions? Reply to the receipt email and we&apos;ll help.</p>
        </div>
      </div>
    </main>
  )
}

export default function SuccessPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen px-4 py-8 bg-white">
          <div className="max-w-3xl mx-auto">
            <p className="text-gray-600">Loading your backyard leads...</p>
          </div>
        </main>
      }
    >
      <SuccessContent />
    </Suspense>
  )
}


