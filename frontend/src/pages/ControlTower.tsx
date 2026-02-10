import { useQuery } from '@tanstack/react-query'
import { controlTowerApi } from '../services/api'
import {
  GlobeAltIcon,
  TruckIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  MapPinIcon,
  ClockIcon,
  ShieldExclamationIcon,
} from '@heroicons/react/24/outline'
import { Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function ControlTower() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['control-tower-overview'],
    queryFn: async () => {
      const response = await controlTowerApi.getOverview()
      return response.data
    },
    refetchInterval: 15000,
  })

  const { data: kpis } = useQuery({
    queryKey: ['control-tower-kpis'],
    queryFn: async () => {
      const response = await controlTowerApi.getKpis(30)
      return response.data
    },
    refetchInterval: 60000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const statCards = [
    {
      name: 'Active Shipments',
      value: overview?.shipments?.active || 0,
      icon: GlobeAltIcon,
      color: 'bg-primary-500',
      detail: `${overview?.shipments?.high_risk || 0} high risk`,
    },
    {
      name: 'Demurrage Exposure',
      value: `$${((overview?.shipments?.total_demurrage_exposure_usd || 0) / 1000).toFixed(0)}K`,
      icon: CurrencyDollarIcon,
      color: 'bg-danger-500',
      detail: `${overview?.shipments?.high_risk || 0} shipments at risk`,
    },
    {
      name: 'Active Vessels',
      value: overview?.vessels?.active || 0,
      icon: MapPinIcon,
      color: 'bg-blue-500',
      detail: `${overview?.vessels?.idle || 0} idle`,
    },
    {
      name: 'Fleet In Transit',
      value: overview?.fleet?.in_transit || 0,
      icon: TruckIcon,
      color: 'bg-green-500',
      detail: `${overview?.fleet?.available || 0} available`,
    },
    {
      name: 'Open Exceptions',
      value: overview?.exceptions?.open || 0,
      icon: ExclamationTriangleIcon,
      color: 'bg-orange-500',
      detail: `${overview?.exceptions?.critical || 0} critical`,
    },
    {
      name: 'Ports Congested',
      value: overview?.ports?.congested || 0,
      icon: ShieldExclamationIcon,
      color: 'bg-warning-500',
      detail: `of ${overview?.ports?.total || 0} ports`,
    },
  ]

  const shipmentsByStatus = overview?.shipments?.by_status || {}
  const statusChartData = {
    labels: Object.keys(shipmentsByStatus),
    datasets: [
      {
        data: Object.values(shipmentsByStatus) as number[],
        backgroundColor: ['#3b82f6', '#f59e0b', '#10b981', '#6366f1', '#ef4444', '#8b5cf6', '#06b6d4'],
        borderWidth: 0,
      },
    ],
  }

  const shipmentsByMode = overview?.shipments?.by_mode || {}
  const modeChartData = {
    labels: Object.keys(shipmentsByMode),
    datasets: [
      {
        label: 'Shipments',
        data: Object.values(shipmentsByMode) as number[],
        backgroundColor: '#3b82f6',
        borderRadius: 4,
      },
    ],
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Control Tower</h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time multimodal operational visibility across all corridors
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <ClockIcon className="h-4 w-4" />
          <span>Auto-refresh: 15s</span>
        </div>
      </div>

      {/* KPI Summary Bar */}
      {kpis && (
        <div className="mb-6 rounded-lg bg-gradient-to-r from-primary-600 to-primary-800 p-4 text-white">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-primary-200">30-Day Demurrage Cost</p>
              <p className="text-xl font-bold">${((kpis.demurrage?.total_cost_usd || 0) / 1000).toFixed(0)}K</p>
            </div>
            <div>
              <p className="text-xs text-primary-200">Fleet Utilization</p>
              <p className="text-xl font-bold">{kpis.fleet?.avg_utilization_pct || 0}%</p>
            </div>
            <div>
              <p className="text-xs text-primary-200">ETA Accuracy (±8h)</p>
              <p className="text-xl font-bold">{kpis.eta_accuracy?.within_8_hours_pct || 0}%</p>
            </div>
            <div>
              <p className="text-xs text-primary-200">Shipments Completed</p>
              <p className="text-xl font-bold">{kpis.shipments_completed || 0}</p>
            </div>
          </div>
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {statCards.map((stat) => (
          <div key={stat.name} className="card">
            <div className="p-4">
              <div className="flex items-center">
                <div className={classNames(stat.color, 'rounded-md p-2')}>
                  <stat.icon className="h-5 w-5 text-white" />
                </div>
                <div className="ml-3">
                  <p className="text-xs text-gray-500">{stat.name}</p>
                  <p className="text-xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
              <p className="mt-2 text-xs text-gray-500">{stat.detail}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="mt-6 grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div className="card">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900">Shipments by Status</h3>
            <div className="mt-4 h-64 flex items-center justify-center">
              <Doughnut
                data={statusChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { position: 'bottom' } },
                }}
              />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900">Active Shipments by Mode</h3>
            <div className="mt-4 h-64">
              <Bar
                data={modeChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: { y: { beginAtZero: true } },
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Exceptions */}
      <div className="mt-6 card">
        <div className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Recent Exceptions</h3>
            <span className="inline-flex items-center rounded-full bg-danger-100 px-2.5 py-0.5 text-xs font-medium text-danger-700">
              {overview?.exceptions?.open || 0} open
            </span>
          </div>
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {(overview?.exceptions?.recent || []).map((exc: any) => (
                  <tr key={exc.id}>
                    <td className="px-4 py-3 text-sm text-gray-900">{exc.type}</td>
                    <td className="px-4 py-3">
                      <span
                        className={classNames(
                          exc.severity === 'critical'
                            ? 'bg-danger-100 text-danger-700'
                            : exc.severity === 'high'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-warning-100 text-warning-700',
                          'inline-flex rounded-full px-2 py-0.5 text-xs font-medium'
                        )}
                      >
                        {exc.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                      {exc.description || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 capitalize">
                        {exc.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {exc.created_at ? new Date(exc.created_at).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))}
                {(!overview?.exceptions?.recent || overview.exceptions.recent.length === 0) && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-sm text-gray-500">
                      No recent exceptions
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
