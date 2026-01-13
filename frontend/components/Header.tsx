'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  HomeIcon, 
  TableCellsIcon, 
  DocumentArrowUpIcon, 
  ClockIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  UserIcon
} from '@heroicons/react/24/outline'

interface HeaderProps {
  user: {
    username: string
    role: string
    subteam: string | null
  }
  activeTab: string
  onTabChange: (tab: string) => void
  onManageUsers?: () => void
}

export default function Header({ user, activeTab, onTabChange, onManageUsers }: HeaderProps) {
  const router = useRouter()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:8000/logout', {
        method: 'POST',
        credentials: 'include',
      })
      router.push('/login')
      router.refresh()
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <header className="sticky top-0 z-50 bg-white">
      {/* Title bar - Word style with window controls area */}
      <div className="bg-[#2B579A] text-white px-4 py-1 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium">USC Racing - Parameter Management</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="opacity-90">{user.username}</span>
          <span className="opacity-75">({user.role})</span>
        </div>
      </div>
      
      {/* Quick Access Toolbar */}
      <div className="bg-[#F2F2F2] border-b border-[#D4D4D4] px-2 py-1 flex items-center gap-1">
        <button className="p-1.5 hover:bg-[#E1E1E1] rounded-sm">
          <UserIcon className="h-4 w-4 text-[#323130]" />
        </button>
        {user.role === 'admin' && onManageUsers && (
          <button 
            onClick={onManageUsers}
            className="p-1.5 hover:bg-[#E1E1E1] rounded-sm"
            title="Manage Users"
          >
            <Cog6ToothIcon className="h-4 w-4 text-[#323130]" />
          </button>
        )}
        <div className="ml-auto flex items-center gap-1">
          <button 
            onClick={handleLogout}
            className="p-1.5 hover:bg-[#E1E1E1] rounded-sm"
            title="Logout"
          >
            <ArrowRightOnRectangleIcon className="h-4 w-4 text-[#323130]" />
          </button>
        </div>
      </div>

      {/* Ribbon Tabs - Word style */}
      <div className="bg-[#F2F2F2] border-b border-[#D4D4D4]">
        <div className="flex items-end">
          <button
            onClick={() => onTabChange('home')}
            className={`ribbon-tab ${activeTab === 'home' ? 'active' : ''}`}
          >
            <HomeIcon className="h-4 w-4 mb-0.5" />
            <span className="text-xs mt-0.5">Home</span>
          </button>
          <button
            onClick={() => onTabChange('parameters')}
            className={`ribbon-tab ${activeTab === 'parameters' ? 'active' : ''}`}
          >
            <TableCellsIcon className="h-4 w-4 mb-0.5" />
            <span className="text-xs mt-0.5">Parameters</span>
          </button>
          <button
            onClick={() => onTabChange('files')}
            className={`ribbon-tab ${activeTab === 'files' ? 'active' : ''}`}
          >
            <DocumentArrowUpIcon className="h-4 w-4 mb-0.5" />
            <span className="text-xs mt-0.5">Files</span>
          </button>
          <button
            onClick={() => onTabChange('sessions')}
            className={`ribbon-tab ${activeTab === 'sessions' ? 'active' : ''}`}
          >
            <ClockIcon className="h-4 w-4 mb-0.5" />
            <span className="text-xs mt-0.5">Sessions</span>
          </button>
          {user.role === 'admin' && (
            <button
              onClick={() => onTabChange('queue')}
              className={`ribbon-tab ${activeTab === 'queue' ? 'active' : ''}`}
            >
              <UserGroupIcon className="h-4 w-4 mb-0.5" />
              <span className="text-xs mt-0.5">Queue</span>
            </button>
          )}
        </div>
      </div>

      {/* Ribbon Content Area - Word style groups */}
      <div className="bg-white border-b-2 border-[#D4D4D4] px-4 py-3">
        <div className="flex items-center gap-6">
          {activeTab === 'home' && (
            <>
              <div className="ribbon-group">
                <div className="ribbon-group-label">View</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>All Parameters</span>
                  </button>
                </div>
              </div>
              <div className="ribbon-group">
                <div className="ribbon-group-label">Actions</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>Initialize</span>
                  </button>
                </div>
              </div>
            </>
          )}
          {activeTab === 'parameters' && (
            <>
              <div className="ribbon-group">
                <div className="ribbon-group-label">Edit</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>Edit Parameter</span>
                  </button>
                  <button className="ribbon-button">
                    <span>View History</span>
                  </button>
                </div>
              </div>
              <div className="ribbon-group">
                <div className="ribbon-group-label">Filter</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>By Subteam</span>
                  </button>
                  <button className="ribbon-button">
                    <span>Search</span>
                  </button>
                </div>
              </div>
            </>
          )}
          {activeTab === 'files' && (
            <>
              <div className="ribbon-group">
                <div className="ribbon-group-label">Upload</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>Upload File</span>
                  </button>
                </div>
              </div>
              <div className="ribbon-group">
                <div className="ribbon-group-label">Manage</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>Download</span>
                  </button>
                  <button className="ribbon-button">
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            </>
          )}
          {activeTab === 'sessions' && (
            <>
              <div className="ribbon-group">
                <div className="ribbon-group-label">View</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>All Sessions</span>
                  </button>
                </div>
              </div>
              <div className="ribbon-group">
                <div className="ribbon-group-label">Compare</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>Compare Sessions</span>
                  </button>
                </div>
              </div>
            </>
          )}
          {activeTab === 'queue' && user.role === 'admin' && (
            <>
              <div className="ribbon-group">
                <div className="ribbon-group-label">Actions</div>
                <div className="flex items-center gap-1">
                  <button className="ribbon-button">
                    <span>Approve</span>
                  </button>
                  <button className="ribbon-button">
                    <span>Reject</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
