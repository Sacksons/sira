import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { casesApi } from '../services/api'
import type { Case, CasePriority, CaseStatus } from '../types'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import { PlusIcon } from '@heroicons/react/24/outline'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const priorityStyles: Record<CasePriority, string> = {
  critical: 'badge-critical',
  high: 'badge-high',
  medium: 'badge-medium',
  low: 'badge-low',
}

const statusStyles: Record<CaseStatus, string> = {
  open: 'bg-blue-100 text-blue-700',
  investigating: 'bg-purple-100 text-purple-700',
  pending: 'bg-yellow-100 text-yellow-700',
  closed: 'bg-gray-100 text-gray-700',
}

export default function Cases() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newCase, setNewCase] = useState({ title: '', overview: '', priority: 'medium' })
  const queryClient = useQueryClient()

  const { data: cases, isLoading } = useQuery<Case[]>({
    queryKey: ['cases'],
    queryFn: async () => {
      const response = await casesApi.getAll()
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: typeof newCase) => casesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] })
      toast.success('Case created successfully')
      setShowCreateModal(false)
      setNewCase({ title: '', overview: '', priority: 'medium' })
    },
    onError: () => {
      toast.error('Failed to create case')
    },
  })

  const handleExport = async (caseId: number, format: 'json' | 'pdf') => {
    try {
      if (format === 'pdf') {
        const response = await casesApi.export(caseId, 'pdf')
        // Handle PDF download
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `case_${caseId}_report.pdf`
        a.click()
        window.URL.revokeObjectURL(url)
      } else {
        const response = await casesApi.export(caseId, 'json')
        console.log(response.data)
        toast.success('Export data ready')
      }
    } catch (error) {
      toast.error('Export failed')
    }
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Cases</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage security incident investigations and compliance cases
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Case
          </button>
        </div>
      </div>

      {/* Cases grid */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          <div className="col-span-full flex justify-center py-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : cases?.length === 0 ? (
          <div className="col-span-full text-center py-10 text-gray-500">
            No cases found. Create one to get started.
          </div>
        ) : (
          cases?.map((caseItem) => (
            <div key={caseItem.id} className="card">
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-500">
                    {caseItem.case_number || `#${caseItem.id}`}
                  </span>
                  <span className={classNames(priorityStyles[caseItem.priority], 'capitalize')}>
                    {caseItem.priority}
                  </span>
                </div>
                <h3 className="mt-2 text-lg font-medium text-gray-900 truncate">
                  {caseItem.title}
                </h3>
                <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                  {caseItem.overview || 'No overview provided'}
                </p>
                <div className="mt-4 flex items-center justify-between">
                  <span
                    className={classNames(
                      statusStyles[caseItem.status],
                      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize'
                    )}
                  >
                    {caseItem.status}
                  </span>
                  <span className="text-sm text-gray-500">
                    {format(new Date(caseItem.created_at), 'MMM d, yyyy')}
                  </span>
                </div>
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => handleExport(caseItem.id, 'pdf')}
                    className="btn-secondary text-xs py-1 px-2"
                  >
                    Export PDF
                  </button>
                  <button
                    onClick={() => handleExport(caseItem.id, 'json')}
                    className="btn-secondary text-xs py-1 px-2"
                  >
                    Export JSON
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowCreateModal(false)} />
            <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Case</h3>
              <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(newCase); }}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Title</label>
                    <input
                      type="text"
                      required
                      value={newCase.title}
                      onChange={(e) => setNewCase({ ...newCase, title: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Overview</label>
                    <textarea
                      rows={3}
                      value={newCase.overview}
                      onChange={(e) => setNewCase({ ...newCase, overview: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Priority</label>
                    <select
                      value={newCase.priority}
                      onChange={(e) => setNewCase({ ...newCase, priority: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>
                <div className="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button type="submit" className="btn-primary sm:col-start-2">
                    Create Case
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="btn-secondary sm:col-start-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
