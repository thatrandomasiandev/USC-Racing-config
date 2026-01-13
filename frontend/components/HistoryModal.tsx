'use client'

import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { motion, AnimatePresence } from 'framer-motion'

interface HistoryItem {
  id: number
  parameter_name: string
  prior_value: string | null
  new_value: string
  updated_by: string
  updated_at: string
  comment: string | null
}

interface HistoryModalProps {
  parameterName: string
  onClose: () => void
}

export default function HistoryModal({ parameterName, onClose }: HistoryModalProps) {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [parameterName])

  const loadHistory = async () => {
    try {
      const response = await fetch(`/api/history?parameter=${encodeURIComponent(parameterName)}`, {
        credentials: 'include',
      })
      const data = await response.json()
      setHistory(data.history || [])
    } catch (error) {
      console.error('Error loading history:', error)
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
          <h2 className="text-lg font-semibold text-word-text">
            History: <span className="text-primary">{parameterName}</span>
          </h2>
          <button onClick={onClose} className="text-word-textSecondary hover:text-word-text">
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            </div>
          ) : history.length === 0 ? (
            <p className="text-word-textSecondary text-center py-8">No history available for this parameter.</p>
          ) : (
            <div className="space-y-3">
              {history.map((item) => (
                <div key={item.id} className="bg-word-surface p-4 border-l-4 border-primary">
                  <div className="flex items-center justify-between mb-2">
                    <strong className="text-word-text">{item.updated_by}</strong>
                    <span className="text-sm text-word-textSecondary">
                      {new Date(item.updated_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    {item.prior_value ? (
                      <>
                        <span className="text-word-textSecondary line-through">{item.prior_value}</span>
                        <span className="text-word-textSecondary">→</span>
                      </>
                    ) : (
                      <span className="text-word-textSecondary">Initial</span>
                    )}
                    <span className="text-primary font-semibold">{item.new_value}</span>
                  </div>
                  {item.comment && (
                    <p className="text-sm text-word-textSecondary mt-2 italic">Comment: {item.comment}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
