import { useQuery } from '@tanstack/react-query'
import { usersApi } from '../services/api'
import type { User } from '../types'
import { format } from 'date-fns'
import { useAuthStore } from '../stores/authStore'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const roleStyles: Record<string, string> = {
  admin: 'bg-purple-100 text-purple-700',
  supervisor: 'bg-blue-100 text-blue-700',
  security_lead: 'bg-green-100 text-green-700',
  operator: 'bg-gray-100 text-gray-700',
}

export default function Users() {
  const { user: currentUser } = useAuthStore()
  const canManageUsers = currentUser?.role === 'admin' || currentUser?.role === 'supervisor'

  const { data: users, isLoading } = useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await usersApi.getAll()
      return response.data
    },
    enabled: canManageUsers,
  })

  if (!canManageUsers) {
    return (
      <div className="text-center py-10">
        <h2 className="text-xl font-semibold text-gray-900">Access Denied</h2>
        <p className="mt-2 text-gray-500">You don't have permission to view this page.</p>
      </div>
    )
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage platform users and their roles
          </p>
        </div>
      </div>

      {/* Users table */}
      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">
                      User
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Role
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Last Login
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {isLoading ? (
                    <tr>
                      <td colSpan={5} className="py-10 text-center">
                        <div className="flex justify-center">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                        </div>
                      </td>
                    </tr>
                  ) : users?.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-10 text-center text-gray-500">
                        No users found
                      </td>
                    </tr>
                  ) : (
                    users?.map((user) => (
                      <tr key={user.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm">
                          <div className="flex items-center">
                            <div className="h-10 w-10 flex-shrink-0">
                              <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                                <span className="text-primary-700 font-medium">
                                  {user.username.charAt(0).toUpperCase()}
                                </span>
                              </div>
                            </div>
                            <div className="ml-4">
                              <div className="font-medium text-gray-900">{user.username}</div>
                              <div className="text-gray-500">{user.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <span
                            className={classNames(
                              roleStyles[user.role] || 'bg-gray-100 text-gray-700',
                              'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize'
                            )}
                          >
                            {user.role.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <span
                            className={classNames(
                              user.is_active
                                ? 'bg-success-100 text-success-700'
                                : 'bg-danger-100 text-danger-700',
                              'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium'
                            )}
                          >
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {user.last_login
                            ? format(new Date(user.last_login), 'MMM d, HH:mm')
                            : 'Never'}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {format(new Date(user.created_at), 'MMM d, yyyy')}
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
