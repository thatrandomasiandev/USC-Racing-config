'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import ParametersTable from '@/components/ParametersTable'
import QueueSection from '@/components/QueueSection'
import MoTeCFiles from '@/components/MoTecFiles'
import SessionsSection from '@/components/SessionsSection'
import UserManagementModal from '@/components/UserManagementModal'

export default function Home() {
  const router = useRouter()
  const [user, setUser] = useState<{ username: string; role: string; subteam: string | null } | null>(null)
  const [loading, setLoading] = useState(true)
  const [userModalOpen, setUserModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('home')

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      // Try to fetch parameters directly - if it works, user is authenticated
      const response = await fetch('/api/parameters', {
        credentials: 'include',
      })
      
      if (response.ok) {
        // Get user info from the main page
        const mainResponse = await fetch('http://localhost:8000/', {
          credentials: 'include',
        })
        
        if (mainResponse.ok) {
          const html = await mainResponse.text()
          const usernameMatch = html.match(/Logged in as: <strong>(\w+)<\/strong>/)
          const roleMatch = html.match(/\((\w+)\)/)
          const subteamMatch = html.match(/user-subteam" content="([^"]*)"/)
          
          if (usernameMatch && roleMatch) {
            setUser({
              username: usernameMatch[1],
              role: roleMatch[1],
              subteam: subteamMatch && subteamMatch[1] ? subteamMatch[1] : null,
            })
          } else {
            router.push('/login')
          }
        } else {
          router.push('/login')
        }
      } else {
        router.push('/login')
      }
    } catch (error) {
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-word-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-word-textSecondary">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-[#F2F2F2]">
      <Header 
        user={user} 
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onManageUsers={() => setUserModalOpen(true)} 
      />
      <main className="bg-white mx-4 my-4 p-6 shadow-sm border border-[#D4D4D4]">
        {/* Word-style document area */}
        <div className="max-w-7xl mx-auto">
          {activeTab === 'home' && (
            <div>
              <h1 className="text-2xl font-semibold text-[#323130] mb-4">Welcome</h1>
              <p className="text-[#605E5C] mb-6">Select a tab above to manage parameters, files, and sessions.</p>
              {user.role === 'admin' && <QueueSection />}
            </div>
          )}
          {activeTab === 'parameters' && <ParametersTable user={user} />}
          {activeTab === 'files' && <MoTecFiles />}
          {activeTab === 'sessions' && <SessionsSection />}
          {activeTab === 'queue' && user.role === 'admin' && <QueueSection />}
        </div>
      </main>
      
      {/* Status bar - Word style */}
      <div className="fixed bottom-0 left-0 right-0 bg-[#F2F2F2] border-t border-[#D4D4D4] px-4 py-1 flex items-center justify-between text-xs text-[#605E5C]">
        <div className="flex items-center gap-4">
          <span>Ready</span>
        </div>
        <div className="flex items-center gap-4">
          <span>USC Racing Parameter Management</span>
        </div>
      </div>
      
      {user.role === 'admin' && (
        <UserManagementModal isOpen={userModalOpen} onClose={() => setUserModalOpen(false)} />
      )}
    </div>
  )
}
