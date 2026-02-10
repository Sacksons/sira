import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fleetApi } from '../services/api'
import {
  TruckIcon,
  WrenchScrewdriverIcon,
  ArrowPathIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import { Doughnut } from 'react-chartjs-2'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const statusColors: Record<string, string> = {
  available: 'bg-green-100 text-green-700',
  in_transit: 'bg-blue-100 text-blue-700',
  loading: 'bg-indigo-100 text-indigo-700',
  unloading: 'bg-purple-100 text-purple-700',
  maintenance: 'bg-orange-100 text-orange-700',
  breakdown: 'bg-danger-100 text-danger-700',
  idle: 'bg-gray-100 text-gray-700',
}

export default function FleetManagement() {
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data: assets, isLoading } = useQuery({
    queryKey: ['fleet-assets', typeFilter, statusFilter],
    queryFn: async () => {
      const params: Record<string, any> = {}
      if (typeFilter) params.asset_type = typeFilter
      if (statusFilter) params.status_filter = statusFilter
      const response = await fleetApi.getAssets(params)
      return response.data
    },
  })

  const { data: utilization } = useQuery({
    queryKey: ['fleet-utilization'],
    queryFn: async () => {
      const response = await fleetApi.getUtilization()
      return response.data
    },
  })

  const { data: availability } = useQuery({
    queryKey: ['fleet-availability'],
    queryFn: async () => {
      const response = await fleetApi.getAvailability()
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const utilizationChart = availability
    ? {
        labels: Object.keys(availability),
        datasets: [
          {
            data: Object.values(availability).map((v: any) => v.total),
            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'],
            borderWidth: 0,
          },
        ],
      }
    : null

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Fleet & Asset Management</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage trucks, rail wagons, equipment, and their allocation
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <div className="card p-4">
          <div className="flex items-center">
            <TruckIcon className="h-8 w-8 text-primary-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-500">Total Assets</p>
              <p className="text-2xl font-bold">{utilization?.total_assets || 0}</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-green-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-500">Avg Utilization</p>
              <p className="text-2xl font-bold">{utilization?.avg_utilization || 0}%</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center">
            <ArrowPathIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-500">In Transit</p>
              <p className="text-2xl font-bold">
                {utilization?.by_type
                  ? Object.values(utilization.by_type).reduce((sum: number, t: any) => sum + (t.in_transit || 0), 0)
                  : 0}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center">
            <WrenchScrewdriverIcon className="h-8 w-8 text-orange-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-500">In Maintenance</p>
              <p className="text-2xl font-bold">
                {assets?.filter((a: any) => a.status === 'maintenance').length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Asset List */}
        <div className="lg:col-span-2 card">
          <div className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Assets</h3>
              <div className="flex gap-2">
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="rounded-md border-gray-300 text-sm"
                >
                  <option value="">All Types</option>
                  <option value="truck">Truck</option>
                  <option value="rail_wagon">Rail Wagon</option>
                  <option value="barge">Barge</option>
                  <option value="crane">Crane</option>
                  <option value="loader">Loader</option>
                </select>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="rounded-md border-gray-300 text-sm"
                >
                  <option value="">All Statuses</option>
                  <option value="available">Available</option>
                  <option value="in_transit">In Transit</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="idle">Idle</option>
                </select>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Utilization</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {(assets || []).map((asset: any) => (
                    <tr key={asset.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-primary-600">{asset.asset_code}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{asset.name}</td>
                      <td className="px-4 py-3 text-sm text-gray-600 capitalize">{asset.asset_type?.replace('_', ' ')}</td>
                      <td className="px-4 py-3">
                        <span className={classNames(statusColors[asset.status] || 'bg-gray-100 text-gray-700', 'inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize')}>
                          {asset.status?.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className={classNames(
                                asset.utilization_pct >= 80 ? 'bg-green-500' : asset.utilization_pct >= 50 ? 'bg-warning-500' : 'bg-danger-500',
                                'h-2 rounded-full'
                              )}
                              style={{ width: `${Math.min(asset.utilization_pct || 0, 100)}%` }}
                            />
                          </div>
                          <span className="text-gray-600">{asset.utilization_pct || 0}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{asset.current_location || '-'}</td>
                    </tr>
                  ))}
                  {(!assets || assets.length === 0) && (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-sm text-gray-500">
                        No assets found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Utilization by Type Chart */}
        <div className="card">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900">Assets by Type</h3>
            <div className="mt-4 h-64 flex items-center justify-center">
              {utilizationChart && (
                <Doughnut
                  data={utilizationChart}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } },
                  }}
                />
              )}
            </div>

            {utilization?.by_type && (
              <div className="mt-4 space-y-2">
                {Object.entries(utilization.by_type).map(([type, data]: [string, any]) => (
                  <div key={type} className="flex justify-between items-center text-sm">
                    <span className="text-gray-600 capitalize">{type.replace('_', ' ')}</span>
                    <span className="font-medium">{data.avg_utilization}% util</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
