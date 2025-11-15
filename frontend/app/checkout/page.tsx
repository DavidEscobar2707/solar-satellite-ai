'use client'

import { useState, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import axios from 'axios'

function CheckoutContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const location = searchParams.get('location') || ''
  const count = Number(searchParams.get('count')) || 10
  const [companyName, setCompanyName] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const unitPrice = 5.0
  const totalPrice = count * unitPrice

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!companyName.trim() || !email.trim()) {
      setError('Please fill in all required fields')
      return
    }

    setLoading(true)
    setError('')

    try {
      // In a real app, you'd create a Stripe checkout session here
      // For MVP, we'll simulate payment and redirect to success
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/api/v1/leads`, {
        location,
        max_properties: count,
      })

      // Store leads data in sessionStorage for success page
      sessionStorage.setItem('leadsData', JSON.stringify(response.data))
      sessionStorage.setItem('companyName', companyName)
      sessionStorage.setItem('email', email)

      router.push(`/success?location=${encodeURIComponent(location)}&count=${count}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Payment didn\'t complete. Please try again or use a different card.')
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen px-4 py-8 bg-white">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">Checkout</h1>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h2 className="font-semibold mb-3">What you get:</h2>
          <ul className="list-disc list-inside space-y-2 text-sm text-gray-700">
            <li>Property addresses with map links</li>
            <li>Aerial image URLs per property</li>
            <li>Backyard status (undeveloped/partial/landscaped/uncertain) + confidence</li>
            <li>Basic attributes (beds, baths, estimated price, lot size when available)</li>
            <li>CSV + JSON download</li>
          </ul>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-2">
              Company name *
            </label>
            <input
              id="companyName"
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              required
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Business email *
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700">Unit price:</span>
              <span className="font-semibold">${unitPrice.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700">Total:</span>
              <span className="text-2xl font-bold text-gray-900">${totalPrice.toFixed(2)}</span>
            </div>
            <p className="text-xs text-gray-600 mb-4">
              Payments processed by Stripe. You&apos;ll receive your leads instantly after payment.
            </p>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Processing...' : 'Pay securely'}
            </button>
          </div>
        </form>
      </div>
    </main>
  )
}

export default function CheckoutPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen px-4 py-8 bg-white">
          <div className="max-w-2xl mx-auto">
            <p className="text-gray-600">Loading checkout...</p>
          </div>
        </main>
      }
    >
      <CheckoutContent />
    </Suspense>
  )
}

