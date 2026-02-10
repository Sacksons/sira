// ============================================================
// SIRA Platform - TypeScript Type Definitions
// ============================================================

// ------------------------------------------------------------
// Type Aliases
// ------------------------------------------------------------

export type ShipmentStatus =
  | 'draft'
  | 'booked'
  | 'loading'
  | 'in_transit'
  | 'at_anchorage'
  | 'discharging'
  | 'completed'
  | 'cancelled'
  | 'delayed'
  | 'exception'

export type VesselStatus =
  | 'active'
  | 'idle'
  | 'in_transit'
  | 'at_port'
  | 'at_anchorage'
  | 'under_maintenance'
  | 'laid_up'
  | 'decommissioned'

export type AssetStatus =
  | 'active'
  | 'idle'
  | 'in_transit'
  | 'maintenance'
  | 'decommissioned'
  | 'offline'

export type PortStatus =
  | 'operational'
  | 'congested'
  | 'restricted'
  | 'closed'
  | 'maintenance'

export type ExceptionSeverity =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical'

// ------------------------------------------------------------
// User types
// ------------------------------------------------------------

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  role: 'operator' | 'security_lead' | 'supervisor' | 'admin'
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
}

// ------------------------------------------------------------
// Auth types
// ------------------------------------------------------------

export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

// ------------------------------------------------------------
// Movement types
// ------------------------------------------------------------

export interface Movement {
  id: number
  cargo: string
  route: string
  assets?: string
  stakeholders?: string
  laycan_start: string
  laycan_end: string
  status: 'active' | 'completed' | 'cancelled' | 'delayed'
  current_location?: string
  current_lat?: number
  current_lng?: number
  risk_score: number
  created_at: string
  updated_at?: string
}

// ------------------------------------------------------------
// Event types
// ------------------------------------------------------------

export interface Event {
  id: number
  movement_id: number
  timestamp: string
  location?: string
  latitude?: number
  longitude?: number
  actor?: string
  event_type: 'planned' | 'actual' | 'security' | 'operational'
  severity: 'info' | 'warning' | 'critical'
  description?: string
  created_at: string
}

// ------------------------------------------------------------
// Alert types
// ------------------------------------------------------------

export type AlertSeverity = 'Critical' | 'High' | 'Medium' | 'Low'
export type AlertStatus = 'open' | 'acknowledged' | 'assigned' | 'investigating' | 'closed'

export interface Alert {
  id: number
  severity: AlertSeverity
  confidence: number
  sla_timer?: number
  sla_breached: boolean
  domain?: string
  site_zone?: string
  movement_id?: number
  event_id?: number
  status: AlertStatus
  case_id?: number
  description?: string
  rule_id?: string
  rule_name?: string
  assigned_to?: number
  acknowledged_at?: string
  resolved_at?: string
  created_at: string
  updated_at?: string
}

// ------------------------------------------------------------
// Case types
// ------------------------------------------------------------

export type CasePriority = 'low' | 'medium' | 'high' | 'critical'
export type CaseStatus = 'open' | 'investigating' | 'pending' | 'closed'

export interface Case {
  id: number
  case_number?: string
  title: string
  overview?: string
  status: CaseStatus
  priority: CasePriority
  category?: string
  costs: number
  assigned_to?: number
  created_by?: number
  created_at: string
  updated_at?: string
  closed_at?: string
}

// ------------------------------------------------------------
// Evidence types
// ------------------------------------------------------------

export interface Evidence {
  id: number
  case_id: number
  evidence_type: string
  file_ref: string
  original_filename?: string
  file_size?: number
  mime_type?: string
  verification_status: 'pending' | 'verified' | 'rejected'
  file_hash?: string
  uploaded_by?: number
  created_at: string
}

// ------------------------------------------------------------
// Playbook types
// ------------------------------------------------------------

export interface Playbook {
  id: number
  incident_type: string
  domain?: string
  title: string
  description?: string
  steps: string
  estimated_duration?: number
  is_active: boolean
  version: number
  created_at: string
}

// ------------------------------------------------------------
// Notification types
// ------------------------------------------------------------

export interface Notification {
  id: number
  user_id: number
  notification_type: string
  channel: string
  title: string
  message: string
  priority: string
  is_read: boolean
  read_at?: string
  created_at: string
}

// ------------------------------------------------------------
// Dashboard stats
// ------------------------------------------------------------

