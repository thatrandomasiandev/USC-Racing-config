'use client'

import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { motion, AnimatePresence } from 'framer-motion'

interface Parameter {
  parameter_name: string
  subteam: string
  current_value: string
  updated_at: string
  updated_by: string
}

interface EditParameterModalProps {
  parameter: Parameter
  onClose: () => void
}

export default function EditParameterModal({ parameter, onClose }: EditParameterModalProps) {
  const [newValue, setNewValue] = useState(parameter.current_value)
  const [comment, setComment] = useState('')
  const [queue, setQueue] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    try {
      const response = await fetch('/api/parameters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          parameter_name: parameter.parameter_name,
          subteam: parameter.subteam,
          new_value: newValue,
          comment: comment || null,
          queue: queue,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({
          text: data.status === 'queued' 
            ? 'Parameter change added to queue for admin approval'
            : `Parameter updated successfully${data.ldx_files_updated ? ` (${data.ldx_files_updated} LDX files updated)` : ''}`,
          type: 'success',
        })
        setTimeout(() => {
          onClose()
        }, 1500)
      } else {
        setMessage({ text: data.detail || 'Error updating parameter', type: 'error' })
      }
    } catch (error) {
      setMessage({ text: 'Network error. Please try again.', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="modal-overlay"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="modal-content"
          onClick={(e) => e.stopPropagation()}
        >
        <div className="flex items-center justify-between p-4 border-b border-word-border bg-ribbon">
          <h2 className="text-lg font-semibold text-word-text">Edit Parameter</h2>
          <button onClick={onClose} className="text-word-textSecondary hover:text-word-text">
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-word-text mb-1.5">
              Parameter Name
            </label>
            <input
              type="text"
              value={parameter.parameter_name}
              disabled
              className="input w-full bg-word-surface opacity-60 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-word-text mb-1.5">
              Current Value
            </label>
            <input
              type="text"
              value={parameter.current_value}
              disabled
              className="input w-full bg-word-surface opacity-60 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-word-text mb-1.5">
              New Value
            </label>
            <input
              type="text"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              required
              className="input w-full"
              placeholder="Enter new value"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-word-text mb-1.5">
              Comment (Optional)
            </label>
            <input
              type="text"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="input w-full"
              placeholder="Brief comment about this change"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="queue"
              checked={queue}
              onChange={(e) => setQueue(e.target.checked)}
              className="w-4 h-4 text-primary bg-white border-word-border rounded-sm focus:ring-primary"
            />
            <label htmlFor="queue" className="text-sm text-word-text">
              Add to queue (requires admin approval)
            </label>
          </div>

          {message && (
            <div
              className={`p-3 border ${
                message.type === 'success'
                  ? 'bg-green-50 border-green-300 text-green-700'
                  : 'bg-red-50 border-red-300 text-red-700'
              }`}
            >
              {message.text}
            </div>
          )}

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Updating...' : 'Update Parameter'}
            </button>
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
          </div>
        </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
