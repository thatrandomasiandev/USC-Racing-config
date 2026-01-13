'use client'

import { useState, useEffect } from 'react'
import { DocumentArrowUpIcon, DocumentTextIcon, TrashIcon } from '@heroicons/react/24/outline'

interface MoTeCFile {
  id: string
  filename: string
  file_type: string
  file_size: number
  uploaded_at: string
}

export default function MoTecFiles() {
  const [files, setFiles] = useState<MoTeCFile[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    loadFiles()
  }, [])

  const loadFiles = async () => {
    try {
      const response = await fetch('/api/motec/files', { credentials: 'include' })
      const data = await response.json()
      setFiles(data.files || [])
    } catch (error) {
      console.error('Error loading files:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', file.name.endsWith('.ldx') ? 'ldx' : 'ld')
    formData.append('auto_populate', 'true')

    try {
      const response = await fetch('/api/motec/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })

      if (response.ok) {
        loadFiles()
      }
    } catch (error) {
      console.error('Error uploading file:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (fileId: string, filename: string) => {
    if (!confirm(`Delete file "${filename}"?`)) return

    try {
      const response = await fetch(`/api/motec/files/${fileId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (response.ok) {
        loadFiles()
      }
    } catch (error) {
      console.error('Error deleting file:', error)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <section>
      <h2 className="text-xl font-semibold text-[#323130] mb-4">MoTeC Files</h2>

      <div className="mb-6">
        <label className="block text-sm font-medium text-word-text mb-2">
          Upload .ldx or .ld file
        </label>
        <div className="flex gap-4">
          <input
            type="file"
            accept=".ldx,.ld"
            onChange={handleUpload}
            disabled={uploading}
            className="input flex-1 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary-dark"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
        </div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Type</th>
                <th>Size</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {files.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-word-textSecondary">
                    No MoTeC files uploaded yet
                  </td>
                </tr>
              ) : (
                files.map((file) => (
                  <tr key={file.id}>
                    <td className="font-medium">{file.filename}</td>
                    <td>
                      <span className="uppercase text-xs bg-primary/20 text-primary px-2 py-1 rounded">
                        {file.file_type}
                      </span>
                    </td>
                    <td className="text-word-textSecondary">{formatFileSize(file.file_size)}</td>
                    <td className="text-word-textSecondary text-sm">
                      {new Date(file.uploaded_at).toLocaleString()}
                    </td>
                    <td>
                      <div className="flex gap-2">
                        <a
                          href={`/api/motec/files/${file.id}/download`}
                          className="btn-secondary btn-small flex items-center gap-1"
                        >
                          <DocumentTextIcon className="h-4 w-4" />
                          Download
                        </a>
                        <button
                          onClick={() => handleDelete(file.id, file.filename)}
                          className="btn-secondary btn-small flex items-center gap-1 text-red-400 hover:text-red-300"
                        >
                          <TrashIcon className="h-4 w-4" />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
