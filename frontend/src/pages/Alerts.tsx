import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '../services/api'
import type { Alert, AlertSeverity, AlertStatus } from '../types'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const severityStyles: Record<AlertSeverity, string> = {
  Critical: 'badge-critical',
  High: 'badge-high',
  Medium: 'badge-medium',
  Low: 'badge-low',
}

const statusStyles: Record<AlertStatus, string> = {
  open: 'bg-danger-100 text-danger-700',
  acknowledged: 'bg-yellow-100 text-yellow-700',
  assigned: 'bg-blue-100 text-blue-700',
  investigating: 'bg-purple-100 text-purple-700',
  closed: 'bg-gray-100 text-gray-700',
}

export default function Alerts() {
  const [filters, setFilters] = useState({
    severity: '',
    status: '',
  })
  const queryClient = useQueryClient()

  const { data: alerts, isLoading } = useQuery<Alert[]>({
    queryKey: ['alerts', filters],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (filters.severity) params.severity = filters.severity
      if (filters.status) params.status = filters.status
      const response = await alertsApi.getAll(params)
      return response.data
    },
  })

  const acknowledgeMutation = useMutation({
    mutationFn: (id: number) => alertsApi.acknowledge(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert acknowledged')
    },
  })

  const resolveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: number; notes: string }) =>
      alertsApi.resolve(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert resolved')
    },
  })

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
          <p className="mt-2 text-sm text-gray-700">
            Monitor and manage security alerts across all movements
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-4 flex gap-4">
        <select
          value={filters.severity}
          onChange={(e) => setFilters((f) => ({ ...f, severity: e.target.value }))}
          className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="">All Severities</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>

        <select
          value={filters.status}
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
          className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="assigned">Assigned</option>
          <option value="investigating">Investigating</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      {/* Alerts table */}
      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">
                      ID
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Severity
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Domain
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Description
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Created
                    </th>
                    <th className="relative py-3.5 pl-3 pr-4">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {isLoading ? (
                    <tr>
                      <td colSpan={7} className="py-10 text-center">
                        <div className="flex justify-center">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                        </div>
                      </td>
                    </tr>
                  ) : alerts?.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-10 text-center text-gray-500">
                        No alerts found
                      </td>
                    </tr>
                  ) : (
                    alerts?.map((alert) => (
                      <tr key={alert.id} className={alert.sla_breached ? 'bg-danger-50' : ''}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900">
                          #{alert.id}
                          {alert.sla_breached && (
                            <span className="ml-2 text-danger-600 text-xs">SLA!</span>
                          )}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <span className={severityStyles[alert.severity]}>
                            {alert.severity}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {alert.domain || '-'}
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-500 max-w-xs truncate">
                          {alert.description || 'No description'}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <span
                            className={classNames(
                              statusStyles[alert.status],
                              'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize'
                            )}
                          >
                            {alert.status}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {format(new Date(alert.created_at), 'MMM d, HH:mm')}
                        </td>
                        <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium">
                          {alert.status === 'open' && (
                            <button
                              onClick={() => acknowledgeMutation.mutate(alert.id)}
                              className="text-primary-600 hover:text-primary-900 mr-3"
                            >
                              Acknowledge
                            </button>
                          )}
                          {alert.status !== 'closed' && (
                            <button
                              onClick={() =>
                                resolveMutation.mutate({ id: alert.id, notes: 'Resolved' })
                              }
                              className="text-success-600 hover:text-success-900"
                            >
                              Resolve
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
