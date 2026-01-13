'use client'

import { useState, useEffect } from 'react'

interface Session {
  session_id: string
  filename: string
  uploaded_at: string
  session_data: any
  parameters_snapshot: any[]
}

export default function SessionsSection() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/sessions', { credentials: 'include' })
      const data = await response.json()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Error loading sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  if (sessions.length === 0) {
    return null
  }

  return (
    <section>
      <h2 className="text-xl font-semibold text-[#323130] mb-4">Session History</h2>
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Session</th>
              <th>File</th>
              <th>Uploaded</th>
              <th>Performance</th>
              <th>Parameters</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session) => (
              <tr key={session.session_id}>
                <td className="font-medium">{session.session_id.split('_').slice(-1)[0]}</td>
                <td className="text-sm font-mono text-word-textSecondary">{session.filename}</td>
                <td className="text-word-textSecondary text-sm">
                  {new Date(session.uploaded_at).toLocaleString()}
                </td>
                <td>
                  {session.session_data?.fastest_time ? (
                    <span className="text-primary">
                      ⏱️ {session.session_data.fastest_time}
                    </span>
                  ) : (
                    <span className="text-word-textSecondary">-</span>
                  )}
                </td>
                <td className="text-word-textSecondary">
                  {session.parameters_snapshot?.length || 0} parameters
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
