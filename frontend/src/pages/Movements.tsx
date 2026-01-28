import { useQuery } from '@tanstack/react-query'
import { movementsApi } from '../services/api'
import type { Movement } from '../types'
import { format } from 'date-fns'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const statusStyles: Record<string, string> = {
  active: 'bg-success-100 text-success-700',
  completed: 'bg-gray-100 text-gray-700',
  cancelled: 'bg-danger-100 text-danger-700',
  delayed: 'bg-warning-100 text-warning-700',
}

export default function Movements() {
  const { data: movements, isLoading } = useQuery<Movement[]>({
    queryKey: ['movements'],
    queryFn: async () => {
      const response = await movementsApi.getAll()
      return response.data
    },
  })

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Movements</h1>
          <p className="mt-2 text-sm text-gray-700">
            Track and monitor all cargo movements and shipments
          </p>
        </div>
      </div>

      {/* Movements table */}
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
                      Cargo
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Route
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Risk Score
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Laycan
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {isLoading ? (
                    <tr>
                      <td colSpan={6} className="py-10 text-center">
                        <div className="flex justify-center">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                        </div>
                      </td>
                    </tr>
                  ) : movements?.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-10 text-center text-gray-500">
                        No movements found
                      </td>
                    </tr>
                  ) : (
                    movements?.map((movement) => (
                      <tr key={movement.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900">
                          #{movement.id}
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-900">
                          {movement.cargo}
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-500 max-w-xs truncate">
                          {movement.route}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <span
                            className={classNames(
                              statusStyles[movement.status] || 'bg-gray-100 text-gray-700',
                              'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize'
                            )}
                          >
                            {movement.status}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <div className="flex items-center">
                            <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                              <div
                                className={classNames(
                                  movement.risk_score > 70 ? 'bg-danger-500' :
                                  movement.risk_score > 40 ? 'bg-warning-500' : 'bg-success-500',
                                  'h-2 rounded-full'
                                )}
                                style={{ width: `${movement.risk_score}%` }}
                              />
                            </div>
                            <span className="text-gray-600">{movement.risk_score.toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {format(new Date(movement.laycan_start), 'MMM d')} -{' '}
                          {format(new Date(movement.laycan_end), 'MMM d')}
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
