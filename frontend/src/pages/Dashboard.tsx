import { useQuery } from '@tanstack/react-query'
import { reportsApi } from '../services/api'
import type { DashboardStats } from '../types'
import {
  BellAlertIcon,
  FolderIcon,
  ExclamationTriangleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { Doughnut } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const severityColors: Record<string, string> = {
  Critical: 'text-danger-600 bg-danger-100',
  High: 'text-orange-600 bg-orange-100',
  Medium: 'text-warning-600 bg-warning-100',
  Low: 'text-success-600 bg-success-100',
}

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await reportsApi.getDashboard()
      return response.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
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
      name: 'Open Alerts',
      value: stats?.alerts.open || 0,
      icon: BellAlertIcon,
      color: 'bg-danger-500',
      change: `${stats?.alerts.today || 0} today`,
    },
    {
      name: 'Critical Alerts',
      value: stats?.alerts.critical || 0,
      icon: ExclamationTriangleIcon,
      color: 'bg-orange-500',
      change: 'Require immediate action',
    },
    {
      name: 'Open Cases',
      value: stats?.cases.open || 0,
      icon: FolderIcon,
      color: 'bg-primary-500',
      change: `${stats?.cases.today || 0} opened today`,
    },
    {
      name: 'SLA Breached',
      value: stats?.sla.breached || 0,
      icon: ClockIcon,
      color: 'bg-warning-500',
      change: `${stats?.sla.at_risk || 0} at risk`,
    },
  ]

  const alertChartData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [
      {
        data: [
          stats?.alerts.critical || 0,
          Math.floor((stats?.alerts.total || 0) * 0.3),
          Math.floor((stats?.alerts.total || 0) * 0.4),
          Math.floor((stats?.alerts.total || 0) * 0.2),
        ],
        backgroundColor: ['#dc2626', '#ea580c', '#d97706', '#16a34a'],
        borderWidth: 0,
      },
    ],
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Real-time overview of your security operations
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="card">
            <div className="p-5">
              <div className="flex items-center">
                <div className={classNames(stat.color, 'rounded-md p-3')}>
                  <stat.icon className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="truncate text-sm font-medium text-gray-500">{stat.name}</dt>
                    <dd className="text-3xl font-semibold text-gray-900">{stat.value}</dd>
                  </dl>
                </div>
              </div>
              <div className="mt-3 text-sm text-gray-500">{stat.change}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts and recent alerts */}
      <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Alert distribution chart */}
        <div className="card">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900">Alert Distribution</h3>
            <div className="mt-4 h-64 flex items-center justify-center">
              <Doughnut
                data={alertChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                    },
                  },
                }}
              />
            </div>
          </div>
        </div>

        {/* Recent alerts */}
        <div className="card">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900">Recent Alerts</h3>
            <div className="mt-4 flow-root">
              <ul className="-my-5 divide-y divide-gray-200">
                {stats?.recent_alerts.map((alert) => (
                  <li key={alert.id} className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <span
                          className={classNames(
                            severityColors[alert.severity],
                            'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium'
                          )}
                        >
                          {alert.severity}
                        </span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-900">
                          {alert.description || 'No description'}
                        </p>
                        <p className="truncate text-sm text-gray-500">
                          {new Date(alert.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <span
                          className={classNames(
                            alert.status === 'open'
                              ? 'bg-danger-100 text-danger-700'
                              : 'bg-gray-100 text-gray-700',
                            'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize'
                          )}
                        >
                          {alert.status}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
