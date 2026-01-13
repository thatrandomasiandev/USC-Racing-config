'use client'

import { useEffect, useState } from 'react'
import { PencilIcon, ClockIcon } from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'
import EditParameterModal from './EditParameterModal'
import HistoryModal from './HistoryModal'

interface Parameter {
  parameter_name: string
  subteam: string
  current_value: string
  updated_at: string
  updated_by: string
}

interface User {
  username: string
  role: string
  subteam: string | null
}

interface ParametersTableProps {
  user: User
}

const SUBTEAMS = ['All', 'Suspension', 'Powertrain', 'Ergo', 'DAQ', 'Aero', 'Mechanical', 'MoTeC']

export default function ParametersTable({ user }: ParametersTableProps) {
  const [parameters, setParameters] = useState<Parameter[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState(user.role === 'admin' ? 'All' : user.subteam || '')
  const [searchQuery, setSearchQuery] = useState('')
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [historyModalOpen, setHistoryModalOpen] = useState(false)
  const [selectedParameter, setSelectedParameter] = useState<Parameter | null>(null)

  useEffect(() => {
    loadParameters()
  }, [activeTab])

  const loadParameters = async () => {
    setLoading(true)
    try {
      const subteam = activeTab === 'All' ? null : activeTab
      const url = subteam 
        ? `/api/parameters?subteam=${encodeURIComponent(subteam)}` 
        : '/api/parameters'
      const response = await fetch(url, { credentials: 'include' })
      const data = await response.json()
      setParameters(data.parameters || [])
    } catch (error) {
      console.error('Error loading parameters:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredParameters = parameters.filter(p => 
    p.parameter_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.subteam.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleEdit = (param: Parameter) => {
    setSelectedParameter(param)
    setEditModalOpen(true)
  }

  const handleHistory = (param: Parameter) => {
    setSelectedParameter(param)
    setHistoryModalOpen(true)
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-[#323130] mb-4">Parameters</h2>
        <button
          onClick={async () => {
            await fetch('/api/car-parameters/initialize', { 
              method: 'POST', 
              credentials: 'include' 
            })
            loadParameters()
          }}
          className="btn-secondary btn-small"
        >
          Initialize Car Parameters
        </button>
      </div>

      {user.role === 'admin' && (
        <div className="flex gap-2 mb-4 flex-wrap border-b-2 border-border pb-2">
          {SUBTEAMS.map(subteam => (
            <button
              key={subteam}
              onClick={() => setActiveTab(subteam)}
              className={`tab-button ${activeTab === subteam ? 'active' : ''}`}
            >
              {subteam}
            </button>
          ))}
        </div>
      )}

      <div className="mb-4">
        <input
          type="text"
          placeholder="Search parameters..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input w-full max-w-md"
        />
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-word-textSecondary">Loading parameters...</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Parameter Name</th>
                <th>Subteam</th>
                <th>Current Value</th>
                <th>Last Updated</th>
                <th>Updated By</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredParameters.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-word-textSecondary">
                    No parameters found
                  </td>
                </tr>
              ) : (
                filteredParameters.map((param, index) => (
                  <motion.tr
                    key={param.parameter_name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <td className="font-medium">{param.parameter_name}</td>
                    <td>{param.subteam}</td>
                    <td className="font-semibold text-primary">{param.current_value}</td>
                    <td className="text-gray-400 text-sm">
                      {new Date(param.updated_at).toLocaleString()}
                    </td>
                    <td>{param.updated_by}</td>
                    <td>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEdit(param)}
                          className="btn-primary btn-small flex items-center gap-1"
                        >
                          <PencilIcon className="h-4 w-4" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleHistory(param)}
                          className="btn-secondary btn-small flex items-center gap-1"
                        >
                          <ClockIcon className="h-4 w-4" />
                          History
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {editModalOpen && selectedParameter && (
        <EditParameterModal
          parameter={selectedParameter}
          onClose={() => {
            setEditModalOpen(false)
            setSelectedParameter(null)
            loadParameters()
          }}
        />
      )}

      {historyModalOpen && selectedParameter && (
        <HistoryModal
          parameterName={selectedParameter.parameter_name}
          onClose={() => {
            setHistoryModalOpen(false)
            setSelectedParameter(null)
          }}
        />
      )}
    </section>
  )
}
