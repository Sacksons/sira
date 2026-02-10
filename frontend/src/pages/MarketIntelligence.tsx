import { useQuery } from '@tanstack/react-query'
import { marketApi } from '../services/api'
import {
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline'
import { Bar } from 'react-chartjs-2'
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
  Filler,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler)

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function MarketIntelligence() {
  const { data: latestIndices, isLoading: indicesLoading } = useQuery({
    queryKey: ['market-indices-latest'],
    queryFn: async () => {
      const response = await marketApi.getLatestIndices()
      return response.data
    },
    refetchInterval: 300000,
  })

  const { data: benchmarks } = useQuery({
    queryKey: ['rate-benchmarks'],
    queryFn: async () => {
      const response = await marketApi.getRateBenchmarks()
      return response.data
    },
  })

  const { data: demurrageExposure } = useQuery({
    queryKey: ['demurrage-exposure'],
    queryFn: async () => {
      const response = await marketApi.getDemurrageExposure()
      return response.data
    },
    refetchInterval: 60000,
  })

  const { data: rates } = useQuery({
    queryKey: ['freight-rates'],
    queryFn: async () => {
      const response = await marketApi.getRates()
      return response.data
    },
  })

  if (indicesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const benchmarkChart = benchmarks?.benchmarks
    ? {
        labels: benchmarks.benchmarks.map((b: any) => `${b.lane} (${b.mode})`),
        datasets: [
          {
            label: 'Avg Rate (USD)',
            data: benchmarks.benchmarks.map((b: any) => b.avg_rate),
            backgroundColor: '#3b82f6',
            borderRadius: 4,
          },
          {
            label: 'Min Rate',
            data: benchmarks.benchmarks.map((b: any) => b.min_rate),
            backgroundColor: '#10b981',
            borderRadius: 4,
          },
          {
            label: 'Max Rate',
            data: benchmarks.benchmarks.map((b: any) => b.max_rate),
            backgroundColor: '#ef4444',
            borderRadius: 4,
          },
        ],
      }
    : null

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Market Intelligence</h1>
        <p className="mt-1 text-sm text-gray-500">
          Freight rate benchmarks, market indices, and demurrage analytics
        </p>
      </div>

      {/* Demurrage Exposure Summary */}
      {demurrageExposure && (
        <div className="mb-6 rounded-lg bg-gradient-to-r from-danger-600 to-orange-600 p-5 text-white">
          <h3 className="text-sm font-medium text-red-100 mb-3">Demurrage Exposure Dashboard</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div>
              <p className="text-xs text-red-200">Total Exposure</p>
              <p className="text-2xl font-bold">${((demurrageExposure.total_exposure_usd || 0) / 1000).toFixed(0)}K</p>
            </div>
            <div>
              <p className="text-xs text-red-200">Demurrage Days</p>
              <p className="text-2xl font-bold">{demurrageExposure.total_demurrage_days || 0}</p>
            </div>
            <div>
              <p className="text-xs text-red-200">Active Shipments</p>
              <p className="text-2xl font-bold">{demurrageExposure.active_shipments || 0}</p>
            </div>
            <div>
              <p className="text-xs text-red-200">High Risk</p>
              <p className="text-2xl font-bold">{demurrageExposure.high_risk_shipments || 0}</p>
            </div>
            <div>
              <p className="text-xs text-red-200">Avg Risk Score</p>
              <p className="text-2xl font-bold">{demurrageExposure.avg_risk_score || 0}/100</p>
            </div>
          </div>
        </div>
      )}

      {/* Market Indices */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-3">Market Indices</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {(latestIndices || []).map((idx: any) => (
            <div key={idx.index_name} className="card p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs text-gray-500">{idx.index_name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {idx.value?.toLocaleString()} {idx.unit || ''}
                  </p>
                </div>
                {idx.change_pct !== null && idx.change_pct !== undefined && (
                  <div className={classNames(
                    idx.change_pct >= 0 ? 'text-green-600' : 'text-danger-600',
                    'flex items-center text-sm font-medium'
                  )}>
                    {idx.change_pct >= 0 ? (
                      <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                    ) : (
                      <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                    )}
                    {Math.abs(idx.change_pct).toFixed(1)}%
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {idx.recorded_at ? new Date(idx.recorded_at).toLocaleDateString() : ''}
              </p>
            </div>
          ))}
          {(!latestIndices || latestIndices.length === 0) && (
            <div className="col-span-4 text-center py-8 text-sm text-gray-500">
              No market index data available
            </div>
          )}
        </div>
      </div>

      {/* Rate Benchmarks Chart */}
      {benchmarkChart && (
        <div className="card mb-6">
          <div className="p-5">
            <h3 className="text-lg font-medium text-gray-900">Rate Benchmarks (90-Day)</h3>
            <div className="mt-4 h-72">
              <Bar
                data={benchmarkChart}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { position: 'top' } },
                  scales: { y: { beginAtZero: true, title: { display: true, text: 'USD' } } },
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Freight Rates Table */}
      <div className="card">
        <div className="p-5">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Freight Rates</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lane</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mode</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rate (USD)</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Effective</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {(rates || []).slice(0, 20).map((rate: any) => (
                  <tr key={rate.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{rate.lane}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{rate.mode}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      ${rate.rate_usd?.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{rate.rate_unit?.replace('_', '/')}</td>
                    <td className="px-4 py-3">
                      <span className={classNames(
                        rate.rate_type === 'spot' ? 'bg-orange-100 text-orange-700' :
                        rate.rate_type === 'contract' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700',
                        'rounded-full px-2 py-0.5 text-xs font-medium capitalize'
                      )}>
                        {rate.rate_type || 'market'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{rate.source || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {rate.effective_date ? new Date(rate.effective_date).toLocaleDateString() : '-'}
                    </td>
                  </tr>
                ))}
                {(!rates || rates.length === 0) && (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-sm text-gray-500">
                      No freight rate data available
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
