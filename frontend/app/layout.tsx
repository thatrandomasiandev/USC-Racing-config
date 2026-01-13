import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'USC Racing - Parameter Management',
  description: 'Parameter management system for USC Racing subteams',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
