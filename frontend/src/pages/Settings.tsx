import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { authApi } from '../services/api'
import toast from 'react-hot-toast'

export default function Settings() {
  const { user } = useAuthStore()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()

    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    setIsLoading(true)
    try {
      await authApi.changePassword(currentPassword, newPassword)
      toast.success('Password changed successfully')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to change password')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account and notification preferences
        </p>
      </div>

      <div className="space-y-8">
        {/* Profile Section */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900">Profile Information</h2>
            <div className="mt-4 grid grid-cols-1 gap-y-4 sm:grid-cols-2 sm:gap-x-6">
              <div>
                <label className="block text-sm font-medium text-gray-500">Username</label>
                <p className="mt-1 text-sm text-gray-900">{user?.username}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Email</label>
                <p className="mt-1 text-sm text-gray-900">{user?.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Role</label>
                <p className="mt-1 text-sm text-gray-900 capitalize">{user?.role?.replace('_', ' ')}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Status</label>
                <p className="mt-1 text-sm text-gray-900">
                  {user?.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Change Password Section */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900">Change Password</h2>
            <form onSubmit={handlePasswordChange} className="mt-4 space-y-4 max-w-md">
              <div>
                <label htmlFor="current-password" className="block text-sm font-medium text-gray-700">
                  Current Password
                </label>
                <input
                  type="password"
                  id="current-password"
                  required
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
              <div>
                <label htmlFor="new-password" className="block text-sm font-medium text-gray-700">
                  New Password
                </label>
                <input
                  type="password"
                  id="new-password"
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
              <div>
                <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  id="confirm-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary"
              >
                {isLoading ? 'Changing...' : 'Change Password'}
              </button>
            </form>
          </div>
        </div>

        {/* About Section */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900">About SIRA Platform</h2>
            <div className="mt-4 text-sm text-gray-500">
              <p><strong>Version:</strong> 1.0.0</p>
              <p className="mt-2">
                SIRA (Shipping Intelligence & Risk Analytics) is a comprehensive platform
                for managing shipping movements, tracking security events, and generating
                compliance reports.
              </p>
              <p className="mt-2">
                <strong>Sponsored by:</strong> Energie Partners (EP)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
