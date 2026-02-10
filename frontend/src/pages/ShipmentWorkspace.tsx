import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { shipmentsApi } from '../services/api'
import {
  DocumentTextIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const statusColors: Record<string, string> = {
  planned: 'bg-gray-100 text-gray-700',
  loading: 'bg-blue-100 text-blue-700',
  in_transit: 'bg-indigo-100 text-indigo-700',
  at_port: 'bg-purple-100 text-purple-700',
  discharging: 'bg-cyan-100 text-cyan-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-danger-100 text-danger-700',
}

const riskColors = (score: number) => {
  if (score >= 80) return 'text-danger-600 bg-danger-100'
  if (score >= 60) return 'text-orange-600 bg-orange-100'
  if (score >= 40) return 'text-warning-600 bg-warning-100'
  return 'text-green-600 bg-green-100'
}

export default function ShipmentWorkspace() {
  const [selectedShipment, setSelectedShipment] = useState<number | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data: shipments, isLoading } = useQuery({
    queryKey: ['shipments', statusFilter],
    queryFn: async () => {
      const params: Record<string, any> = {}
      if (statusFilter) params.status_filter = statusFilter
      const response = await shipmentsApi.getAll(params)
      return response.data
    },
  })

  const { data: shipmentDetail } = useQuery({
    queryKey: ['shipment-detail', selectedShipment],
    queryFn: async () => {
      if (!selectedShipment) return null
      const response = await shipmentsApi.getById(selectedShipment)
      return response.data
    },
    enabled: !!selectedShipment,
  })

  const { data: atRisk } = useQuery({
    queryKey: ['shipments-at-risk'],
    queryFn: async () => {
      const response = await shipmentsApi.getAtRisk(50)
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

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Shipment Workspace</h1>
        <p className="mt-1 text-sm text-gray-500">
          End-to-end shipment tracking with milestones, documents, and chain-of-custody
        </p>
      </div>

      {/* At-Risk Banner */}
      {atRisk && atRisk.length > 0 && (
        <div className="mb-6 rounded-lg bg-orange-50 border border-orange-200 p-4">
          <div className="flex items-center mb-2">
            <ExclamationTriangleIcon className="h-5 w-5 text-orange-500 mr-2" />
            <span className="font-medium text-orange-800">{atRisk.length} Shipments at Demurrage Risk</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {atRisk.slice(0, 5).map((s: any) => (
              <button
                key={s.id}
                onClick={() => setSelectedShipment(s.id)}
                className="inline-flex items-center rounded-md bg-orange-100 px-2 py-1 text-xs font-medium text-orange-700 hover:bg-orange-200"
              >
                {s.shipment_ref} (Risk: {s.demurrage_risk_score})
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Shipment List */}
        <div className={classNames(selectedShipment ? 'lg:col-span-1' : 'lg:col-span-3', 'card')}>
          <div className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Shipments</h3>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="rounded-md border-gray-300 text-sm"
              >
                <option value="">All Statuses</option>
                <option value="planned">Planned</option>
                <option value="loading">Loading</option>
                <option value="in_transit">In Transit</option>
                <option value="at_port">At Port</option>
                <option value="discharging">Discharging</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {(shipments || []).map((shipment: any) => (
                <div
                  key={shipment.id}
                  onClick={() => setSelectedShipment(shipment.id)}
                  className={classNames(
                    'border rounded-lg p-3 cursor-pointer transition-colors',
                    selectedShipment === shipment.id ? 'border-primary-500 bg-primary-50' : 'hover:bg-gray-50'
                  )}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">{shipment.shipment_ref}</p>
                      <p className="text-xs text-gray-500 mt-1">{shipment.cargo_type} | {shipment.origin} → {shipment.destination}</p>
                    </div>
                    <span className={classNames(statusColors[shipment.status] || 'bg-gray-100 text-gray-700', 'rounded-full px-2 py-0.5 text-xs font-medium capitalize')}>
                      {shipment.status?.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center justify-between">
                    <div className="flex items-center text-xs text-gray-500">
                      <MapPinIcon className="h-3 w-3 mr-1" />
                      {shipment.current_leg || shipment.current_mode || 'N/A'}
                    </div>
                    {shipment.demurrage_risk_score > 0 && (
                      <span className={classNames(riskColors(shipment.demurrage_risk_score), 'rounded px-1.5 py-0.5 text-xs font-medium')}>
                        Risk: {shipment.demurrage_risk_score}
                      </span>
                    )}
                  </div>
                </div>
              ))}
              {(!shipments || shipments.length === 0) && (
                <p className="text-sm text-gray-500 text-center py-8">No shipments found</p>
              )}
            </div>
          </div>
        </div>

        {/* Shipment Detail Panel */}
        {selectedShipment && shipmentDetail && (
          <div className="lg:col-span-2 space-y-4">
            {/* Header */}
            <div className="card p-5">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{shipmentDetail.shipment_ref}</h2>
                  <p className="text-sm text-gray-500 mt-1">
                    {shipmentDetail.cargo_type} | {shipmentDetail.volume_tonnes ? `${shipmentDetail.volume_tonnes}t` : ''} | {shipmentDetail.origin} → {shipmentDetail.destination}
                  </p>
                </div>
                <div className="text-right">
                  <span className={classNames(statusColors[shipmentDetail.status] || 'bg-gray-100 text-gray-700', 'rounded-full px-3 py-1 text-sm font-medium capitalize')}>
                    {shipmentDetail.status?.replace('_', ' ')}
                  </span>
                  {shipmentDetail.eta_destination && (
                    <p className="text-xs text-gray-500 mt-2">
                      ETA: {new Date(shipmentDetail.eta_destination).toLocaleString()}
                      {shipmentDetail.eta_confidence && ` (${(shipmentDetail.eta_confidence * 100).toFixed(0)}% conf.)`}
                    </p>
                  )}
                </div>
              </div>

              {/* Demurrage info */}
              {shipmentDetail.demurrage_risk_score > 0 && (
                <div className="mt-4 rounded-lg bg-orange-50 p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-orange-800">Demurrage Risk</span>
                    <span className={classNames(riskColors(shipmentDetail.demurrage_risk_score), 'rounded px-2 py-0.5 text-sm font-bold')}>
                      {shipmentDetail.demurrage_risk_score}/100
                    </span>
                  </div>
                  {shipmentDetail.demurrage_exposure_usd > 0 && (
                    <p className="text-xs text-orange-600 mt-1">
                      Exposure: ${shipmentDetail.demurrage_exposure_usd?.toLocaleString()}
                      {shipmentDetail.demurrage_days > 0 && ` | ${shipmentDetail.demurrage_days} days`}
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Milestones */}
            <div className="card p-5">
              <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                <ClockIcon className="h-5 w-5 mr-2 text-gray-400" />
                Milestones
              </h3>
              {shipmentDetail.milestones && shipmentDetail.milestones.length > 0 ? (
                <div className="space-y-3">
                  {shipmentDetail.milestones.map((m: any) => (
                    <div key={m.id} className="flex items-start gap-3">
                      <div className={classNames(
                        m.status === 'completed' ? 'bg-green-500' :
                        m.status === 'delayed' ? 'bg-orange-500' :
                        'bg-gray-300',
                        'w-3 h-3 rounded-full mt-1.5 flex-shrink-0'
                      )} />
                      <div className="flex-1">
                        <div className="flex justify-between">
                          <span className="text-sm font-medium text-gray-900 capitalize">{m.milestone_type?.replace('_', ' ')}</span>
                          <span className="text-xs text-gray-500">{m.mode || ''}</span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {m.planned_time && <span>Planned: {new Date(m.planned_time).toLocaleString()}</span>}
                          {m.actual_time && <span className="ml-2">Actual: {new Date(m.actual_time).toLocaleString()}</span>}
                          {m.variance_hours && (
                            <span className={classNames(
                              m.variance_hours > 0 ? 'text-danger-600' : 'text-green-600',
                              'ml-2 font-medium'
                            )}>
                              ({m.variance_hours > 0 ? '+' : ''}{m.variance_hours.toFixed(1)}h)
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No milestones recorded</p>
              )}
            </div>

            {/* Documents */}
            <div className="card p-5">
              <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                <DocumentTextIcon className="h-5 w-5 mr-2 text-gray-400" />
                Documents
              </h3>
              {shipmentDetail.documents && shipmentDetail.documents.length > 0 ? (
                <div className="space-y-2">
                  {shipmentDetail.documents.map((doc: any) => (
                    <div key={doc.id} className="flex items-center justify-between border rounded p-2">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{doc.title}</p>
                        <p className="text-xs text-gray-500 capitalize">{doc.document_type?.replace('_', ' ')}</p>
                      </div>
                      <span className={classNames(
                        doc.status === 'verified' ? 'bg-green-100 text-green-700' :
                        doc.status === 'rejected' ? 'bg-danger-100 text-danger-700' :
                        'bg-warning-100 text-warning-700',
                        'rounded-full px-2 py-0.5 text-xs font-medium capitalize'
                      )}>
                        {doc.status}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No documents uploaded</p>
              )}
            </div>

            {/* Chain of Custody */}
            <div className="card p-5">
              <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                <ShieldCheckIcon className="h-5 w-5 mr-2 text-gray-400" />
                Chain of Custody
                <span className={classNames(
                  shipmentDetail.custody_status === 'intact' ? 'bg-green-100 text-green-700' :
                  shipmentDetail.custody_status === 'tampered' ? 'bg-danger-100 text-danger-700' :
                  'bg-gray-100 text-gray-700',
                  'ml-2 rounded-full px-2 py-0.5 text-xs font-medium capitalize'
                )}>
                  {shipmentDetail.custody_status}
                </span>
              </h3>
              {shipmentDetail.custody_events && shipmentDetail.custody_events.length > 0 ? (
                <div className="space-y-3">
                  {shipmentDetail.custody_events.map((event: any) => (
                    <div key={event.id} className="border-l-2 border-gray-200 pl-3">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium text-gray-900 capitalize">{event.event_type?.replace('_', ' ')}</span>
                        <span className="text-xs text-gray-500">{new Date(event.timestamp).toLocaleString()}</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {event.from_party && <span>From: {event.from_party}</span>}
                        {event.to_party && <span className="ml-2">To: {event.to_party}</span>}
                        {event.seal_number && <span className="ml-2">Seal: {event.seal_number}</span>}
                        {event.volume_variance_pct !== null && event.volume_variance_pct !== undefined && (
                          <span className={classNames(
                            Math.abs(event.volume_variance_pct) > 2 ? 'text-danger-600 font-medium' : 'text-green-600',
                            'ml-2'
                          )}>
                            Volume: {event.volume_variance_pct > 0 ? '+' : ''}{event.volume_variance_pct.toFixed(1)}%
                          </span>
                        )}
                      </div>
                      {event.digital_signature && (
                        <p className="text-xs text-gray-400 mt-1 font-mono truncate">Sig: {event.digital_signature.slice(0, 24)}...</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No custody events recorded</p>
              )}
            </div>

            {/* Exceptions */}
            {shipmentDetail.exceptions && shipmentDetail.exceptions.length > 0 && (
              <div className="card p-5">
                <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 mr-2 text-orange-400" />
                  Exceptions ({shipmentDetail.exceptions.length})
                </h3>
                <div className="space-y-2">
                  {shipmentDetail.exceptions.map((exc: any) => (
                    <div key={exc.id} className="border rounded p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="text-sm font-medium text-gray-900 capitalize">{exc.exception_type?.replace('_', ' ')}</span>
                          <p className="text-xs text-gray-500 mt-1">{exc.description}</p>
                        </div>
                        <span className={classNames(
                          exc.severity === 'critical' ? 'bg-danger-100 text-danger-700' :
                          exc.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                          'bg-warning-100 text-warning-700',
                          'rounded-full px-2 py-0.5 text-xs font-medium capitalize'
                        )}>
                          {exc.severity}
                        </span>
                      </div>
                      {exc.ai_recommendation && (
                        <div className="mt-2 rounded bg-blue-50 p-2">
                          <p className="text-xs text-blue-700">
                            <span className="font-medium">AI Recommendation:</span> {exc.ai_recommendation}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
