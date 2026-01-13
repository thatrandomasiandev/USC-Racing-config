'use client'

import { useState, useEffect } from 'react'
import { XMarkIcon, TrashIcon } from '@heroicons/react/24/outline'
import { motion, AnimatePresence } from 'framer-motion'

interface User {
  id: number
  username: string
  role: string
  subteam: string | null
  created_at: string
  password?: string
}

interface DeletedUser {
  username: string
  role: string
  subteam: string | null
  deleted_at: string
  deleted_by: string
}

interface UserManagementModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function UserManagementModal({ isOpen, onClose }: UserManagementModalProps) {
  const [users, setUsers] = useState<User[]>([])
  const [deletedUsers, setDeletedUsers] = useState<DeletedUser[]>([])
  const [subteams, setSubteams] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [newUser, setNewUser] = useState({ username: '', password: '', role: 'user', subteam: '' })

  useEffect(() => {
    if (isOpen) {
      loadData()
    }
  }, [isOpen])

  const loadData = async () => {
    try {
      const [usersRes, deletedRes] = await Promise.all([
        fetch('/api/users', { credentials: 'include' }),
        fetch('/api/users/deleted', { credentials: 'include' }),
      ])
      const usersData = await usersRes.json()
      const deletedData = await deletedRes.json()
      setUsers(usersData.users || [])
      setDeletedUsers(deletedData.deleted_users || [])
      setSubteams(usersData.subteams || [])
    } catch (error) {
      console.error('Error loading users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(newUser),
      })

      if (response.ok) {
        setNewUser({ username: '', password: '', role: 'user', subteam: '' })
        loadData()
      }
    } catch (error) {
      console.error('Error creating user:', error)
    }
  }

  const handleDeleteUser = async (username: string) => {
    if (!confirm(`Delete user "${username}"?`)) return

    try {
      const response = await fetch(`/api/users/${username}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (response.ok) {
        loadData()
      }
    } catch (error) {
      console.error('Error deleting user:', error)
    }
  }

  if (!isOpen) return null

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
          className="modal-content max-w-5xl"
          onClick={(e) => e.stopPropagation()}
        >
        <div className="flex items-center justify-between p-4 border-b border-word-border bg-ribbon">
          <h2 className="text-lg font-semibold text-word-text">User Management</h2>
          <button onClick={onClose} className="text-word-textSecondary hover:text-word-text">
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-word-text mb-4 pb-2 border-b border-word-border">Create New User</h3>
            <form onSubmit={handleCreateUser} className="grid grid-cols-4 gap-4">
              <input
                type="text"
                placeholder="Username"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                required
                className="input"
              />
              <input
                type="password"
                placeholder="Password"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                required
                className="input"
              />
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                className="input"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
              <div className="flex gap-2">
                <select
                  value={newUser.subteam}
                  onChange={(e) => setNewUser({ ...newUser, subteam: e.target.value })}
                  required
                  className="input flex-1"
                >
                  <option value="">Select Subteam</option>
                  {subteams.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
                <button type="submit" className="btn-primary">
                  Create
                </button>
              </div>
            </form>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-word-text mb-4 pb-2 border-b border-word-border">Existing Users</h3>
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Password</th>
                    <th>Role</th>
                    <th>Subteam</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="font-medium">{user.username}</td>
                      <td className="font-mono text-sm bg-word-surface px-2 py-1">
                        {user.password || 'N/A'}
                      </td>
                      <td>
                        <select
                          defaultValue={user.role}
                          onChange={async (e) => {
                            await fetch(`/api/users/${user.username}/role?role=${e.target.value}`, {
                              method: 'PATCH',
                              credentials: 'include',
                            })
                            loadData()
                          }}
                          className="input text-sm py-1"
                        >
                          <option value="user">User</option>
                          <option value="admin">Admin</option>
                        </select>
                      </td>
                      <td>
                        <select
                          defaultValue={user.subteam || ''}
                          onChange={async (e) => {
                            await fetch(
                              `/api/users/${user.username}/subteam?subteam=${e.target.value}`,
                              {
                                method: 'PATCH',
                                credentials: 'include',
                              }
                            )
                            loadData()
                          }}
                          className="input text-sm py-1"
                        >
                          <option value="">No Subteam</option>
                          {subteams.map((st) => (
                            <option key={st} value={st}>
                              {st}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <button
                          onClick={() => handleDeleteUser(user.username)}
                          className="btn-secondary btn-small text-red-400 hover:text-red-300 flex items-center gap-1"
                        >
                          <TrashIcon className="h-4 w-4" />
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {deletedUsers.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-word-text mb-4 pb-2 border-b border-word-border">Recently Deleted Users</h3>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Role</th>
                      <th>Subteam</th>
                      <th>Deleted At</th>
                      <th>Deleted By</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deletedUsers.map((user) => (
                      <tr key={user.username}>
                        <td className="font-medium">{user.username}</td>
                        <td>
                          <span className="text-xs bg-ribbon px-2 py-1">{user.role}</span>
                        </td>
                        <td>{user.subteam || 'N/A'}</td>
                        <td className="text-word-textSecondary text-sm">
                          {new Date(user.deleted_at).toLocaleString()}
                        </td>
                        <td>{user.deleted_by}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
