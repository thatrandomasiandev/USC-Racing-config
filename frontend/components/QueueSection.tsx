'use client'

import { useState, useEffect } from 'react'
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface QueueItem {
  form_id: string
  parameter_name: string
  subteam: string
  current_value: string | null
  new_value: string
  submitted_by: string
  submitted_at: string
  comment: string | null
}

export default function QueueSection() {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadQueue()
  }, [])

  const loadQueue = async () => {
    try {
      const response = await fetch('/api/queue?status=pending', { credentials: 'include' })
      const data = await response.json()
      setQueueItems(data.queue || [])
    } catch (error) {
      console.error('Error loading queue:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleProcess = async (formId: string) => {
    if (!confirm('Approve this parameter change?')) return

    try {
      const response = await fetch(`/api/queue/${formId}/process`, {
        method: 'POST',
        credentials: 'include',
      })

      if (response.ok) {
        loadQueue()
      }
    } catch (error) {
      console.error('Error processing queue item:', error)
    }
  }

  const handleReject = async (formId: string) => {
    if (!confirm('Reject this parameter change?')) return

    try {
      const response = await fetch(`/api/queue/${formId}/reject`, {
        method: 'POST',
        credentials: 'include',
      })

      if (response.ok) {
        loadQueue()
      }
    } catch (error) {
      console.error('Error rejecting queue item:', error)
    }
  }

  if (queueItems.length === 0) {
    return null
  }

  return (
    <section>
      <h2 className="text-xl font-semibold text-[#323130] mb-4">Queue (Pending Changes)</h2>
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Parameter</th>
              <th>Subteam</th>
              <th>Current → New</th>
              <th>Submitted By</th>
              <th>Comment</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {queueItems.map((item) => (
              <tr key={item.form_id}>
                <td className="font-medium">{item.parameter_name}</td>
                <td>{item.subteam}</td>
                <td>
                  <span className="text-word-textSecondary line-through">{item.current_value || 'N/A'}</span>
                  <span className="mx-2 text-word-textSecondary">→</span>
                  <span className="text-primary font-semibold">{item.new_value}</span>
                </td>
                <td>{item.submitted_by}</td>
                <td className="text-gray-400">{item.comment || '-'}</td>
                <td>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleProcess(item.form_id)}
                      className="btn-primary btn-small flex items-center gap-1"
                    >
                      <CheckIcon className="h-4 w-4" />
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(item.form_id)}
                      className="btn-secondary btn-small flex items-center gap-1"
                    >
                      <XMarkIcon className="h-4 w-4" />
                      Reject
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
