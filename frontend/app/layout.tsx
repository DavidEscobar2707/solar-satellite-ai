import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'BackyardLeadAI - Landscaping Leads',
  description: 'Find homes with undeveloped backyards and turn them into landscaping leads',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}

