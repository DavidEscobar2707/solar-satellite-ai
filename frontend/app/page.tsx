'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

export default function Home() {
  const [location, setLocation] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!location.trim()) {
      setError('Please enter a location')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Validate location first
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${apiUrl}/api/v1/validate-location`, { location })
      
      // Navigate to results page with location
      router.push(`/results?location=${encodeURIComponent(location)}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'We couldn\'t find that US location. Try a city or neighborhood (e.g., "Carmel Valley, San Diego").')
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-12 bg-gradient-to-b from-white to-blue-50">
      <div className="w-full max-w-2xl">
        <h1 className="text-4xl md:text-5xl font-bold text-center mb-4 text-gray-900">
          Find Backyard Opportunities
        </h1>
        <p className="text-lg text-center text-gray-600 mb-8 max-w-xl mx-auto">
          Search and buy verified backyard development leads for your landscaping business.
        </p>

        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="location" className="sr-only">Location</label>
            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Carmel Valley, San Diego"
              className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary"
              disabled={loading}
              aria-label="Enter US city or neighborhood"
            />
            {error && (
              <p className="mt-2 text-sm text-red-600" role="alert">
                {error}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-white py-3 px-6 rounded-lg font-semibold text-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Searching...' : 'Search backyard leads'}
          </button>
        </form>
      </div>
    </main>
  )
}

