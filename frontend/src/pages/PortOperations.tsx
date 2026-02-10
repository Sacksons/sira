import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { portsApi } from '../services/api'
import {
  BuildingOffice2Icon,
} from '@heroicons/react/24/outline'
import { Bar } from 'react-chartjs-2'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const portStatusColors: Record<string, string> = {
  operational: 'bg-green-100 text-green-700',
  congested: 'bg-orange-100 text-orange-700',
  closed: 'bg-danger-100 text-danger-700',
  restricted: 'bg-warning-100 text-warning-700',
}

export default function PortOperations() {
  const [selectedPort, setSelectedPort] = useState<number | null>(null)

  const { data: ports, isLoading } = useQuery({
    queryKey: ['ports'],
    queryFn: async () => {
      const response = await portsApi.getAll()
      return response.data
    },
  })

  const { data: congestion } = useQuery({
    queryKey: ['port-congestion'],
    queryFn: async () => {
      const response = await portsApi.getCongestionSummary()
      return response.data
    },
    refetchInterval: 60000,
  })

  const { data: berths } = useQuery({
    queryKey: ['berths', selectedPort],
    queryFn: async () => {
      if (!selectedPort) return []
      const response = await portsApi.getBerths(selectedPort)
      return response.data
    },
    enabled: !!selectedPort,
  })

  const { data: bookings } = useQuery({
    queryKey: ['berth-bookings'],
    queryFn: async () => {
      const response = await portsApi.getBookings()
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

  const congestionChart = congestion
    ? {
        labels: congestion.map((p: any) => p.port_code),
        datasets: [
          {
            label: 'Queue Length',
            data: congestion.map((p: any) => p.current_queue),
            backgroundColor: '#f59e0b',
            borderRadius: 4,
          },
          {
            label: 'Active Bookings',
            data: congestion.map((p: any) => p.active_bookings),
            backgroundColor: '#3b82f6',
            borderRadius: 4,
          },
        ],
      }
    : null

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Port & Terminal Operations</h1>
        <p className="mt-1 text-sm text-gray-500">
          Berth allocation, anchorage management, and port congestion tracking
        </p>
      </div>

      {/* Port Congestion Chart */}
      {congestionChart && (
        <div className="card mb-6">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900">Port Congestion Overview</h3>
            <div className="mt-4 h-64">
              <Bar
                data={congestionChart}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { position: 'top' } },
                  scales: { y: { beginAtZero: true } },
                }}
              />
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Port List */}
        <div className="lg:col-span-2 card">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ports</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Port</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Country</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Queue</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Wait</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Dwell</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {(ports || []).map((port: any) => (
                    <tr
                      key={port.id}
                      className={classNames(
                        'hover:bg-gray-50 cursor-pointer',
                        selectedPort === port.id ? 'bg-primary-50' : ''
                      )}
                      onClick={() => setSelectedPort(port.id)}
                    >
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{port.name}</td>
                      <td className="px-4 py-3 text-sm text-primary-600 font-mono">{port.code}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{port.country}</td>
                      <td className="px-4 py-3">
                        <span className={classNames(portStatusColors[port.status] || 'bg-gray-100 text-gray-700', 'inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize')}>
                          {port.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 font-medium">{port.current_queue}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{port.avg_wait_days}d</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{port.avg_dwell_days}d</td>
                    </tr>
                  ))}
                  {(!ports || ports.length === 0) && (
                    <tr>
                      <td colSpan={7} className="px-4 py-8 text-center text-sm text-gray-500">
                        No ports configured
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Berth Panel */}
        <div className="card">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {selectedPort ? 'Berths' : 'Select a Port'}
            </h3>
            {selectedPort && berths ? (
              <div className="space-y-3">
                {berths.map((berth: any) => (
                  <div key={berth.id} className="border rounded-lg p-3">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900">{berth.name}</span>
                      <span className={classNames(
                        berth.status === 'available' ? 'bg-green-100 text-green-700' :
                        berth.status === 'occupied' ? 'bg-blue-100 text-blue-700' :
                        'bg-orange-100 text-orange-700',
                        'rounded-full px-2 py-0.5 text-xs font-medium capitalize'
                      )}>
                        {berth.status}
                      </span>
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                      {berth.berth_type && <span className="capitalize">{berth.berth_type} | </span>}
                      {berth.loading_rate && <span>{berth.loading_rate} t/hr</span>}
                    </div>
                  </div>
                ))}
                {berths.length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">No berths configured</p>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <BuildingOffice2Icon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Click a port to view its berths</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Berth Bookings */}
      <div className="mt-6 card">
        <div className="p-5">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Berth Bookings</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Booking ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Berth</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vessel</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scheduled Arrival</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scheduled Departure</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cargo</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {(bookings || []).slice(0, 20).map((booking: any) => (
                  <tr key={booking.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">#{booking.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">Berth {booking.berth_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">Vessel {booking.vessel_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {new Date(booking.scheduled_arrival).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {new Date(booking.scheduled_departure).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{booking.cargo_type || '-'}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 capitalize">
                        {booking.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {(!bookings || bookings.length === 0) && (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-sm text-gray-500">
                      No bookings found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