export interface DashboardStats {
  alerts: {
    total: number
    open: number
    critical: number
    today: number
    this_week: number
  }
  cases: {
    total: number
    open: number
    today: number
  }
  sla: {
    breached: number
    at_risk: number
  }
  recent_alerts: Array<{
    id: number
    severity: AlertSeverity
    description?: string
    status: AlertStatus
    created_at: string
  }>
  generated_at: string
}

// ------------------------------------------------------------
// Vessel types
// ------------------------------------------------------------

export interface Vessel {
  id: number
  name: string
  imo_number: string
  mmsi?: string
  vessel_type: string
  flag?: string
  dwt?: number
  loa?: number
  beam?: number
  draft?: number
  year_built?: number
  owner?: string
  operator?: string
  status: VesselStatus
  current_lat?: number
  current_lng?: number
  current_speed?: number
  current_heading?: number
  current_destination?: string
  position_updated_at?: string
  charter_type?: string
  charter_rate?: number
  charter_start?: string
  charter_end?: string
  created_at: string
  updated_at?: string
}

// ------------------------------------------------------------
// Port types
// ------------------------------------------------------------

export interface Port {
  id: number
  name: string
  code: string
  country: string
  region?: string
  latitude: number
  longitude: number
  port_type?: string
  max_draft?: number
  max_loa?: number
  anchorage_capacity?: number
  status: PortStatus
  current_queue: number
  avg_wait_days: number
  avg_dwell_days: number
  authority?: string
  timezone?: string
  created_at: string
}

// ------------------------------------------------------------
// Berth types
// ------------------------------------------------------------

export interface Berth {
  id: number
  port_id: number
  name: string
  berth_type?: string
  max_draft?: number
  max_loa?: number
  cargo_types?: string[]
  equipment?: string[]
  loading_rate?: number
  status: string
  created_at: string
}

// ------------------------------------------------------------
// Berth Booking types
// ------------------------------------------------------------

export interface BerthBooking {
  id: number
  berth_id: number
  vessel_id: number
  shipment_id?: number
  scheduled_arrival: string
  scheduled_departure: string
  actual_arrival?: string
  actual_departure?: string
  status: string
  cargo_type?: string
  cargo_volume?: number
  priority: number
  created_at: string
}

// ------------------------------------------------------------
// Asset types
// ------------------------------------------------------------

export interface Asset {
  id: number
  asset_code: string
  name: string
  asset_type: string
  sub_type?: string
  owner?: string
  operator?: string
  capacity?: number
  max_payload?: number
  status: AssetStatus
  current_location?: string
  current_lat?: number
  current_lng?: number
  current_speed?: number
  assigned_corridor_id?: number
  assigned_shipment_id?: number
  utilization_pct: number
  total_trips: number
  total_distance_km: number
  next_maintenance?: string
  maintenance_status: string
  iot_device_id?: string
  created_at: string
  updated_at?: string
}

// ------------------------------------------------------------
// Corridor types
// ------------------------------------------------------------

export interface Corridor {
  id: number
  name: string
  code: string
  corridor_type?: string
  country?: string
  region?: string
  description?: string
  origin_port_id?: number
  destination_port_id?: number
  waypoints?: Array<{ lat: number; lng: number; name?: string }>
  total_distance_km?: number
  modes?: string[]
  primary_commodity?: string
  annual_volume_mt?: number
  status: string
  avg_transit_days?: number
  avg_demurrage_days?: number
  avg_cost_per_tonne?: number
  created_at: string
}

// ------------------------------------------------------------
// Shipment types
// ------------------------------------------------------------

export interface Shipment {
  id: number
  shipment_ref: string
  corridor_id?: number
  vessel_id?: number
  cargo_type: string
  cargo_grade?: string
  volume_tonnes?: number
  bill_of_lading?: string
  origin: string
  destination: string
  origin_port_id?: number
  destination_port_id?: number
  laycan_start: string
  laycan_end: string
  status: ShipmentStatus
  current_leg?: string
  current_mode?: string
  eta_destination?: string
  eta_confidence?: number
  eta_updated_at?: string
  demurrage_risk_score: number
  demurrage_exposure_usd: number
  demurrage_days: number
  shipper?: string
  receiver?: string
  custody_seal_id?: string
  custody_status: string
  freight_cost?: number
  total_cost?: number
  loading_started?: string
  loading_completed?: string
  departed_origin?: string
  arrived_destination?: string
  discharge_started?: string
  discharge_completed?: string
  created_at: string
  updated_at?: string
}

// ------------------------------------------------------------
// Shipment Milestone types
// ------------------------------------------------------------

export interface ShipmentMilestone {
  id: number
  shipment_id: number
  milestone_type: string
  description?: string
  location?: string
  mode?: string
  planned_time?: string
  actual_time?: string
  variance_hours?: number
  status: string
  created_at: string
}

// ------------------------------------------------------------
// Custody Event types
// ------------------------------------------------------------

export interface CustodyEvent {
  id: number
  shipment_id: number
  event_type: string
  timestamp: string
  location?: string
  latitude?: number
  longitude?: number
  from_party?: string
  to_party?: string
  witnessed_by?: string
  seal_number?: string
  seal_status?: string
  measured_volume?: number
  expected_volume?: number
  volume_variance_pct?: number
  photo_ref?: string
  document_ref?: string
  digital_signature?: string
  blockchain_tx?: string
  notes?: string
  created_by?: number
  created_at: string
}

// ------------------------------------------------------------
// Shipment Document types
// ------------------------------------------------------------

export interface ShipmentDocument {
  id: number
  shipment_id: number
  document_type: string
  title: string
  file_ref?: string
  file_hash?: string
  status: string
  issued_by?: string
  issued_at?: string
  verified_by?: string
  verified_at?: string
  notes?: string
  created_at: string
}

// ------------------------------------------------------------
// Shipment Exception types
// ------------------------------------------------------------

export interface ShipmentException {
  id: number
  shipment_id: number
  exception_type: string
  severity: ExceptionSeverity
  description?: string
  impact_description?: string
  estimated_delay_hours?: number
  estimated_cost_usd?: number
  status: string
  resolution?: string
  resolved_at?: string
  ai_recommendation?: string
  ai_confidence?: number
  created_at: string
}

// ------------------------------------------------------------
// Freight Rate types
// ------------------------------------------------------------

export interface FreightRate {
  id: number
  corridor_id?: number
  lane: string
  mode: string
  cargo_type?: string
  rate_usd: number
  rate_unit: string
  currency: string
  rate_type?: string
  source?: string
  effective_date: string
  expiry_date?: string
  vessel_class?: string
  created_at: string
}

// ------------------------------------------------------------
// Market Index types
// ------------------------------------------------------------

export interface MarketIndex {
  id: number
  index_name: string
  index_type?: string
  value: number
  unit?: string
  change_pct?: number
  change_abs?: number
  period?: string
  source?: string
  recorded_at: string
  created_at: string
}

// ------------------------------------------------------------
// Demurrage Record types
// ------------------------------------------------------------

export interface DemurrageRecord {
  id: number
  shipment_id: number
  vessel_id?: number
  port_id?: number
  demurrage_days?: number
  demurrage_rate_usd?: number
  demurrage_amount_usd?: number
  status: string
  created_at: string
}

// ------------------------------------------------------------
// IoT Device types
// ------------------------------------------------------------

export interface IoTDevice {
  id: number
  device_id: string
  device_type: string
  manufacturer?: string
  model?: string
  status: string
  battery_level?: number
  last_seen?: string
  last_lat?: number
  last_lng?: number
  asset_id?: number
  vessel_id?: number
  created_at: string
}

// ------------------------------------------------------------
// Control Tower Overview types
// ------------------------------------------------------------

export interface ControlTowerOverview {
  shipments: {
    active: number
    high_risk: number
    total_demurrage_exposure_usd: number
    by_status: Record<string, number>
    by_mode: Record<string, number>
  }
  vessels: {
    active: number
    idle: number
    total: number
  }
  fleet: {
    total: number
    in_transit: number
    available: number
    maintenance: number
  }
  ports: {
    total: number
    congested: number
    operational: number
  }
  corridors: {
    active: number
  }
  exceptions: {
    open: number
    critical: number
    recent: ShipmentException[]
  }
}

// ------------------------------------------------------------
// Map Data types
// ------------------------------------------------------------

export interface MapData {
  vessels: Array<{
    id: number
    name: string
    imo_number: string
    vessel_type: string
    status: VesselStatus
    lat: number
    lng: number
    speed?: number
    heading?: number
    destination?: string
  }>
  assets: Array<{
    id: number
    asset_code: string
    name: string
    asset_type: string
    status: AssetStatus
    lat: number
    lng: number
    speed?: number
  }>
  ports: Array<{
    id: number
    name: string
    code: string
    country: string
    status: PortStatus
    lat: number
    lng: number
    current_queue: number
  }>
  corridors: Array<{
    id: number
    name: string
    code: string
    status: string
    waypoints: Array<{ lat: number; lng: number }>
    origin_port_id?: number
    destination_port_id?: number
  }>
}

// ------------------------------------------------------------
// API Response types
// ------------------------------------------------------------

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ApiError {
  detail: string
}
